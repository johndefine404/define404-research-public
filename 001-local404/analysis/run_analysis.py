"""사전 등록(prereg.md) 분석 파이프라인 진입점.

  python analysis/run_analysis.py --dryrun          # 지금 있는 데이터로 시험 실행 -> analysis/out_dryrun/
  python analysis/run_analysis.py --dryrun --dict-only [--only-qids-from analysis/out_dryrun/judgments.csv]
                                                    # 사전(표현 사전) 판정 단독 -> analysis/out_dictonly/ (LLM 라벨 미사용, 미해결은 review=미판정. prereg 8절 원 규칙 결과)
  python analysis/run_analysis.py --final --rater-b # 수집 완료 뒤. 독립 LLM 판정자 B 일치도 포함(사람 판정 대체). 시스템별 유효 답이 다 차지 않으면 거부 -> analysis/out_final/

모델·검색·네트워크를 호출하지 않는다. collect/, sampling/, judge/, prereg 는 읽기만 한다.
"""
import argparse
import datetime as dt
import hashlib
import json
import math
import platform
import sys
from pathlib import Path

import numpy as np
import pandas as pd

import config as C
import load_data as L
import auto_judge as J
import human_sample as HS
import stats_lib as S

AMBIGUITIES = [
    "A1 검색 조건 유효 기준: HANDOFF 3절은 searches==0 만 무효. 실제로는 searches==1 인데 본문이 검색 한도 소진·미실행이라고 말하는 답이 많다. 기본(strict)은 그런 답도 무효로 보고 결측 처리. --search-validity searches_only 로 HANDOFF 기준 그대로 돌릴 수 있다.",
    "A2 W-mem(prereg 4번째 시스템) 대신 L-mem(같은 모델 로컬 Ollama)을 4번째 확증 시스템으로 분석. 경로 변경은 HANDOFF 7절 1번 사항. Workers AI(W-mem) 답은 탐색 전용이라 확증 분석에서 제외.",
    "A3 비율의 분모: H1·정확도는 '모름'을 포함한 해당 칸 전체 답을 분모로 한다(prereg 문구 '폐업 가게 중'). 단정한 답만 분모로 한 값은 탐색 열로 따로 낸다.",
    "A4 정답률(H2·종합 모형): 영업 상태 판정이 정답과 같으면 1, 틀림 또는 모름이면 0 (rules.md 1절은 모름을 별도 범주로 두므로 이 합산은 해석 선택). 기본 점수는 느슨한 판정, 엄격한 판정은 병행 표.",
    "A5 H3 '오류율' = 틀림(단정이 정답과 다름) 비율, 모름은 오류가 아님. 분모는 짝을 이룬 전체 답. 짝 = (가게, 언어), 군집 = 가게.",
    "A6 H1·H2·H3·H4 검정 방향: 양측 p 를 Holm 입력으로 쓰고(보수적), 사전 등록 방향의 단측 p 도 병기. prereg 는 어느 쪽인지 안 적음.",
    "A7 Holm 보정의 가족: H1~H5 를 하나로 묶으면 H1·H2·H4 는 시스템/언어별 다수 검정이라 가족 정의가 필요. 기본은 '확증 검정 전체(유의 해석 가능한 칸만)'을 한 가족으로, 가설별 가족도 병기.",
    "A8 H5: '5개 언어 판정이 모두 같지 않다' 의 판정 값에 '모름'을 별개 값으로 넣음(3값). 단정한 답끼리의 충돌(영업 대 폐업)은 탐색 열. 귀무가설 비율이 0 이라 p 값을 정의할 수 없어 H5 는 신뢰구간(하한>0)로만 판단하고 Holm 입력에서 뺀다.",
    "A9 H4 폐업 뒤 일수 = 측정일(2026-10-21) - 폐업일자, log 는 자연로그. 모형은 가게 임의절편 로지스틱을 직접 구현(Gauss-Hermite ML). 단정 '영업 중' 사건이 거의 없으면 추정 불가로 표시.",
    "A10 종합 모형 기준 범주: 언어 ko, 영업상태 영업, 카카오 등록 있음, 지역 광역, 시스템 H-mem. 모든 시스템·언어 답을 한 모형에 넣음.",
    "A11 사람 200답 표본: '무작위 200답'의 모집단(전체 유효 답, 시스템 비층화)과 평가 방식(평가자는 답이 말한 것만 적고 정답 대조는 코드)은 prereg 에 없음. 확정 표본은 수집 완료 뒤에 다시 뽑아야 함.",
    "A12 judge/rules.md 5절은 판정 코드를 judge/auto_judge.py 로 적었으나 judge/ 는 수정 금지 대상이라 analysis/auto_judge.py 로 둠. 다국어 사전은 사전 등록 이후 작성됨 -> 사람 표본 일치율 보고 필요. 사전으로 확정 못 하는 답은 review 로 남기고 LLM 보조 분류(미실행)나 사람 판정을 기다린다.",
    "A13 업태 대응: 표본 파일의 '패밀리레스트랑'(철자)을 rules.md 의 '패밀리레스토랑'과 같은 양식으로 취급. '식육(숯불구이)' 등 rules.md 대응표에 없는 업태는 '기타'(업종 판정 제외).",
    "A14 표본 40 미만 칸: interpretable=False 로 표시하고 Holm 에서 제외. '칸'은 시스템 x (언어 | 영업상태 | 짝 수) 단위.",
    "A15 미해결(review) 답은 모든 분석에서 제외하고 개수를 보고. 최종 분석 전에 review 가 0 이어야 한다(LLM 보조 분류 또는 사람 판정으로 해소).",
    "A16 검색 2조건 부표본(결과 분석 전 결정, 2026-10-24): H-search·S-search 는 층화 무작위 100곳 x 5언어(500문항, 시드 20261024, sampling/subsample_search_v1.csv)만 분석한다. 검색 대 기억 짝 비교(H3)는 같은 100곳에서 H-mem 과 짝짓는다. H-mem·L-mem 단독 분석은 800곳 전부. 검색 조건 H4(폐업 가게만)는 약 50곳이라 검정력이 낮다. 종합 모형은 시스템마다 가게 구성이 달라(검색 100곳, 기억 800곳) 해석에 주의한다.",
    "A17 언어 이탈 답(질문 언어가 아닌 문자 체계)은 strict 에서 검색 조건 답을 무효로 본다(load_data.script_ok, 보수적 기준). 기억 조건은 집계만 하고 제외하지 않는다(H-mem_ja_001 200답이 한글: 처리 방침 결정 대기).",
    "A18 LLM 보조 판정(analysis/llm_judge/): 판정자는 질문·답만 보고 단정한 것(status/address/type)을 적고, 정답 대조는 코드가 한다. 사전이 review 로 남긴 항목에만 LLM 라벨을 쓰고, 사전이 확정한 항목과의 일치(카파)는 llm_dictionary_agreement.csv 로 보고한다. rules.md 가 모호한 곳: 시·군·구만 되풀이한 주소의 처리, 외국어로 쓴 주소의 한글 환산, 업종 8묶음 밖 표현, 다른 가게를 소개하며 대상 가게 결론이 없을 때."
]


