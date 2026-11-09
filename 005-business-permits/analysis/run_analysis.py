#!/usr/bin/env python3
# [Define404] 005 영업 행정 질문: 사전 등록 분석 뼈대 (경량판: 95% CI, 짝 차이, Holm)
# 입력: judge/judged.csv   출력: analysis/out/results.json, analysis/out/tables.md
# 표준 라이브러리만 쓴다. 대상(민원)마다 답이 1개(언어 1, 시스템 1)이므로 대상 단위 군집 CI는 Wilson 구간과 같다.
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


def days(v):
    return 0 if v == "즉시" else int(v[:-1])


def main():
    import sys
    src, outname = (sys.argv[1], sys.argv[2]) if len(sys.argv) > 2 else ("judged.csv", "out")
    rows = [r for r in csv.DictReader(open(ROOT / "judge" / src, encoding="utf-8"))
            if "invalid-no-search" not in r["flags"] and "empty" not in r["flags"]]
    res = {"n_used": len(rows), "preregistered": {}, "exploratory": {}}

    def rate(sub, f):
        return wilson(sum(1 for r in sub if f(r)), len(sub))

    def cell(filt):
        sub = [r for r in rows if filt(r)]
        return {"period_loose": rate(sub, lambda r: r["period_loose"] == "1"),
                "period_strict": rate(sub, lambda r: r["period_strict"] == "1"),
                "period_wrong": rate(sub, lambda r: r["period_verdict"] == "wrong"),
                "period_unknown": rate(sub, lambda r: r["period_verdict"] == "unknown"),
                "fee_loose": rate(sub, lambda r: r["fee_loose"] == "1"),
                "fee_strict": rate(sub, lambda r: r["fee_strict"] == "1"),
                "fee_wrong": rate(sub, lambda r: r["fee_verdict"] == "wrong"),
                "fee_unknown": rate(sub, lambda r: r["fee_verdict"] == "unknown"),
                "both_strict": rate(sub, lambda r: r["both_strict"] == "1"),
                "both_loose": rate(sub, lambda r: r["both_loose"] == "1")}
    res["preregistered"]["cells"] = {
        "all": cell(lambda r: True),
        "short": cell(lambda r: r["pgroup"] == "short"),
        "long": cell(lambda r: r["pgroup"] == "long"),
        "free": cell(lambda r: r["paid"] == "free"),
        "paid": cell(lambda r: r["paid"] == "paid"),
    }

    # H1 (1차, 짝): 같은 민원에서 수수료 맞음(느슨) - 처리기간 맞음(느슨) < 0 (단측)
    h1 = paired_diff([(int(r["fee_loose"]), int(r["period_loose"])) for r in rows])
    # H2 (2차): 처리기간 맞음(느슨) 짧은 민원(즉시~3일) - 긴 민원(4일 이상) > 0 (단측)
    s = [r for r in rows if r["pgroup"] == "short"]
    l = [r for r in rows if r["pgroup"] == "long"]
    h2 = two_prop_diff(sum(int(r["period_loose"]) for r in s), len(s), sum(int(r["period_loose"]) for r in l), len(l)) if s and l else None
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

    # 탐색(사전 등록 아님)
    ex = res["exploratory"]
    ex["by_city"] = {c: cell(lambda r, c=c: r["city"] == c) for c in sorted({r["city"] for r in rows})}
    # 처리기간이 틀린 답의 방향: 정답보다 짧게/길게 (주장값이 하나인 답만)
    single = [r for r in rows if r["period_verdict"] == "wrong" and "|" not in r["period_claims"]]
    shorter = sum(1 for r in single if days(r["period_claims"]) < days(r["period_true"]))
    ex["period_wrong_direction"] = {"n_single_wrong": len(single), "shorter": shorter, "longer": len(single) - shorter,
                                    "shorter_rate": wilson(shorter, len(single)) if single else None}
    # 수수료가 틀린 답 중 무료 민원을 유료로, 유료 민원을 무료로 말한 건
    fw = [r for r in rows if r["fee_verdict"] == "wrong"]
    ex["fee_wrong_kind"] = {"n_wrong": len(fw),
                            "free_said_paid": sum(1 for r in fw if r["fee_true"] == "무료"),
                            "paid_said_free": sum(1 for r in fw if r["fee_true"] != "무료" and "무료" in r["fee_claims"].split("|")),
                            "paid_other_amount": sum(1 for r in fw if r["fee_true"] != "무료" and "무료" not in r["fee_claims"].split("|"))}
    ex["loose_minus_strict_period"] = paired_diff([(int(r["period_loose"]), int(r["period_strict"])) for r in rows])
    ex["loose_minus_strict_fee"] = paired_diff([(int(r["fee_loose"]), int(r["fee_strict"])) for r in rows])
    # 탐색(시범 20건 본 뒤 추가): "확인하지 못했다"는 단서가 붙은 답과 아닌 답
    ex["hedged"] = {"rate": wilson(sum(1 for r in rows if r.get("hedged") == "1"), len(rows)),
                    "hedged": cell(lambda r: r.get("hedged") == "1"),
                    "plain": cell(lambda r: r.get("hedged") != "1")}
    # 탐색: 숫자를 말한 답만 놓고 본 정답률(맞음 / (맞음 + 틀림))
    ex["given_claim"] = {}
    for name in ("period", "fee"):
        cl = [r for r in rows if r[f"{name}_verdict"] != "unknown"]
        ex["given_claim"][name] = wilson(sum(1 for r in cl if r[f"{name}_verdict"] == "correct"), len(cl)) if cl else None
    ex["searches_mean"] = sum(int(r["searches"] or 0) for r in rows) / len(rows) if rows else None

    out = HERE / outname
    out.mkdir(exist_ok=True)
    (out / "results.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")

    def fmt(w):
        return "-" if not w else ("n<40, 해석 안 함" if not w["interpret"] else f"{w['p']*100:.1f}% [{w['lo']*100:.1f}, {w['hi']*100:.1f}] (n={w['n']})")
    lines = ["# 결과표 (자동 생성, 손으로 고치지 않는다)", "", f"사용 답 수: {res['n_used']}", "",
             "## 표 1. 처리기간 (95% Wilson CI, 대상 단위)", "", "| 칸 | 맞음(느슨) | 맞음(엄격) | 틀림 | 모름 |", "|---|---|---|---|---|"]
    for k, v in res["preregistered"]["cells"].items():
        lines.append(f"| {k} | {fmt(v['period_loose'])} | {fmt(v['period_strict'])} | {fmt(v['period_wrong'])} | {fmt(v['period_unknown'])} |")
    lines += ["", "## 표 2. 수수료", "", "| 칸 | 맞음(느슨) | 맞음(엄격) | 틀림 | 모름 |", "|---|---|---|---|---|"]
    for k, v in res["preregistered"]["cells"].items():
        lines.append(f"| {k} | {fmt(v['fee_loose'])} | {fmt(v['fee_strict'])} | {fmt(v['fee_wrong'])} | {fmt(v['fee_unknown'])} |")
    lines += ["", "## 표 3. 둘 다 맞음", "", "| 칸 | 느슨 | 엄격 |", "|---|---|---|"]
    for k, v in res["preregistered"]["cells"].items():
        lines.append(f"| {k} | {fmt(v['both_loose'])} | {fmt(v['both_strict'])} |")
    lines += ["", "## 표 4. 사전 등록 가설", "", "| 가설 | 차이 | 95% CI | 단측 p | Holm p |", "|---|---|---|---|---|"]
    for h in ("H1", "H2"):
        v = res["preregistered"][h]
        if v.get("diff") is not None:
            lines.append(f"| {h} | {v['diff']*100:+.1f}%p | [{v['lo']*100:.1f}, {v['hi']*100:.1f}] | {v['p_one_sided']:.4f} | {v['p_holm']:.4f} |")
    lines += ["", "## 표 5. 탐색 (사전 등록 아님)", ""]
    for k, v in ex["by_city"].items():
        lines.append(f"- {k}: 처리기간 느슨 {fmt(v['period_loose'])}, 수수료 느슨 {fmt(v['fee_loose'])}")
    d = ex["period_wrong_direction"]
    lines.append(f"- 처리기간 틀린 답(주장값 하나) {d['n_single_wrong']}건: 짧게 {d['shorter']}, 길게 {d['longer']}, 짧게 비율 {fmt(d['shorter_rate'])}")
    k = ex["fee_wrong_kind"]
    lines.append(f"- 수수료 틀린 답 {k['n_wrong']}건: 무료 민원을 유료로 {k['free_said_paid']}, 유료 민원을 무료로 {k['paid_said_free']}, 다른 금액 {k['paid_other_amount']}")
    for name in ("period", "fee"):
        p = ex[f"loose_minus_strict_{name}"]
        if p:
            lines.append(f"- {name} 느슨 - 엄격 짝 차이: {p['diff']*100:+.1f}%p [{p['lo']*100:.1f}, {p['hi']*100:.1f}] (n={p['n']})")
    hd = ex["hedged"]
    lines.append(f"- 확인 못 했다는 단서가 붙은 답: {fmt(hd['rate'])}")
    lines.append(f"  - 단서 있음: 처리기간 느슨 {fmt(hd['hedged']['period_loose'])}, 수수료 느슨 {fmt(hd['hedged']['fee_loose'])}, 둘 다 엄격 {fmt(hd['hedged']['both_strict'])}")
    lines.append(f"  - 단서 없음: 처리기간 느슨 {fmt(hd['plain']['period_loose'])}, 수수료 느슨 {fmt(hd['plain']['fee_loose'])}, 둘 다 엄격 {fmt(hd['plain']['both_strict'])}")
    for name in ("period", "fee"):
        lines.append(f"- {name} 숫자를 말한 답 중 맞음: {fmt(ex['given_claim'][name])}")
    if ex["searches_mean"] is not None:
        lines.append(f"- 문항당 평균 검색 횟수: {ex['searches_mean']:.2f}")
    (out / "tables.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
