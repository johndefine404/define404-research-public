"""사전 등록 분석 뼈대 (경량판, 표준 라이브러리만). 입력 judge/judged.csv → 출력 analysis/out/results.json, tables.md.
- 비율마다 95% 신뢰구간: 메뉴가 군집. 한 메뉴·한 언어에 답 1개이므로 메뉴별 지표의 평균과 정규근사 구간(Wilson 병기).
- H1: 같은 메뉴 짝 차이 (en 엄격 일치 - ja 엄격 일치), 짝 차이의 평균과 표준오차, 단측 p(en > ja).
- H2: en 문항에서 표준 출처 참조 여부별 엄격 일치율 차이(독립 두 집단, 정규근사), 단측 p(참조 > 미참조).
- Holm 보정(가설 2개). 표본 40 미만 칸은 해석 안 함 표시. 탐색 분석은 exploratory 키 아래 따로."""
import csv, json, math
from collections import defaultdict
from pathlib import Path
from statistics import NormalDist

HERE = Path(__file__).parent
JUDGED = HERE.parent / "judge" / "judged.csv"
OUT = HERE / "out"
Z = NormalDist().inv_cdf(0.975)
N = NormalDist()

def wilson(k, n):
    if n == 0:
        return (math.nan, math.nan)
    p = k / n; d = 1 + Z * Z / n
    c = (p + Z * Z / (2 * n)) / d; h = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))

def prop(values):
    n = len(values); k = sum(values)
    p = k / n if n else math.nan
    se = math.sqrt(p * (1 - p) / n) if n else math.nan
    lo, hi = wilson(k, n)
    return {"k": k, "n": n, "p": p, "se": se, "ci_wilson": [lo, hi], "interpret": n >= 40}

def paired(a, b):
    d = [x - y for x, y in zip(a, b)]; n = len(d)
    m = sum(d) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in d) / (n - 1)) if n > 1 else math.nan
    se = sd / math.sqrt(n)
    z = m / se if se else math.nan
    return {"n_pairs": n, "diff": m, "se": se, "ci": [m - Z * se, m + Z * se], "z": z, "p_one_sided": 1 - N.cdf(z), "p_two_sided": 2 * (1 - N.cdf(abs(z)))}

def two_group(a, b):
    pa, pb = prop(a), prop(b)
    d = pa["p"] - pb["p"]; se = math.sqrt(pa["se"] ** 2 + pb["se"] ** 2)
    z = d / se if se else math.nan
    return {"group_a": pa, "group_b": pb, "diff": d, "se": se, "ci": [d - Z * se, d + Z * se], "z": z,
            "p_one_sided": 1 - N.cdf(z) if not math.isnan(z) else math.nan, "p_two_sided": 2 * (1 - N.cdf(abs(z))) if not math.isnan(z) else math.nan,
            "interpret": pa["n"] >= 40 and pb["n"] >= 40}

def holm(pvals):
    order = sorted(range(len(pvals)), key=lambda i: pvals[i]); adj = [0] * len(pvals); run = 0
    for rank, i in enumerate(order):
        run = max(run, (len(pvals) - rank) * pvals[i]); adj[i] = min(1.0, run)
    return adj

def main():
    rows = list(csv.DictReader(JUDGED.open(encoding="utf-8")))
    by = defaultdict(dict)
    for r in rows:
        by[r["sid"]][r["lang"]] = r
    res = {"n_items": len(rows), "n_menus": len(by), "preregistered": {}, "exploratory": {}}
    for lang in ("en", "ja"):
        sub = [r for r in rows if r["lang"] == lang]
        res["preregistered"][f"rates_{lang}"] = {v: prop([int(r["verdict"] == v) for r in sub]) for v in ("strict", "loose", "mismatch", "no_answer")}
        res["preregistered"][f"rates_{lang}"]["loose_or_strict"] = prop([int(r["verdict"] in ("strict", "loose")) for r in sub])
    pairs = [(by[s]["en"], by[s]["ja"]) for s in by if "en" in by[s] and "ja" in by[s]]
    h1 = paired([int(a["verdict"] == "strict") for a, _ in pairs], [int(b["verdict"] == "strict") for _, b in pairs])
    en = [r for r in rows if r["lang"] == "en"]
    h2 = two_group([int(r["verdict"] == "strict") for r in en if r["cites_hansik"] == "1"], [int(r["verdict"] == "strict") for r in en if r["cites_hansik"] != "1"])
    adj = holm([h1["p_one_sided"], h2["p_one_sided"]])
    h1["p_holm"], h2["p_holm"] = adj
    res["preregistered"]["H1_en_minus_ja_strict_paired"] = h1
    res["preregistered"]["H2_strict_by_hansik_citation_en"] = h2
    res["exploratory"]["cites_hansik_rate"] = {lang: prop([int(r["cites_hansik"] == "1") for r in rows if r["lang"] == lang]) for lang in ("en", "ja")}
    res["exploratory"]["ingredient_mismatch_among_en_mismatch"] = prop([int(r["ingredient_mismatch"] == "1") for r in en if r["verdict"] == "mismatch"])
    res["exploratory"]["strict_by_category_en"] = {c: prop([int(r["verdict"] == "strict") for r in en if r["category"] == c]) for c in sorted({r["category"] for r in en})}
    res["exploratory"]["flags"] = {f: sum(1 for r in rows if f in r["flags"].split("|")) for f in ("multiple", "manual", "extract_fail", "empty")}
    OUT.mkdir(exist_ok=True)
    (OUT / "results.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    lines = ["# 결과 표 (자동 생성, 손으로 고치지 않는다)", "", "| 지표 | 언어 | 비율 | 95% CI | n |", "|---|---|---|---|---|"]
    for lang in ("en", "ja"):
        for v, d in res["preregistered"][f"rates_{lang}"].items():
            lines.append(f"| {v} | {lang} | {d['p']:.3f} | {d['ci_wilson'][0]:.3f}~{d['ci_wilson'][1]:.3f} | {d['n']}{'' if d['interpret'] else ' (40 미만, 해석 안 함)'} |")
    lines += ["", f"H1 짝 차이(en-ja 엄격): {h1['diff']:.3f} [{h1['ci'][0]:.3f}, {h1['ci'][1]:.3f}], 단측 p {h1['p_one_sided']:.4f}, Holm {h1['p_holm']:.4f}, 짝 {h1['n_pairs']}",
              f"H2 출처 참조-미참조(en 엄격): {h2['diff']:.3f} [{h2['ci'][0]:.3f}, {h2['ci'][1]:.3f}], 단측 p {h2['p_one_sided']:.4f}, Holm {h2['p_holm']:.4f}, n {h2['group_a']['n']}/{h2['group_b']['n']}{'' if h2['interpret'] else ' (40 미만 칸, 해석 안 함)'}"]
    (OUT / "tables.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))

if __name__ == "__main__":
    main()
