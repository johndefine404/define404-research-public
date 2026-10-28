# [Define404] 002 탐색 분석(사전 등록 아님): 메뉴명 줄 전체(괄호 안 포함)에 표준 이름이 들어 있는 비율.
# 등록 규칙은 괄호 안을 지우고 본 이름만 비교한다. 괄호 속 설명으로 표준을 같이 적은 답이 얼마나 되는지 따로 센다.
import csv, json, math, sys, unicodedata, re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "judge"))
import auto_judge as aj
ROOT = Path(__file__).resolve().parent.parent
def wilson(k, n, z=1.959964):
    if n == 0: return (0, 0)
    p = k / n; d = 1 + z*z/n; c = p + z*z/(2*n); h = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n))
    return ((c-h)/d, (c+h)/d)
def flat_en(s):
    s = unicodedata.normalize("NFKC", s).lower()
    s = re.sub(r"[^\w\s]", " ", s)
    return " ".join(s.split())
def flat_ja(s):
    s = unicodedata.normalize("NFKC", s)
    return re.sub(r"[\s・ー()（）]", "", s)
rows = list(csv.DictReader(open(ROOT / "judge" / "judged.csv", encoding="utf-8")))
out = []
for lg in ("en", "ja"):
    sub = [r for r in rows if r["lang"] == lg]
    f = flat_en if lg == "en" else flat_ja
    k = sum(1 for r in sub if f(r["standard"]) and f(r["standard"]) in f(r["candidate"]))
    lo, hi = wilson(k, len(sub))
    out.append({"lang": lg, "measure": "standard_in_name_line", "k": k, "n": len(sub), "rate": round(k/len(sub), 4), "ci_lo": round(lo, 4), "ci_hi": round(hi, 4)})
k = sum(1 for r in rows if r["cites_hansik"] == "1")
out.append({"lang": "all", "measure": "cites_hansik_or_kr", "k": k, "n": len(rows), "rate": round(k/len(rows), 4), "ci_lo": round(wilson(k, len(rows))[0], 4), "ci_hi": round(wilson(k, len(rows))[1], 4)})
w = csv.DictWriter(open(ROOT / "analysis" / "out" / "explore_contains.csv", "w", newline="", encoding="utf-8"), fieldnames=out[0].keys())
w.writeheader(); w.writerows(out)
for o in out: print(o)
