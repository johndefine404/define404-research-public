"""003 Local404 데이터 노트: 같은 가게, 5개 언어 답의 일관성. 사전 등록 분석 (prereg.md 7절).

입력은 1편(001-local404)의 판정 결과 파일 하나다. 새 판정·새 수집·모델 호출은 하지 않는다.
  기본 입력: ../../001-local404/analysis/out_final/judgments.csv (읽기 전용)
  출력:      analysis/out/ (h1.csv, h2.csv, h3.csv, holm.csv, explore_*.csv, results.json)

실행:
  python analysis/run_analysis.py                      # 기본 입력·출력
  python analysis/run_analysis.py --judgments X --out Y # 가짜 입력 시험용

통계 도구는 1편 analysis/stats_lib.py 를 그대로 불러 쓴다(군집 로버스트 SE, 짝 차이, Wilson, Holm).
"""
import argparse
import datetime as dt
import hashlib
import itertools
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
EP = HERE.parent                                   # 003-local404-consistency/
LOCAL404 = EP.parent / "001-local404"              # 읽기 전용
sys.path.insert(0, str(LOCAL404 / "analysis"))
import stats_lib as S                              # noqa: E402

DEFAULT_JUDGMENTS = LOCAL404 / "analysis" / "out_final" / "judgments.csv"
LANGS = ["ko", "en", "ja", "zh", "vi"]
OTHERS = ["en", "ja", "zh", "vi"]
CLAUDE = ["H-mem", "H-search", "S-search"]
MIN_CELL_N = 40            # prereg 7절: 40 미만 칸은 해석하지 않는다
ALPHA = 0.05