# ------------------------------------------------------------------------------ 사전 대 LLM 일치
def llm_agreement(answers, store_by_id, llm, out):
    """사전이 확정한(review 아닌) 라벨 대 LLM 라벨의 일치율·카파. LLM 은 질문·답만 보고 '답이 단정한 것'을 적었고(정답·시스템 모름),
    주소·업종은 정답과 대조해 사전과 같은 범주(match/none/wrong)로 바꿔 비교한다. 겹치는 항목만. 불일치 목록은 llm_dictionary_disagreements.csv."""
    if not llm:
        return None
    base = J.judge_all(answers, store_by_id, {})           # 사전만
    rows, dis = [], []
    by_key = {(a["system"], a["qid"]): a for a in answers}
    pairs = {f: {"all": ([], [])} for f in ("status", "address", "type")}
    for r in base:
        lab = llm.get(f'{r["system"]}|{r["qid"]}')
        if not lab:
            continue
        a = by_key[(r["system"], r["qid"])]
        if lab.get("answer_sha1") and lab["answer_sha1"] != hashlib.sha1(a["answer"].encode("utf-8")).hexdigest():
            continue
        st = store_by_id[r["item_id"]]
        derived = {"status": lab["status"],
                   "address": "na" if not st["address"] else J._addr_from_stated(lab.get("stated_address"), st["address"]),
                   "type": ("na" if J.truth_bundle(st["biz_type"]) == "기타" else
                            ("none" if not lab.get("stated_type") else ("match" if lab["stated_type"] == J.truth_bundle(st["biz_type"]) else "wrong")))}
        for f in ("status", "address", "type"):
            d = r[f]
            if d in ("review", "na") or derived[f] == "na":
                continue
            for grp in ("all", r["system"]):
                pairs[f].setdefault(grp, ([], []))
                pairs[f][grp][0].append(d); pairs[f][grp][1].append(derived[f])
            if d != derived[f]:
                dis.append({"system": r["system"], "qid": r["qid"], "field": f, "dictionary": d, "llm": derived[f]})
    for f, grps in pairs.items():
        for grp, (x, y) in grps.items():
            if x:
                k = HS.kappa_with_ci(x, y)
                rows.append({"field": f, "group": grp, **{kk: r4(v) if isinstance(v, float) else v for kk, v in k.items()}})
    if rows:
        write_csv(pd.DataFrame(rows), out / "llm_dictionary_agreement.csv")
    write_csv(pd.DataFrame(dis, columns=["system", "qid", "field", "dictionary", "llm"]), out / "llm_dictionary_disagreements.csv")
    return rows


