#!/usr/bin/env python3
# [Define404] 007 관광객 추천 식당: 사전 등록 분석 (표준 라이브러리만)
# 입력: judge/judged.csv, judge/answers.csv  출력: analysis/out/*.json, *.csv
# 단위: 추천 가게. 군집: 시군구(area_id). 비율의 95% 신뢰구간은 군집 비율 추정량의 델타 방법 표준오차.
import csv, json, math, os
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
JUDGE = Path(os.environ.get("D404_JUDGE", ROOT / "judge"))
OUT = Path(os.environ.get("D404_OUT", HERE / "out"))
Z = 1.959963984540054
MIN_CELL = 40


def norm_sf(z):
    return 0.5 * math.erfc(z / math.sqrt(2))


def ratio(clusters):
    """clusters: [(k, n)]. 합 비율과 군집 표준오차."""
    cl = [(k, n) for k, n in clusters if n > 0]
    m, K, N = len(cl), sum(k for k, _ in cl), sum(n for _, n in cl)
    if N == 0 or m < 2:
        return {"k": K, "n": N, "clusters": m, "p": None, "se": None, "lo": None, "hi": None}
    p = K / N
    se = math.sqrt(m / (m - 1) * sum((k - p * n) ** 2 for k, n in cl)) / N
    return {"k": K, "n": N, "clusters": m, "p": p, "se": se, "lo": max(0.0, p - Z * se), "hi": min(1.0, p + Z * se),
            "interpret": N >= MIN_CELL}


def paired(diffs, direction=1):
    m = len(diffs)
    if m < 2:
        return {"pairs": m}
    mean = sum(diffs) / m
    sd = math.sqrt(sum((d - mean) ** 2 for d in diffs) / (m - 1))
    se = sd / math.sqrt(m)
    z = mean / se if se > 0 else 0.0
    return {"pairs": m, "diff": mean, "se": se, "lo": mean - Z * se, "hi": mean + Z * se,
            "p_one_sided": norm_sf(direction * z)}


def holm(ps):
    keys = sorted(ps, key=lambda k: ps[k])
    out, run = {}, 0.0
    for i, k in enumerate(keys):
        run = max(run, min(1.0, (len(keys) - i) * ps[k]))
        out[k] = run
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    recs = [r for r in csv.DictReader(open(JUDGE / "judged.csv", encoding="utf-8")) if r["in_answer"] == "1"]
    answers = list(csv.DictReader(open(JUDGE / "answers.csv", encoding="utf-8")))
    res = {"n_answers": len(answers), "n_invalid": sum(1 for a in answers if a["invalid"]),
           "n_recs_in_answer": len(recs)}
    for mode in ("loose", "strict"):
        col = f"{mode}_status"
        cnt = defaultdict(lambda: [0, 0, 0])  # (area, lang) -> [closed, matched, all]
        for r in recs:
            c = cnt[(r["area_id"], r["lang"])]
            c[2] += 1
            if r[col] in ("영업", "폐업"):
                c[1] += 1
                c[0] += r[col] == "폐업"
        strata = {r["area_id"]: r["stratum"] for r in recs}
        areas = sorted({a for a, _ in cnt})
        R = {}
        # 전체·언어별 폐업 비율(확인된 추천 가게 중)
        R["closed_all"] = ratio([(sum(cnt[(a, l)][0] for l in ("ko", "en")), sum(cnt[(a, l)][1] for l in ("ko", "en"))) for a in areas])
        for l in ("ko", "en"):
            R[f"closed_{l}"] = ratio([(cnt[(a, l)][0], cnt[(a, l)][1]) for a in areas])
            R[f"unverified_{l}"] = ratio([(cnt[(a, l)][2] - cnt[(a, l)][1], cnt[(a, l)][2]) for a in areas])
        R["unverified_all"] = ratio([(sum(cnt[(a, l)][2] - cnt[(a, l)][1] for l in ("ko", "en")), sum(cnt[(a, l)][2] for l in ("ko", "en"))) for a in areas])
        # H1: 영어 > 한국어 폐업 비율, 짝(두 언어 모두 확인된 가게가 있는 시군구)
        d1 = [cnt[(a, "en")][0] / cnt[(a, "en")][1] - cnt[(a, "ko")][0] / cnt[(a, "ko")][1]
              for a in areas if cnt[(a, "en")][1] and cnt[(a, "ko")][1]]
        R["H1"] = paired(d1, 1)
        # H2: 도 > 광역 폐업 비율(두 언어 합)
        g = {s: ratio([(sum(cnt[(a, l)][0] for l in ("ko", "en")), sum(cnt[(a, l)][1] for l in ("ko", "en")))
                       for a in areas if strata[a] == s]) for s in ("도", "광역")}
        R["closed_do"], R["closed_metro"] = g["도"], g["광역"]
        if g["도"]["p"] is not None and g["광역"]["p"] is not None:
            diff = g["도"]["p"] - g["광역"]["p"]
            se = math.sqrt(g["도"]["se"] ** 2 + g["광역"]["se"] ** 2)
            R["H2"] = {"diff": diff, "se": se, "lo": diff - Z * se, "hi": diff + Z * se,
                       "p_one_sided": norm_sf(diff / se) if se > 0 else None}
        # H3: 인허가에서 못 찾은 비율 영어 > 한국어, 짝
        d3 = [(cnt[(a, "en")][2] - cnt[(a, "en")][1]) / cnt[(a, "en")][2] - (cnt[(a, "ko")][2] - cnt[(a, "ko")][1]) / cnt[(a, "ko")][2]
              for a in areas if cnt[(a, "en")][2] and cnt[(a, "ko")][2]]
        R["H3"] = paired(d3, 1)
        ps = {h: R[h]["p_one_sided"] for h in ("H1", "H2", "H3") if R.get(h, {}).get("p_one_sided") is not None}
        R["holm"] = holm(ps)
        res[mode] = R
        with open(OUT / f"area_counts_{mode}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["area_id", "stratum", "lang", "closed", "matched", "recs"])
            for (a, l), c in sorted(cnt.items()):
                w.writerow([a, strata[a], l, *c])
    (OUT / "results.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    L = res["loose"]
    print(json.dumps({k: (L[k]["p"] if "p" in L[k] else L[k]) for k in ("closed_all", "closed_ko", "closed_en", "unverified_all")}, ensure_ascii=False))
    print("H1", L["H1"], "\nH2", L.get("H2"), "\nH3", L["H3"], "\nholm", L["holm"])


if __name__ == "__main__":
    main()
