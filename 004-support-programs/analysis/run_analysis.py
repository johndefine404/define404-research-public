#!/usr/bin/env python3
# [Define404] 004 지원사업 질문: 사전 등록 분석 뼈대 (경량판: 95% CI, 짝 차이, Holm)
# 입력: judge/judged.csv   출력: analysis/out/results.json, analysis/out/tables.md
# 표준 라이브러리만 쓴다. 대상(공고)마다 답이 1개(언어 1, 시스템 1)이므로 대상 단위 군집 CI는 Wilson 구간과 같다.
# 사전 등록 분석(H1, H2)과 탐색 분석을 파일 안에서 나눈다.

import csv
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
Z = 1.959963984540054
MIN_CELL = 40


def norm_sf(z):
    return 0.5 * math.erfc(z / math.sqrt(2))


def wilson(k, n):
    if n == 0:
        return None
    p = k / n
    den = 1 + Z * Z / n
    c = (p + Z * Z / (2 * n)) / den
    h = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n)) / den
    return {"k": k, "n": n, "p": p, "lo": max(0.0, c - h), "hi": min(1.0, c + h), "interpret": n >= MIN_CELL}


def two_prop_diff(k1, n1, k2, n2):
    # 독립 두 비율 차이 (p1 - p2), Wald CI와 양측 z 검정(합동 분산)
    p1, p2 = k1 / n1, k2 / n2
    se = math.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
    pp = (k1 + k2) / (n1 + n2)
    se0 = math.sqrt(pp * (1 - pp) * (1 / n1 + 1 / n2)) or 1e-12
    z = (p1 - p2) / se0
    return {"diff": p1 - p2, "lo": p1 - p2 - Z * se, "hi": p1 - p2 + Z * se, "z": z, "p_two_sided": 2 * norm_sf(abs(z))}


def paired_diff(pairs):
    # 같은 대상의 두 조건(0/1) 짝 차이. Miller 2024: 차이의 표준오차 = sd(diff)/sqrt(n)
    d = [a - b for a, b in pairs]
    n = len(d)
    if n < 2:
        return None
    m = sum(d) / n
    var = sum((x - m) ** 2 for x in d) / (n - 1)
    se = math.sqrt(var / n)
    z = m / se if se > 0 else 0.0
    return {"n": n, "diff": m, "lo": m - Z * se, "hi": m + Z * se, "z": z, "p_two_sided": 2 * norm_sf(abs(z))}


def holm(pvals):
    # pvals: {이름: p}. 반환: {이름: 보정 p}
    items = sorted(pvals.items(), key=lambda kv: kv[1])
    m = len(items)
    adj, running = {}, 0.0
    for i, (name, p) in enumerate(items):
        running = max(running, min(1.0, (m - i) * p))
        adj[name] = running
    return adj


def one_sided_p(stat, direction):
    # direction "greater": H1 diff > 0, "less": diff < 0
    z = stat["z"]
    return norm_sf(z) if direction == "greater" else norm_sf(-z)