# ------------------------------------------------------------------------------ 데이터 프레임
def build_frame(judged, store):
    sdf = pd.DataFrame(store)[["item_id", "truth", "kakao", "region", "days_since_close"]]
    df = pd.DataFrame([{k: v for k, v in r.items() if k != "_answer"} for r in judged])
    df = df.merge(sdf, on="item_id", how="left")
    df["resolved"] = df["status"].isin(["open", "closed", "unknown"])
    df["acc"] = np.where(df["resolved"], (df["status"] == df["truth"]).astype(float), np.nan)
    df["wrong"] = np.where(df["resolved"], (df["status"].isin(["open", "closed"]) & (df["status"] != df["truth"])).astype(float), np.nan)
    df["says_open"] = np.where(df["resolved"], (df["status"] == "open").astype(float), np.nan)
    df["says_closed"] = np.where(df["resolved"], (df["status"] == "closed").astype(float), np.nan)
    df["acc_strict"] = np.where(df["correct_strict"].isna(), np.nan, df["correct_strict"].astype(float))
    # 엄격 점수: 영업 상태가 틀렸거나 모름이면 0, 맞았는데 주소·업종 review 면 결측
    strict = np.full(len(df), np.nan)
    for i, (st, tr, cs) in enumerate(zip(df["status"], df["truth"], df["correct_strict"])):
        if st in ("unknown",) or (st in ("open", "closed") and st != tr):
            strict[i] = 0.0
        elif st in ("open", "closed") and cs is not None and not (isinstance(cs, float) and math.isnan(cs)):
            strict[i] = float(cs)
    df["acc_strict"] = strict
    return df


def ok(n):
    return bool(n >= C.MIN_CELL_N)


def r4(x):
    return None if x is None or (isinstance(x, float) and math.isnan(x)) else round(float(x), 6)


# ------------------------------------------------------------------------------ 기술 통계
def tbl_status_distribution(df):
    rows = []
    for (s, tr, lg), g in df.groupby(["system", "truth", "lang"]):
        n = len(g)
        c = g["status"].value_counts()
        rows.append({"system": s, "truth": tr, "lang": lg, "n": n, "open": int(c.get("open", 0)), "closed": int(c.get("closed", 0)),
                     "unknown": int(c.get("unknown", 0)), "review_unresolved": int(c.get("review", 0)),
                     "interpretable": ok(n)})
    return pd.DataFrame(rows)


def tbl_accuracy(df):
    rows = []
    for (s, lg), g in df[df.resolved].groupby(["system", "lang"]):
        a = S.mean_with_ci(g["acc"], g["item_id"])
        w = S.mean_with_ci(g["wrong"], g["item_id"])
        u = S.mean_with_ci((g["status"] == "unknown").astype(float), g["item_id"])
        gs = g[g["acc_strict"].notna()]
        st = S.mean_with_ci(gs["acc_strict"], gs["item_id"]) if len(gs) else {"mean": float("nan"), "ci_lo": float("nan"), "ci_hi": float("nan"), "n": 0}
        rows.append({"system": s, "lang": lg, "n": a["n"], "stores": a["g"],
                     "acc_lenient": a["mean"], "acc_lenient_lo": a["ci_lo"], "acc_lenient_hi": a["ci_hi"],
                     "error_rate": w["mean"], "error_lo": w["ci_lo"], "error_hi": w["ci_hi"],
                     "unknown_rate": u["mean"], "unknown_lo": u["ci_lo"], "unknown_hi": u["ci_hi"],
                     "acc_strict": st["mean"], "acc_strict_lo": st["ci_lo"], "acc_strict_hi": st["ci_hi"], "n_strict_determinable": st["n"],
                     "interpretable": ok(a["n"])})
    return pd.DataFrame(rows)


