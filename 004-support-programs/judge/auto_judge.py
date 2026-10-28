#!/usr/bin/env python3
# [Define404] 004 지원사업 질문: 규칙 자동 판정 (judge/rules.md v1.0)
# 입력: sampling/sample.csv, collect/raw/<시스템>/*.jsonl (한 줄 = {"qid","system","lang","answer","searches"(검색 횟수, 옛 이름 searched도 읽음),"ts"})
# 출력: judge/judged.csv (qid, system, status_claim, status_truth, status_ok, deadline, agency, loose, strict, flags)
# 표준 라이브러리만 쓴다. 정답 대조는 이 코드가 한다. LLM 판정자는 없다.

import csv
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

OPEN_PAT = re.compile(r"(신청\s*할\s*수\s*있|신청\s*가능|접수\s*중|진행\s*중|모집\s*중|신청하실\s*수\s*있|접수\s*가능|아직\s*신청)")
CLOSED_PAT = re.compile(r"(마감\s*되었|마감\s*됐|마감되어|마감이\s*되|종료\s*되었|종료\s*됐|종료되어|접수가\s*끝|이미\s*지났|지났습니다|신청\s*할\s*수\s*없|신청이\s*불가|신청\s*불가|접수가\s*종료|마감된\s*상태|마감입니다|마감됨|마감\s*상태)")
COND_PAT = re.compile(r"(다면|라면|경우에는|경우\s)")
DEADLINE_CTX = ["마감", "까지", "종료", "신청기간", "접수기간", "신청 기간", "접수 기간", "신청은", "접수는"]
AGENCY_SUFFIX = re.compile(r"[가-힣A-Za-z·()]+(기관|공단|진흥원|재단|센터|협회|시청|군청|구청|부|청|연구원|테크노파크|공사|위원회)")

ALIASES = {
    "소상공인시장진흥공단": ["소진공"],
    "중소벤처기업부": ["중기부"],
    "중소벤처기업진흥공단": ["중진공"],
    "한국산업기술진흥원": ["KIAT"],
    "창업진흥원": ["KISED"],
    "대한무역투자진흥공사": ["KOTRA", "코트라"],
    "한국무역협회": ["KITA"],
    "정보통신산업진흥원": ["NIPA"],
    "한국산업기술기획평가원": ["KEIT"],
    "중소기업기술정보진흥원": ["TIPA", "기정원"],
    "한국콘텐츠진흥원": ["KOCCA"],
    "한국농수산식품유통공사": ["aT"],
}

DATE_PATS = [
    (re.compile(r"(\d{4})[-./](\d{1,2})[-./](\d{1,2})"), lambda m: (int(m[1]), int(m[2]), int(m[3]))),
    (re.compile(r"(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일"), lambda m: (int(m[1]), int(m[2]), int(m[3]))),
    (re.compile(r"(?<![\d년])(\d{1,2})월\s*(\d{1,2})일"), lambda m: (2026, int(m[1]), int(m[2]))),
    (re.compile(r"(?<![\d.])(\d{1,2})\.(\d{1,2})\.(?!\d)"), lambda m: (2026, int(m[1]), int(m[2]))),
]


def norm(s):
    s = re.sub(r"\(재\)|\(사\)|재단법인|사단법인", "", s)
    return re.sub(r"[\s()·\-]", "", s)


def find_dates(text):
    out = []
    for pat, conv in DATE_PATS:
        for m in pat.finditer(text):
            try:
                y, mo, d = conv(m)
                if 1 <= mo <= 12 and 1 <= d <= 31:
                    out.append((f"{y:04d}-{mo:02d}-{d:02d}", m.start(), m.end()))
            except ValueError:
                pass
    return out


def judge_status(answer):
    sents = [s for s in re.split(r"(?<=[.!?。])\s+|\n+", answer) if s.strip()]
    last = None
    flag = ""
    for s in sents:
        o, c = bool(OPEN_PAT.search(s)), bool(CLOSED_PAT.search(s))
        if o and c:
            # 같은 문장에 둘 다: 조건문이면 건너뛰고, 아니면 허브 판정 대상
            if COND_PAT.search(s):
                continue
            last, flag = None, "manual-status"
            continue
        if o and not COND_PAT.search(s):
            last = "open"
        elif c and not COND_PAT.search(s):
            last = "closed"
    return (last or "unknown"), flag


def judge_deadline(answer, truth):
    dates = find_dates(answer)
    ctx_dates = []
    for d, s, e in dates:
        window = answer[max(0, s - 40):e + 40]
        before = answer[max(0, s - 10):s]
        if any(k in window for k in DEADLINE_CTX) or "~" in before or "부터" in before:
            ctx_dates.append(d)
    if not ctx_dates:
        return "none"
    return "correct" if truth in ctx_dates else "wrong"


def judge_agency(answer, row):
    names = []
    if row["agency"] in ("기초자치단체", "직접수행"):
        names.append(row["ministry"])
        m = re.match(r"\[[^\]]+\]\s*(\S+?(시|군|구))\b", row["title"])
        if m:
            names.append(m.group(1))
    else:
        names.append(row["agency"])
        names.append(row["ministry"])
    cands = []
    for n in names:
        cands.append(norm(n))
        cands += [norm(a) for a in ALIASES.get(n, [])]
    na = norm(answer)
    if any(c and c in na for c in cands):
        return "correct"
    if AGENCY_SUFFIX.search(answer):
        return "wrong"
    return "none"


def main():
    sample = {r["qid"]: r for r in csv.DictReader(open(ROOT / "sampling" / "sample.csv", encoding="utf-8"))}
    raw_dir = ROOT / "collect" / "raw"
    files = sorted(raw_dir.glob("*/*.jsonl")) if raw_dir.exists() else []
    if len(sys.argv) > 1:
        files = [Path(p) for p in sys.argv[1:]]
    rows = []
    for f in files:
        for line in open(f, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            r = sample.get(rec["qid"])
            if not r:
                continue
            ans = rec.get("answer") or ""
            flags = []
            if not ans.strip():
                flags.append("empty")
            if rec.get("searches", rec.get("searched", 1)) == 0 or re.search(r"검색\s*(한도|제한|를?\s*할 수 없)", ans):
                flags.append("invalid-no-search")
            claim, status_flag = judge_status(ans)
            if status_flag:
                flags.append(status_flag)
            truth = "open" if r["status"] == "ongoing" else "closed"
            dl = judge_deadline(ans, r["apply_end"])
            ag = judge_agency(ans, r)
            loose = int(dl == "correct")
            strict = int(dl == "correct" and claim == truth and ag != "wrong")
            rows.append({"qid": rec["qid"], "system": rec.get("system", f.parent.name), "status_claim": claim,
                         "status_truth": truth, "status_ok": int(claim == truth), "deadline": dl, "agency": ag,
                         "loose": loose, "strict": strict, "flags": ";".join(flags),
                         "status": r["status"], "jurisdiction": r["jurisdiction"], "ts": rec.get("ts", "")})
    out = HERE / "judged.csv"
    if rows:
        with open(out, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
    n_manual = sum("manual-status" in r["flags"] for r in rows)
    print(f"판정 {len(rows)}건, 허브 직접 판정 대상 {n_manual}건, 무효 {sum('invalid-no-search' in r['flags'] for r in rows)}건 -> {out}")


if __name__ == "__main__":
    main()