def main():
    rows = [r for r in csv.DictReader(open(ROOT / "judge" / "judged.csv", encoding="utf-8"))
            if "invalid-no-search" not in r["flags"] and "empty" not in r["flags"]]
    res = {"n_used": len(rows), "preregistered": {}, "exploratory": {}}

    # 비율표: 층별 느슨·엄격·상태 단정
    def cell(filt):
        sub = [r for r in rows if filt(r)]
        return {"loose": wilson(sum(int(r["loose"]) for r in sub), len(sub)),
                "strict": wilson(sum(int(r["strict"]) for r in sub), len(sub)),
                "status_ok": wilson(sum(int(r["status_ok"]) for r in sub), len(sub)),
                "unknown": wilson(sum(r["status_claim"] == "unknown" for r in sub), len(sub))}
    res["preregistered"]["cells"] = {
        "all": cell(lambda r: True),
        "central": cell(lambda r: r["jurisdiction"] == "central"),
        "local": cell(lambda r: r["jurisdiction"] == "local"),
        "ongoing": cell(lambda r: r["status"] == "ongoing"),
        "expired": cell(lambda r: r["status"] == "expired"),
    }

    # H1: 마감일 맞음 비율, 지자체 < 중앙부처 (단측)
    c = [r for r in rows if r["jurisdiction"] == "central"]
    l = [r for r in rows if r["jurisdiction"] == "local"]
    h1 = two_prop_diff(sum(int(r["loose"]) for r in l), len(l), sum(int(r["loose"]) for r in c), len(c)) if c and l else None
    # H2: 마감 공고를 "가능" 단정 비율 > 진행 공고를 "마감" 단정 비율 (단측)
    e = [r for r in rows if r["status"] == "expired"]
    o = [r for r in rows if r["status"] == "ongoing"]
    h2 = two_prop_diff(sum(r["status_claim"] == "open" for r in e), len(e),
                       sum(r["status_claim"] == "closed" for r in o), len(o)) if e and o else None
    pv = {}
    if h1:
        h1["p_one_sided"] = one_sided_p(h1, "less")
        pv["H1"] = h1["p_one_sided"]
    if h2:
        h2["p_one_sided"] = one_sided_p(h2, "greater")
        pv["H2"] = h2["p_one_sided"]
    adj = holm(pv) if pv else {}
    res["preregistered"]["H1"] = dict(h1 or {}, p_holm=adj.get("H1"))
    res["preregistered"]["H2"] = dict(h2 or {}, p_holm=adj.get("H2"))

    # 짝 차이(같은 대상): 느슨 대 엄격 (기술 통계, 가설 아님)
    res["exploratory"]["loose_minus_strict_paired"] = paired_diff([(int(r["loose"]), int(r["strict"])) for r in rows])
    # 탐색: 지원분야별, 상태 x 소관 4칸 (40 미만 칸은 해석하지 않는다)
    res["exploratory"]["by_cell"] = {f"{s}/{j}": cell(lambda r, s=s, j=j: r["status"] == s and r["jurisdiction"] == j)
                                     for s in ("ongoing", "expired") for j in ("central", "local")}

    out = HERE / "out"
    out.mkdir(exist_ok=True)
    (out / "results.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")

    def fmt(w):
        return "n<40, 해석 안 함" if w and not w["interpret"] else (f"{w['p']*100:.1f}% [{w['lo']*100:.1f}, {w['hi']*100:.1f}] (n={w['n']})" if w else "-")
    lines = ["# 결과표 (자동 생성, 손으로 고치지 않는다)", "", f"사용 답 수: {res['n_used']}", "",
             "## 표 1. 비율 (95% Wilson CI, 대상 단위)", "", "| 칸 | 느슨(마감일 맞음) | 엄격 | 신청 가능 여부 맞음 | 모름 |", "|---|---|---|---|---|"]
    for k, v in res["preregistered"]["cells"].items():
        lines.append(f"| {k} | {fmt(v['loose'])} | {fmt(v['strict'])} | {fmt(v['status_ok'])} | {fmt(v['unknown'])} |")
    lines += ["", "## 표 2. 사전 등록 가설", "", "| 가설 | 차이 | 95% CI | 단측 p | Holm p |", "|---|---|---|---|---|"]
    for h in ("H1", "H2"):
        v = res["preregistered"][h]
        if v.get("diff") is not None:
            lines.append(f"| {h} | {v['diff']*100:+.1f}%p | [{v['lo']*100:.1f}, {v['hi']*100:.1f}] | {v['p_one_sided']:.4f} | {v['p_holm']:.4f} |")
    lines += ["", "## 표 3. 탐색 (사전 등록 아님)", ""]
    for k, v in res["exploratory"]["by_cell"].items():
        lines.append(f"- {k}: 느슨 {fmt(v['loose'])}, 엄격 {fmt(v['strict'])}")
    pdf = res["exploratory"]["loose_minus_strict_paired"]
    if pdf:
        lines.append(f"- 느슨 - 엄격 짝 차이: {pdf['diff']*100:+.1f}%p [{pdf['lo']*100:.1f}, {pdf['hi']*100:.1f}] (n={pdf['n']})")
    (out / "tables.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