# ------------------------------------------------------------------------------ 탐색 요약 (확증 아님)
def tbl_exploratory(df):
    """시스템 x (전체 | 언어 | 정답 영업상태) 별 영업 상태 분포, 주소·업종 언급률과 언급했을 때 정확도. 모두 탐색.
    비율은 Wilson 95% CI (가게 군집 무시: 단순 이항, 기술용). L-mem 은 수집 중이라 부분 자료(partial)로 표시."""
    rows = []
    systems = [s for s in C.SYSTEMS if (df.system == s).any()]
    for s in systems:
        d0 = df[df.system == s]
        scopes = [("all", "all", d0)]
        scopes += [("lang", lg, g) for lg, g in d0.groupby("lang")]
        scopes += [("truth", tr, g) for tr, g in d0.groupby("truth")]
        for scope, val, g in scopes:
            n = len(g)
            row = {"system": s, "scope": scope, "value": val, "n": n, "stores": g["item_id"].nunique(),
                   "partial_data": s == "L-mem", "interpretable": ok(n)}
            for k in ("open", "closed", "unknown", "review"):
                c = int((g["status"] == k).sum())
                lo, hi = S.wilson(c, n) if n else (float("nan"), float("nan"))
                row.update({k: c, f"{k}_pct": c / n if n else float("nan"), f"{k}_lo": lo, f"{k}_hi": hi})
            for fld in ("address", "type"):
                asserted = g[g[fld].isin(["match", "wrong"])]
                na = len(asserted)
                m = int((asserted[fld] == "match").sum())
                lo, hi = S.wilson(na, n) if n else (float("nan"), float("nan"))
                alo, ahi = S.wilson(m, na) if na else (float("nan"), float("nan"))
                row.update({f"{fld}_asserted": na, f"{fld}_asserted_pct": na / n if n else float("nan"),
                            f"{fld}_asserted_lo": lo, f"{fld}_asserted_hi": hi,
                            f"{fld}_correct_given_asserted": m, f"{fld}_acc_given_asserted": m / na if na else float("nan"),
                            f"{fld}_acc_lo": alo, f"{fld}_acc_hi": ahi})
            rows.append(row)
    return pd.DataFrame(rows)


# ------------------------------------------------------------------------------ H1
def tbl_h1(df, systems):
    rows = []
    for s in systems:
        d = df[(df.system == s) & df.resolved]
        cl, op = d[d.truth == "closed"], d[d.truth == "open"]
        for variant, (a_, b_) in {"all_answers": (cl, op),
                                  "committed_only(exploratory)": (cl[cl.status != "unknown"], op[op.status != "unknown"])}.items():
            r = S.diff_independent(a_["says_open"], a_["item_id"], b_["says_closed"], b_["item_id"])
            ciA = S.mean_with_ci(a_["says_open"], a_["item_id"]); ciB = S.mean_with_ci(b_["says_closed"], b_["item_id"])
            n_min = min(r["n_a"], r["n_b"])
            rows.append({"hypothesis": "H1", "confirmatory": variant == "all_answers", "variant": variant, "system": s,
                         "n_closed": r["n_a"], "stores_closed": r["g_a"], "p_says_open_given_closed": r["mean_a"], "ci_a_lo": ciA["ci_lo"], "ci_a_hi": ciA["ci_hi"],
                         "n_open": r["n_b"], "stores_open": r["g_b"], "p_says_closed_given_open": r["mean_b"], "ci_b_lo": ciB["ci_lo"], "ci_b_hi": ciB["ci_hi"],
                         "diff_A_minus_B": r["est"], "se": r["se"], "ci_lo": r["ci_lo"], "ci_hi": r["ci_hi"], "z": r["z"],
                         "p_two": r["p_two"], "p_directional(A>B)": r["p_greater"], "interpretable": ok(n_min),
                         "note": r.get("note", "")})
    return pd.DataFrame(rows)


# ------------------------------------------------------------------------------ H2
def tbl_h2(df, systems):
    rows = []
    for s in systems:
        d = df[(df.system == s) & df.resolved]
        for score, col in (("lenient", "acc"), ("strict", "acc_strict")):
            wide = d.pivot_table(index="item_id", columns="lang", values=col, aggfunc="first")
            for lg in [x for x in C.LANGS if x != "ko"]:
                if "ko" not in wide or lg not in wide:
                    pairs = pd.Series(dtype=float)
                else:
                    sub = wide[["ko", lg]].dropna()
                    pairs = sub[lg] - sub["ko"]
                    acc_ko, acc_l = sub["ko"].mean() if len(sub) else float("nan"), sub[lg].mean() if len(sub) else float("nan")
                r = S.paired_cluster_diff(pairs.values, pairs.index.values)
                rows.append({"hypothesis": "H2", "confirmatory": score == "lenient", "score": score, "system": s, "lang": lg,
                             "n_pairs": len(pairs), "acc_ko_paired": acc_ko if len(pairs) else float("nan"), "acc_lang_paired": acc_l if len(pairs) else float("nan"),
                             "diff_lang_minus_ko": r["est"] if len(pairs) else float("nan"), "se": r["se"] if len(pairs) else float("nan"),
                             "ci_lo": r["ci_lo"] if len(pairs) else float("nan"), "ci_hi": r["ci_hi"] if len(pairs) else float("nan"),
                             "p_two": r["p_two"] if len(pairs) else float("nan"), "p_directional(lang<ko)": r["p_less"] if len(pairs) else float("nan"),
                             "interpretable": ok(len(pairs)), "note": r.get("note", "") if len(pairs) else "no pairs"})
    return pd.DataFrame(rows)


