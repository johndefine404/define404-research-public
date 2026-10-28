# [Define404] 004 판정 규칙 v1.1 (신청 가능 여부만): 첫 문장의 결론 방향으로 판정한다.
# v1.0 구현은 "신청 가능성은 사실상 없어 보입니다"를 가능으로, 지난 회차 마감 언급을 마감으로 읽었다(judge/rules.md 7절).
# 입력 judge/judged_v10.csv + collect/raw, 출력 judge/judged.csv(status_claim·status_ok·strict만 바꿈)
import csv, glob, json, re
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
NEG = re.compile(r"(신청\s*할\s*수\s*없|신청하기\s*어려|신청이\s*어렵|신청\s*하기\s*어렵|마감(?!일|\s*\d)|끝난|끝났|종료|지났|아니요|가능성은\s*(사실상\s*)?없)")
POS = re.compile(r"(신청\s*가능(?!\s*여부)|신청이\s*가능|신청할\s*수\s*있(?!는지)|신청하실\s*수\s*있|접수\s*중|열려\s*있)")
def first(ans):
    return re.split(r"(?<=[.!?])\s+", ans.strip())[0]
def claim(ans):
    s = first(ans)
    if NEG.search(s):
        return "closed"
    if POS.search(s):
        return "open"
    return "unknown"
ans = {}
for f in glob.glob(str(ROOT / "collect/raw/*/*.jsonl")):
    for l in open(f, encoding="utf-8"):
        r = json.loads(l); ans[r["qid"]] = r["answer"]
rows = list(csv.DictReader(open(ROOT / "judge/judged_v10.csv", encoding="utf-8")))
for r in rows:
    c = claim(ans[r["qid"]])
    r["status_claim"] = c
    r["status_ok"] = "1" if c == r["status_truth"] else "0"
    r["strict"] = "1" if (r["loose"] == "1" and r["status_ok"] == "1" and r["agency"] != "wrong") else "0"
w = csv.DictWriter(open(ROOT / "judge/judged.csv", "w", newline="", encoding="utf-8"), fieldnames=rows[0].keys())
w.writeheader(); w.writerows(rows)
from collections import Counter
print(Counter((r["status_truth"], r["status_claim"]) for r in rows))