def sha256(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


# ------------------------------------------------------------------ 적재
def load(path):
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    need = {"system", "qid", "item_id", "lang", "status", "address", "type", "truth", "kakao", "region"}
    miss = need - set(df.columns)
    if miss:
        sys.exit(f"judgments.csv 에 열이 없다: {sorted(miss)}")
    df = df[df.lang.isin(LANGS)].copy()
    # 언급 여부(0/1). na(정답이 기타라 판정 제외)·review(미확정)는 결측.
    def said(col):
        v = df[col]
        out = pd.Series(np.nan, index=df.index, dtype=float)
        out[v.isin(["match", "wrong"])] = 1.0
        out[v == "none"] = 0.0
        return out
    df["said_type"] = said("type")
    df["said_addr"] = said("address")
    df["type_match"] = np.where(df["type"] == "match", 1.0, np.where(df["type"] == "wrong", 0.0, np.nan))
    df["addr_match"] = np.where(df["address"] == "match", 1.0, np.where(df["address"] == "wrong", 0.0, np.nan))
    df["status_resolved"] = df["status"].isin(["open", "closed", "unknown"])
    return df


def wide(df, system, col):
    """가게 x 언어 표. 5개 언어가 모두 있는(결측 없는) 가게만 complete=True."""
    d = df[df.system == system].pivot_table(index="item_id", columns="lang", values=col, aggfunc="first")
    for lg in LANGS:
        if lg not in d.columns:
            d[lg] = np.nan
    d = d[LANGS]
    return d


def shop_attrs(df):
    return (df.drop_duplicates("item_id").set_index("item_id")[["truth", "kakao", "region"]])


def interp(n):
    return bool(n >= MIN_CELL_N)


# ------------------------------------------------------------------ 가설 검정
def ko_vs_others(df, system, col, label, confirmatory):
    """가게마다 d = said_ko - mean(said_en, ja, zh, vi). 5개 언어 완비 가게만. 짝 차이, 가게 군집 CI."""
    w = wide(df, system, col)
    n_all = len(w)
    c = w.dropna()
    n = len(c)
    rows = []
    if n == 0:
        rows.append({"hypothesis": label, "confirmatory": confirmatory, "system": system, "measure": col,
                     "comparison": "ko - mean(en,ja,zh,vi)", "n_shops": 0, "n_shops_dropped_incomplete": n_all,
                     "interpretable": False, "note": "no complete shops"})
        return rows, None
    d = c["ko"] - c[OTHERS].mean(axis=1)
    r = S.paired_cluster_diff(d.values, c.index.values, ALPHA)
    base = {"hypothesis": label, "confirmatory": confirmatory, "system": system, "measure": col,
            "n_shops": n, "n_shops_dropped_incomplete": n_all - n, "interpretable": interp(n)}
    rows.append({**base, "comparison": "ko - mean(en,ja,zh,vi)",
                 "rate_ko": float(c["ko"].mean()), "rate_others_mean": float(c[OTHERS].mean(axis=1).mean()),
                 "diff": r["est"], "se": r["se"], "ci_lo": r.get("ci_lo"), "ci_hi": r.get("ci_hi"),
                 "p_two": r.get("p_two"), "p_greater": r.get("p_greater"), "note": r.get("note", "")})
    # 언어별 짝 차이(기술 통계, 검정 가족에 넣지 않음)
    for lg in OTHERS:
        dd = c["ko"] - c[lg]
        rr = S.paired_cluster_diff(dd.values, c.index.values, ALPHA)
        rows.append({**base, "confirmatory": False, "comparison": f"ko - {lg}",
                     "rate_ko": float(c["ko"].mean()), "rate_others_mean": float(c[lg].mean()),
                     "diff": rr["est"], "se": rr["se"], "ci_lo": rr.get("ci_lo"), "ci_hi": rr.get("ci_hi"),
                     "p_two": rr.get("p_two"), "p_greater": rr.get("p_greater"), "note": rr.get("note", "")})
    return rows, rows[0]


def inconsistent_flag(w):
    """5개 언어 언급 여부가 모두 같지 않으면 1. 완비 가게만."""
    c = w.dropna()
    s = c.sum(axis=1)
    return pd.Series(((s > 0) & (s < len(LANGS))).astype(float), index=c.index)


def h3_kakao(df, system, col):
    """언급 불일치 가게 비율: 카카오 등록 대 비등록. 독립 두 군(가게 단위), 방향 등록 > 비등록."""
    w = wide(df, system, col)
    f = inconsistent_flag(w)
    at = shop_attrs(df).reindex(f.index)
    a = f[at.kakao == "registered"]
    b = f[at.kakao == "unregistered"]
    r = S.diff_independent(a.values, a.index.values, b.values, b.index.values, ALPHA)
    return {"hypothesis": "H3", "confirmatory": True, "system": system, "measure": col,
            "comparison": "inconsistent(kakao registered) - inconsistent(unregistered)",
            "n_registered": int(len(a)), "n_unregistered": int(len(b)),
            "rate_registered": r["mean_a"], "rate_unregistered": r["mean_b"],
            "diff": r["est"], "se": r["se"], "ci_lo": r.get("ci_lo"), "ci_hi": r.get("ci_hi"),
            "p_two": r.get("p_two"), "p_greater": r.get("p_greater"),
            "interpretable": interp(min(len(a), len(b))), "note": r.get("note", "")}


# ------------------------------------------------------------------ 탐색
def explore_pairs(df, systems, col):
    """언어 쌍 10개별 언급 불일치율(두 언어가 모두 있는 가게 기준) + Wilson CI."""
    rows = []
    for sy in systems:
        w = wide(df, sy, col)
        for a, b in itertools.combinations(LANGS, 2):
            c = w[[a, b]].dropna()
            n = len(c)
            k = int((c[a] != c[b]).sum())
            lo, hi = S.wilson(k, n, ALPHA)
            # 갈릴 때 어느 쪽이 말했나
            a_only = int(((c[a] == 1) & (c[b] == 0)).sum())
            b_only = int(((c[a] == 0) & (c[b] == 1)).sum())
            rows.append({"system": sy, "measure": col, "lang_a": a, "lang_b": b, "n_shops": n,
                         "n_disagree": k, "prop_disagree": (k / n if n else float("nan")),
                         "wilson_lo": lo, "wilson_hi": hi, "a_said_only": a_only, "b_said_only": b_only,
                         "interpretable": interp(n), "confirmatory": False})
    return rows


def explore_inconsistency(df, systems, col):
    """시스템별 5개 언어 언급 불일치 가게 비율(완비 가게) + 속성별(영업상태·카카오·지역)."""
    rows = []
    at = shop_attrs(df)
    for sy in systems:
        w = wide(df, sy, col)
        f = inconsistent_flag(w)
        groups = [("all", f)]
        a2 = at.reindex(f.index)
        for key in ["truth", "kakao", "region"]:
            for val in sorted(a2[key].dropna().unique()):
                groups.append((f"{key}={val}", f[a2[key] == val]))
        for name, g in groups:
            n, k = len(g), int(g.sum())
            lo, hi = S.wilson(k, n, ALPHA)
            rows.append({"system": sy, "measure": col, "group": name, "n_shops": n, "n_inconsistent": k,
                         "prop_inconsistent": (k / n if n else float("nan")), "wilson_lo": lo, "wilson_hi": hi,
                         "interpretable": interp(n), "confirmatory": False})
    return rows


def explore_correctness(df, systems, said_col, match_col):
    """갈릴 때 어느 쪽이 맞나. (1) 언어별로, 말한 답 중 맞은 비율(답 단위, 가게 군집 CI).
    (2) 둘 이상 언어가 말한 가게 중 판정(맞음/틀림)이 언어 간 갈린 가게 비율.
    (3) 한 언어는 맞고 다른 언어는 틀린 쌍에서 언어별로 맞은 쪽이 된 횟수."""
    rows = []
    for sy in systems:
        d = df[(df.system == sy)]
        for lg in LANGS:
            x = d[(d.lang == lg) & d[match_col].notna()]
            r = S.mean_with_ci(x[match_col].values, x.item_id.values, ALPHA) if len(x) else None
            rows.append({"system": sy, "kind": "match_rate_among_said", "lang": lg,
                         "n_answers": int(len(x)), "n_shops": int(x.item_id.nunique()),
                         "value": (r["mean"] if r else float("nan")),
                         "ci_lo": (r["ci_lo"] if r else float("nan")), "ci_hi": (r["ci_hi"] if r else float("nan")),
                         "interpretable": interp(len(x)), "confirmatory": False})
        wm = wide(df, sy, match_col)
        multi = wm[wm.notna().sum(axis=1) >= 2]
        n = len(multi)
        k = int(((multi.max(axis=1) == 1) & (multi.min(axis=1) == 0)).sum())
        lo, hi = S.wilson(k, n, ALPHA)
        rows.append({"system": sy, "kind": "judgment_disagree_among_multi_said", "lang": "all",
                     "n_answers": int(multi.notna().sum().sum()), "n_shops": n, "value": (k / n if n else float("nan")),
                     "ci_lo": lo, "ci_hi": hi, "interpretable": interp(n), "confirmatory": False})
        # 쌍 단위: 한쪽 맞음·한쪽 틀림일 때 맞은 쪽 언어 집계
        wins = {lg: 0 for lg in LANGS}
        losses = {lg: 0 for lg in LANGS}
        for a, b in itertools.combinations(LANGS, 2):
            c = wm[[a, b]].dropna()
            wins[a] += int(((c[a] == 1) & (c[b] == 0)).sum()); losses[b] += int(((c[a] == 1) & (c[b] == 0)).sum())
            wins[b] += int(((c[b] == 1) & (c[a] == 0)).sum()); losses[a] += int(((c[b] == 1) & (c[a] == 0)).sum())
        for lg in LANGS:
            tot = wins[lg] + losses[lg]
            rows.append({"system": sy, "kind": "pairwise_right_when_split", "lang": lg,
                         "n_answers": tot, "n_shops": float("nan"), "value": (wins[lg] / tot if tot else float("nan")),
                         "ci_lo": S.wilson(wins[lg], tot, ALPHA)[0] if tot else float("nan"),
                         "ci_hi": S.wilson(wins[lg], tot, ALPHA)[1] if tot else float("nan"),
                         "interpretable": interp(tot), "confirmatory": False})
    return rows


def explore_lmem_status(df):
    """L-mem: 한국어·영어·일본어 세 언어 영업 상태 판정이 모두 확정된 가게에서 판정이 서로 다른 가게 비율.
    1편 H5는 5개 언어 완비 가게가 없어 검정 불가였다. 3개 언어 기준은 새 기술 통계(탐색)."""
    d = df[(df.system == "L-mem") & df.status_resolved]
    w = d.pivot_table(index="item_id", columns="lang", values="status", aggfunc="first")
    langs3 = [lg for lg in ["ko", "en", "ja"] if lg in w.columns]
    rows = []
    if len(langs3) < 2:
        return [{"system": "L-mem", "langs": ",".join(langs3), "n_shops": 0, "note": "fewer than 2 languages", "confirmatory": False}]
    c = w[langs3].dropna()
    n = len(c)
    k = int((c.nunique(axis=1) > 1).sum())
    conflict = int(((c == "open").any(axis=1) & (c == "closed").any(axis=1)).sum())
    lo, hi = S.wilson(k, n, ALPHA)
    rows.append({"system": "L-mem", "langs": ",".join(langs3), "n_shops": n, "n_inconsistent": k,
                 "prop_inconsistent": (k / n if n else float("nan")), "wilson_lo": lo, "wilson_hi": hi,
                 "n_open_vs_closed_conflict": conflict, "interpretable": interp(n), "confirmatory": False})
    return rows


# ------------------------------------------------------------------ 실행
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--judgments", default=str(DEFAULT_JUDGMENTS))
    ap.add_argument("--out", default=str(HERE / "out"))
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    df = load(a.judgments)

    # 1차 H1: H-mem 업종 언급, 한국어 대 나머지 4개 언어 평균
    h1_rows, h1 = ko_vs_others(df, "H-mem", "said_type", "H1", True)
    # 2차 H2: 검색 2조건에서 같은 비교 (H2a S-search, H2b H-search)
    h2_rows, h2 = [], []
    for lab, sy in [("H2a", "S-search"), ("H2b", "H-search")]:
        r, main_row = ko_vs_others(df, sy, "said_type", lab, True)
        h2_rows += r
        h2.append(main_row)
    # 2차 H3: H-mem 업종 언급 불일치, 카카오 등록 대 비등록
    h3 = h3_kakao(df, "H-mem", "said_type")

    # Holm: 확증 검정 4개(H1, H2a, H2b, H3)를 한 가족으로. 40 미만 칸·p 미정의는 가족에서 뺀다.
    fam = [r for r in [h1] + h2 + [h3] if r is not None]
    pv = [r["p_two"] if (r.get("interpretable") and r.get("p_two") is not None and not (isinstance(r["p_two"], float) and math.isnan(r["p_two"]))) else float("nan") for r in fam]
    adj = S.holm(pv)
    holm_rows = []
    for r, p0, p1 in zip(fam, pv, adj):
        holm_rows.append({"hypothesis": r["hypothesis"], "system": r["system"], "comparison": r["comparison"],
                          "diff": r.get("diff"), "ci_lo": r.get("ci_lo"), "ci_hi": r.get("ci_hi"),
                          "p_two": p0, "holm_p_two": p1, "p_greater_onesided": r.get("p_greater"),
                          "in_family": not (isinstance(p0, float) and math.isnan(p0)),
                          "supported(holm_p<0.05 and diff>0)": bool((not (isinstance(p1, float) and math.isnan(p1))) and p1 < ALPHA and (r.get("diff") or 0) > 0),
                          "interpretable": r.get("interpretable"), "note": r.get("note", "")})

    # 탐색(사전 명시, 검정 가족 밖)
    ex_pairs = explore_pairs(df, CLAUDE, "said_type")
    ex_incons = explore_inconsistency(df, CLAUDE, "said_type")
    ex_corr = explore_correctness(df, CLAUDE, "said_type", "type_match")
    ex_addr = (ko_vs_others(df, "H-mem", "said_addr", "E-addr", False)[0]
               + explore_pairs(df, CLAUDE, "said_addr") + explore_inconsistency(df, CLAUDE, "said_addr")
               + explore_correctness(df, CLAUDE, "said_addr", "addr_match"))
    ex_lmem = explore_lmem_status(df)

    def w(name, rows):
        pd.DataFrame(rows).to_csv(out / name, index=False, encoding="utf-8")
    w("h1.csv", h1_rows); w("h2.csv", h2_rows); w("h3.csv", [h3]); w("holm.csv", holm_rows)
    w("explore_pairs.csv", ex_pairs); w("explore_inconsistency.csv", ex_incons)
    w("explore_correctness.csv", ex_corr); w("explore_address.csv", ex_addr); w("explore_lmem_status.csv", ex_lmem)

    inv = []
    for sy in sorted(df.system.unique()):
        d = df[df.system == sy]
        inv.append({"system": sy, "n_answers": int(len(d)), "n_shops": int(d.item_id.nunique()),
                    "type_na_excluded(truth=기타)": int((d["type"] == "na").sum()),
                    "type_review_unresolved": int((d["type"] == "review").sum()),
                    "address_review_unresolved": int((d["address"] == "review").sum()),
                    "shops_complete_5lang_said_type": int(wide(df, sy, "said_type").dropna().shape[0])})
    w("data_inventory.csv", inv)
    res = {"episode": "003-local404-consistency", "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
           "inputs": {"judgments_csv": str(a.judgments), "judgments_sha256": sha256(a.judgments),
                      "stats_lib": str(LOCAL404 / "analysis" / "stats_lib.py"),
                      "stats_lib_sha256": sha256(LOCAL404 / "analysis" / "stats_lib.py")},
           "min_cell_n": MIN_CELL_N, "alpha": ALPHA, "holm_family": [r["hypothesis"] for r in fam],
           "confirmatory": {"H1": h1, "H2": h2, "H3": h3, "holm": holm_rows},
           "inventory": inv,
           "versions": {"python": sys.version.split()[0], "numpy": np.__version__, "pandas": pd.__version__}}
    (out / "results.json").write_text(json.dumps(res, ensure_ascii=False, indent=2, default=float), encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