# ------------------------------------------------------------------------------ H3
def tbl_h3(df):
    # 검색 쪽은 부표본 100곳뿐이고(load_data 가 제한), 기억 쪽도 같은 가게로 맞춘다(A16). 짝 조인이 이미 그렇게 되지만 명시해 둔다.
    sub = L.subsample_ids()
    a = df[(df.system == "H-search") & df.resolved & df.item_id.isin(sub)][["item_id", "lang", "wrong"]].rename(columns={"wrong": "w_search"})
    b = df[(df.system == "H-mem") & df.resolved & df.item_id.isin(sub)][["item_id", "lang", "wrong"]].rename(columns={"wrong": "w_mem"})
    m = a.merge(b, on=["item_id", "lang"], how="inner")
    m["d"] = m["w_search"] - m["w_mem"]
    rows = []
    for lg, g in [("all", m)] + [(x, m[m.lang == x]) for x in C.LANGS]:
        r = S.paired_cluster_diff(g["d"].values, g["item_id"].values) if len(g) else {"est": float("nan"), "se": float("nan"), "ci_lo": float("nan"), "ci_hi": float("nan"), "p_two": float("nan"), "p_less": float("nan")}
        rows.append({"hypothesis": "H3", "confirmatory": lg == "all", "lang": lg, "n_pairs": len(g), "stores": g["item_id"].nunique(),
                     "error_search": g["w_search"].mean() if len(g) else float("nan"), "error_mem": g["w_mem"].mean() if len(g) else float("nan"),
                     "diff_search_minus_mem": r["est"], "se": r["se"], "ci_lo": r["ci_lo"], "ci_hi": r["ci_hi"],
                     "p_two": r["p_two"], "p_directional(search<mem)": r["p_less"], "interpretable": ok(len(g)),
                     "note": r.get("note", "")})
    return pd.DataFrame(rows)


# ------------------------------------------------------------------------------ H4
def tbl_h4(df, systems):
    rows = []
    for s in systems:
        d = df[(df.system == s) & df.resolved & (df.truth == "closed") & df.days_since_close.notna()].copy()
        d["logdays"] = np.log(d["days_since_close"].clip(lower=1).astype(float))
        n, ev = len(d), int(d["says_open"].sum())
        base = {"hypothesis": "H4", "confirmatory": True, "system": s, "n": n, "stores": d["item_id"].nunique(), "events_says_open": ev,
                "interpretable": ok(n)}
        if n == 0:
            rows.append({**base, "note": "no rows"}); continue
        mu = d["logdays"].mean()
        X = np.column_stack([np.ones(n), d["logdays"].values - mu])
        r = S.fit_glmm_logit(X, d["says_open"].values, d["item_id"].values, ["Intercept", "log_days_centered"])
        if not r.ok:
            rows.append({**base, "note": "not estimable: " + r.note}); continue
        t = r.table()[1]
        rows.append({**base, "coef_log_days": t["coef"], "se": t["se"], "odds_ratio_per_logday": t["odds_ratio"],
                     "or_ci_lo": t["or_ci_lo"], "or_ci_hi": t["or_ci_hi"], "p_two": t["p_two"], "p_directional(slope<0)": t["p_less"],
                     "sigma_store": r.sigma, "converged": r.converged, "note": r.note + (" few events (<10)" if ev < 10 else "")})
    return pd.DataFrame(rows)


# ------------------------------------------------------------------------------ H5
def tbl_h5(df, systems):
    rows = []
    for s in systems:
        d = df[(df.system == s) & df.resolved]
        wide = d.pivot_table(index="item_id", columns="lang", values="status", aggfunc="first")
        wide = wide.reindex(columns=C.LANGS).dropna()
        n = len(wide)
        if n == 0:
            rows.append({"hypothesis": "H5", "confirmatory": True, "system": s, "n_stores_all5": 0, "interpretable": False, "note": "no store has all 5 languages"}); continue
        inc = wide.nunique(axis=1) > 1
        k = int(inc.sum())
        w_lo, w_hi = S.wilson(k, n)
        c_lo, c_hi = S.clopper_pearson(k, n)
        low1 = S.clopper_pearson_lower_onesided(k, n)
        # 탐색: 단정한 답끼리의 충돌(영업 대 폐업)
        conflict = wide.apply(lambda r: set(r) >= {"open", "closed"}, axis=1)
        kc = int(conflict.sum())
        rows.append({"hypothesis": "H5", "confirmatory": True, "system": s, "n_stores_all5": n, "n_inconsistent": k, "prop_inconsistent": k / n,
                     "wilson_lo": w_lo, "wilson_hi": w_hi, "exact_lo": c_lo, "exact_hi": c_hi, "exact_lower_onesided_95": low1,
                     "supported(lower>0)": bool(low1 > 0), "n_open_vs_closed_conflict(exploratory)": kc,
                     "prop_open_vs_closed_conflict(exploratory)": kc / n, "interpretable": ok(n),
                     "note": "p-value undefined for H0: p=0; decision by CI lower bound"})
    return pd.DataFrame(rows)


