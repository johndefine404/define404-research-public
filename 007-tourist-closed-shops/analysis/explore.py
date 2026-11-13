#!/usr/bin/env python3
# [Define404] 007 탐색 분석(사전 등록 밖, 원고에 "탐색"으로 표시). 판정 v1.1 결과를 쓴다.
# 출력: analysis/out/explore.json, analysis/out/summary.csv(공개용, AI 답 원문 없음)
import csv, json, glob, math
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlparse

R = Path(__file__).resolve().parent.parent
OUT = R / "analysis" / "out"
recs = list(csv.DictReader(open(R / "judge/judged.csv", encoding="utf-8")))
v10 = {(r["qid"], r["rec"]): r for r in csv.DictReader(open(R / "judge/judged_v10.csv", encoding="utf-8"))}
answers = list(csv.DictReader(open(R / "judge/answers.csv", encoding="utf-8")))
sample = {r["area_id"]: r for r in csv.DictReader(open(R / "sampling/sample.csv", encoding="utf-8"))}
raw = {}
for p in glob.glob(str(R / "collect/raw/S-search/*.jsonl")):
    for l in open(p, encoding="utf-8"):
        o = json.loads(l); raw[o["qid"]] = o
E = {}
# 1. 답마다 추천 수
for lg in ("ko", "en"):
    ns = [int(a["n_recs"]) for a in answers if a["lang"] == lg]
    E[f"recs_per_answer_{lg}"] = {"answers": len(ns), "recs": sum(ns), "mean": sum(ns) / len(ns),
                                  "full5": sum(1 for n in ns if n >= 5), "dist": dict(sorted(Counter(min(n, 5) for n in ns).items()))}
    rs = [r for r in recs if r["lang"] == lg]
    E[f"address_given_{lg}"] = {"k": sum(1 for r in rs if r["address"].strip()), "n": len(rs)}
    E[f"addr_outside_area_{lg}"] = {"k": sum(1 for r in rs if r["addr_in_area"] == "0"), "n": sum(1 for r in rs if r["addr_in_area"] in ("0", "1"))}
# 2. 2026 신설 구
new = [a for a, s in sample.items() if s["sigungu"].split()[-1] in ("검단구", "서해구", "영종구", "제물포구")]
E["new_districts"] = {}
for a in new:
    for lg in ("ko", "en"):
        rs = [r for r in recs if r["area_id"] == a and r["lang"] == lg]
        E["new_districts"][f"{sample[a]['sigungu']}|{lg}"] = {"recs": len(rs), "unverified": sum(1 for r in rs if r["loose_status"] == "미확인")}
# 3. 출처 도메인 (답 단위, 한 답에 같은 도메인은 한 번)
for lg in ("ko", "en"):
    c = Counter()
    for q, o in raw.items():
        if q.endswith("_" + lg):
            ds = {urlparse(u).netloc.lower().removeprefix("www.").removeprefix("m.") for u in o.get("sources", []) if u.startswith("http")}
            c.update(ds)
    E[f"top_domains_{lg}"] = c.most_common(10)
# 4. 폐업 추천의 폐업 경과(수집일 2026-11-14 기준, 가장 최근 폐업일)
yrs = []
for r in recs:
    if r["loose_status"] == "폐업":
        d = max(r["closed_dates"].split(";"))
        y, m = int(d[:4]), int(d[5:7])
        yrs.append(round((2026 * 12 + 11 - (y * 12 + m)) / 12, 1))
E["closed_years_since"] = sorted(yrs)
# 5. v1.0 -> v1.1 이동
E["v10_to_v11"] = dict(Counter((v10[(r["qid"], r["rec"])]["loose_status"], r["loose_status"]) for r in recs if (r["qid"], r["rec"]) in v10).most_common())
E["v10_to_v11"] = {f"{a}->{b}": n for (a, b), n in Counter((v10[(r["qid"], r["rec"])]["loose_status"], r["loose_status"]) for r in recs).items()}
(OUT / "explore.json").write_text(json.dumps(E, ensure_ascii=False, indent=1), encoding="utf-8")
with open(OUT / "summary.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["area_id", "stratum", "sigungu", "lang", "rec", "name_in_answer", "address_in_answer", "match", "status_v11", "status_v10", "status_strict_v11"])
    for r in recs:
        w.writerow([r["area_id"], r["stratum"], sample[r["area_id"]]["sigungu"], r["lang"], r["rec"], r["name"], r["address"], r["match"],
                    r["loose_status"], v10[(r["qid"], r["rec"])]["loose_status"], r["strict_status"]])
print(json.dumps({k: v for k, v in E.items() if not k.startswith("top")}, ensure_ascii=False)[:1500])
print(E["top_domains_ko"][:6]); print(E["top_domains_en"][:6])