# ------------------------------------------------------------------------------ 종합 모형
def tbl_model(df):
    d = df[df.resolved].copy()
    if d.empty:
        return pd.DataFrame(), {}
    systems = [s for s in C.SYSTEMS if s in set(d.system)]
    ref_sys = "H-mem" if "H-mem" in systems else systems[0]
    cols, names = [np.ones(len(d))], ["Intercept"]
    for lg in C.LANGS[1:]:
        cols.append((d.lang == lg).astype(float).values); names.append(f"lang[{lg}] vs ko")
    cols.append((d.truth == "closed").astype(float).values); names.append("truth[closed] vs open")
    cols.append((d.kakao == "unregistered").astype(float).values); names.append("kakao[unregistered] vs registered")
    cols.append((d.region == "province").astype(float).values); names.append("region[province] vs metro")
    for s in systems:
        if s != ref_sys:
            cols.append((d.system == s).astype(float).values); names.append(f"system[{s}] vs {ref_sys}")
    X = np.column_stack(cols)
    r = S.fit_glmm_logit(X, d["acc"].values, d["item_id"].values, names)
    meta = {"n": r.n, "stores": r.g, "events_correct": r.events, "ok": r.ok, "sigma_store": r.sigma, "loglik": r.loglik,
            "converged": r.converged, "note": r.note, "reference_system": ref_sys}
    if not r.ok:
        return pd.DataFrame(), meta
    if not np.all(np.isfinite(r.se[~np.isnan(r.beta)])) or r.events < 10:
        meta["note"] = (meta["note"] + " NOT REPORTED: unstable fit (separation / fewer than 10 correct answers; SE not finite).").strip()
        meta["ok"] = False
        return pd.DataFrame(), meta
    t = pd.DataFrame(r.table())
    t.insert(0, "model", "correct_lenient ~ lang + truth + kakao + region + system + (1|store)")
    t.insert(1, "confirmatory", True)
    return t, meta


# ------------------------------------------------------------------------------ Holm
def tbl_holm(h1, h2, h3, h4):
    rows = []
    for _, r in h1[h1.confirmatory].iterrows():
        rows.append(("H1", f"{r.system}", r.p_two, r["p_directional(A>B)"], r.interpretable))
    for _, r in h2[h2.confirmatory].iterrows():
        rows.append(("H2", f"{r.system}|{r.lang}", r.p_two, r["p_directional(lang<ko)"], r.interpretable))
    for _, r in h3[h3.confirmatory].iterrows():
        rows.append(("H3", "H-search vs H-mem (all langs)", r.p_two, r["p_directional(search<mem)"], r.interpretable))
    for _, r in h4.iterrows():
        rows.append(("H4", f"{r.system}", r.get("p_two", float("nan")), r.get("p_directional(slope<0)", float("nan")), r.interpretable))
    t = pd.DataFrame(rows, columns=["hypothesis", "test", "p_two", "p_directional", "interpretable"])
    t["in_family"] = t.interpretable & t.p_two.notna()
    for col, outc in (("p_two", "holm_p_two_all"), ("p_directional", "holm_p_directional_all")):
        v = t[col].where(t.in_family)
        t[outc] = S.holm(v.values)
    for col, outc in (("p_two", "holm_p_two_by_hypothesis"), ("p_directional", "holm_p_directional_by_hypothesis")):
        t[outc] = np.nan
        for h, g in t.groupby("hypothesis"):
            v = g[col].where(g.in_family)
            t.loc[g.index, outc] = S.holm(v.values)
    t["note"] = np.where(t.in_family, "", "not in Holm family: cell n<%d or p undefined" % C.MIN_CELL_N)
    return t


# ------------------------------------------------------------------------------ 보조
def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def data_fingerprint():
    h = hashlib.sha256()
    n = 0
    for sub in ("raw", "raw_retry"):
        for f in sorted((C.COLLECT / sub).rglob("*.jsonl")):
            if "_partial" in f.parts or "W-mem" in f.parts:
                continue
            h.update(f.relative_to(C.COLLECT).as_posix().encode()); h.update(sha256_file(f).encode()); n += 1
    return {"files": n, "sha256_of_file_hashes": h.hexdigest()}


def write_csv(df, path):
    df.to_csv(path, index=False, encoding="utf-8", lineterminator="\n", float_format="%.6g")


def main(argv=None):
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dryrun", action="store_true", help="있는 데이터로 시험 실행 -> out_dryrun/")
    g.add_argument("--final", action="store_true", help="수집 완료 뒤 확정 실행 -> out_final/ (미완이면 거부)")
    ap.add_argument("--search-validity", default="strict", choices=["strict", "searches_only"])
    ap.add_argument("--dict-only", action="store_true", help="LLM 보조 라벨을 쓰지 않고 사전 판정만(미해결은 review). 기본 출력 analysis/out_dictonly/ (--dryrun과 함께만)")
    ap.add_argument("--only-qids-from", help="이 judgments.csv에 있는 (system, qid)로 답을 제한(이전 실행과 같은 답 집합으로 비교할 때)")
    ap.add_argument("--rater-b", action="store_true", help="사람 2인 판정 대신 독립 LLM 판정자 B(analysis/llm_judge/out_b)의 일치도 평가. --final 에서는 이것 또는 사람 시트 둘 중 하나가 있어야 한다")
    ap.add_argument("--out", help="출력 폴더 덮어쓰기 (기본 analysis/out_dryrun 또는 out_final)")
    a = ap.parse_args(argv)
    if a.dict_only and not a.dryrun:
        sys.exit("--dict-only 는 --dryrun 과 함께만 쓴다(확정 실행은 미판정이 0이어야 하므로).")
    mode = ("dryrun_dictonly" if a.dict_only else "dryrun") if a.dryrun else "final"
    out = Path(a.out) if a.out else C.HERE / ("out_dictonly" if a.dict_only else ("out_dryrun" if a.dryrun else "out_final"))

    answers, inv, warns = L.load_answers(a.search_validity)
    if a.only_qids_from:
        keep = pd.read_csv(a.only_qids_from, usecols=["system", "qid"])
        keep = set(zip(keep["system"], keep["qid"]))
        answers = [x for x in answers if (x["system"], x["qid"]) in keep]
    store = L.load_sample()
    store_by_id = {r["item_id"]: r for r in store}
    incomplete = [r for r in inv if r.get("expected") and r["valid"] < r["expected"]]
    if a.final and incomplete:
        sys.exit("REFUSED: --final needs every system complete. Incomplete: " +
                 ", ".join(f'{r["system"]} {r["valid"]}/{r["expected"]}' for r in incomplete))
    out.mkdir(parents=True, exist_ok=True)

    llm_path = out / "llm_labels.jsonl"
    if not llm_path.exists():
        llm_path = C.HERE / "llm_judge" / "llm_labels.jsonl"      # analysis/llm_judge/merge.py 산출 (판정자는 질문·답만 봤다)
    llm = {} if a.dict_only else J.load_llm_labels(llm_path)
    judged = J.judge_all(answers, store_by_id, llm)
    n_stale = len(J.STALE_LLM)
    agree = llm_agreement(answers, store_by_id, llm, out)
    n_review_q = J.write_review_queue(judged, out / "review_queue.jsonl")
    df = build_frame(judged, store)
    unresolved = int((~df.resolved).sum())
    if unresolved:       # 보고 없이 지나가지 않게: 개수와 목록을 파일로 남긴다
        write_csv(df.loc[~df.resolved, ["system", "qid", "lang", "status", "address", "type"]], out / "unresolved_items.csv")
        print(f"UNRESOLVED review items: {unresolved} (list: {out / 'unresolved_items.csv'})")
    if a.final and unresolved:
        sys.exit(f"REFUSED: {unresolved} answers still unresolved (review). Resolve via LLM-assist labels or human judgment first.")
    systems = [s for s in C.SYSTEMS if (df.system == s).any()]

    pub = df.drop(columns=["acc", "wrong", "says_open", "says_closed", "acc_strict"])
    write_csv(pub.assign(mode=mode), out / "judgments.csv")
    write_csv(pd.DataFrame(inv).assign(mode=mode), out / "data_inventory.csv")
    jd = []
    for s in systems:
        g = df[df.system == s]
        row = {"system": s, "n": len(g)}
        for c in ("status", "address", "type"):
            for k, v in g[c].value_counts().items():
                row[f"{c}={k}"] = int(v)
        row["judge_source_llm"] = int((g.judge_source == "llm").sum())
        jd.append(row)
    write_csv(pd.DataFrame(jd).fillna(0).assign(mode=mode), out / "judge_diagnostics.csv")

    t_dist, t_acc = tbl_status_distribution(df), tbl_accuracy(df)
    t_h1, t_h2, t_h3, t_h4, t_h5 = tbl_h1(df, systems), tbl_h2(df, systems), tbl_h3(df), tbl_h4(df, systems), tbl_h5(df, systems)
    t_expl = tbl_exploratory(df)
    t_model, model_meta = tbl_model(df)
    t_holm = tbl_holm(t_h1, t_h2, t_h3, t_h4)
    for name, t in (("status_distribution", t_dist), ("accuracy_by_system_lang", t_acc), ("h1", t_h1), ("h2", t_h2), ("h3", t_h3),
                    ("h4", t_h4), ("h5", t_h5), ("model_coefficients", t_model), ("holm", t_holm), ("exploratory_summary", t_expl)):
        if len(t):
            write_csv(t.assign(mode=mode), out / f"{name}.csv")
        elif (out / f"{name}.csv").exists():
            (out / f"{name}.csv").unlink()      # 이전 실행의 묵은 표가 남지 않게

    # 사람 표본(시험) + 카파
    keys, note = HS.draw_sample(answers)
    kappas, kappas_b, b_problems = None, None, []
    if a.rater_b:
        raw_b, b_problems = HS.load_rater_b(C.HERE / "llm_judge", answers)
        if len(raw_b) != len(keys) or set(raw_b) != set(keys):
            b_problems.append(f"rater B coverage {len(raw_b)}/{len(keys)} or sample differs from draw_sample")
        if b_problems and a.final:
            sys.exit("REFUSED: rater B incomplete/invalid: " + "; ".join(b_problems[:8]))
        if raw_b and not b_problems:
            kappas_b = HS.compute_kappas_b(judged, store_by_id, raw_b, llm)
            write_csv(pd.DataFrame(kappas_b).assign(mode=mode), out / "kappa_rater_b.csv")
    else:
        HS.write_sheets(keys, answers, out, a.dryrun)
        fa, fb = out / "human_sample" / "rater_A_filled.csv", out / "human_sample" / "rater_B_filled.csv"
        if fa.exists() and fb.exists():
            kappas = HS.compute_kappas(out, judged, store_by_id, fa, fb)
            write_csv(pd.DataFrame(kappas).assign(mode=mode), out / "kappa.csv")
        elif a.final:
            sys.exit("REFUSED: --final needs rater evidence: pass --rater-b or fill human_sample/rater_A_filled.csv and rater_B_filled.csv.")

    banner = ("DRY-RUN DICTIONARY-ONLY (사전 판정 단독, LLM 보조 라벨 미사용; 미해결은 review=미판정). prereg 8절 원 규칙 결과 보고용. 논문·보도에 쓰지 말 것." if a.dict_only else
              "DRY-RUN / PROVISIONAL. 수집 미완 + 판정 사전 미검증 상태의 시험 결과. 논문·보도에 쓰지 말 것." if a.dryrun
              else "FINAL run (collection complete).")
    (out / ("DRYRUN_NOT_FOR_PUBLICATION.txt" if a.dryrun else "FINAL.txt")).write_text(banner + "\n", encoding="utf-8")

    def recs(t):
        return json.loads(t.to_json(orient="records", force_ascii=False)) if len(t) else []

    results = {
        "mode": mode, "banner": banner, "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "environment": {"python": platform.python_version(), "numpy": np.__version__, "pandas": pd.__version__},
        "inputs": {"sample_v2_sha256": sha256_file(C.SAMPLE_CSV), "rules_md_sha256": sha256_file(C.RULES_MD),
                   "prereg_md_sha256": sha256_file(C.ROOT / "prereg.md"), "answers_fingerprint": data_fingerprint(),
                   "search_validity": a.search_validity, "llm_labels_used": len(llm), "llm_labels_path": str(llm_path),
                   "llm_labels_stale_dropped": n_stale},
        "llm_dictionary_agreement": agree,
        "counts": {"answers_included": len(df), "unresolved_review": unresolved, "review_queue_rows": n_review_q,
                   "by_system": df.groupby("system").size().to_dict()},
        "data_inventory": inv, "warnings": warns,
        "tables": {"status_distribution": recs(t_dist), "accuracy_by_system_lang": recs(t_acc), "H1": recs(t_h1), "H2": recs(t_h2),
                   "H3": recs(t_h3), "H4": recs(t_h4), "H5": recs(t_h5), "model": recs(t_model), "model_meta": model_meta, "holm": recs(t_holm),
                   "exploratory_summary": recs(t_expl)},
        "human_sample": {"n": len(keys), "note": note, "kappa": kappas},
        "rater_b": {"used": bool(a.rater_b), "n": len(keys), "problems": b_problems, "kappa": kappas_b,
                    "judges": "primary = dictionary + Claude Sonnet; rater B = Claude Haiku (independent wording)"},
        "ambiguities_needing_confirmation": AMBIGUITIES,
        "min_cell_n": C.MIN_CELL_N,
    }
    (out / "results.json").write_text(json.dumps(results, ensure_ascii=False, indent=1, default=str), encoding="utf-8", newline="\n")

    print(banner)
    print(f"out: {out}")
    print(f"answers: {len(df)}  unresolved(review): {unresolved}")
    for r in inv:
        print("  ", {k: r[k] for k in ("system", "valid", "expected", "missing_rate") if k in r})
    print(t_h1[t_h1.variant == "all_answers"][["system", "n_closed", "n_open", "p_says_open_given_closed", "p_says_closed_given_open", "diff_A_minus_B", "interpretable"]].to_string(index=False))


if __name__ == "__main__":
    main()
