#!/usr/bin/env python3
# [Define404] 005 영업 행정 질문: 규칙 자동 판정 v1.1 (judge/rules.md 7절). 등록 규칙 v1.0은 auto_judge_v10.py
# 입력: sampling/sample.csv(정답), collect/raw/S-search/*.jsonl(답)
# 출력: judge/judged.csv
# 표준 라이브러리만 쓴다. LLM 판정자를 쓰지 않는다.

import csv
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

LIMIT_RE = re.compile(r"검색 한도|search limit|사용 한도|검색을 (할|수행할) 수 없")
PERIOD_KW = re.compile(r"처리|소요|걸|기간|기한|발급|완료")
PERIOD_TAIL = re.compile(r"^\s*(\(|[이가]\s*걸|[이가]\s*소요|이내|정도|안팎|가량|내외|소요|걸|이면|만에|안에|내에|까지|입니다|이에요|예요|이며|이고|로|으로|,|\.|$)")
FEE_KW = re.compile(r"수수료|비용|납부|요금|인지|금액|원이")
FEE_EXCL = re.compile(r"과태료|벌금|과징금|보험|자본금|교육비|보증금|등록면허세|면허세|세금|세액|기본세|부가가치세|부가세|인건비|임대료|시설비|월세|벌칙|채권|예치금|평가")
# v1.1: 거절 표현이 있는 문장의 값은 주장으로 세지 않는다
REJECT_RE = re.compile(r"적용되지 않|적용할 수 없|적용된다고 볼 수 없|아니어서|아니므로|아니라서|무관|쓰지 않|인용하지 않|참고하지 마|같다고 볼 수 없|근거로 쓰기 어렵|다른 업종|다른 절차|다른 제도|등록 수수료가 아닙|이 아닙니다|가 아닙니다")
HEDGE_RE = re.compile(r"확인하지 못|확인 못|확인되지 않|확인할 수 없|확인이 안|미확인|찾지 못")  # 탐색용 표시(판정에는 쓰지 않음, 2026-11-10 시범 20건 본 뒤 추가)
FREE_RE = re.compile(r"무료|수수료(는|가|도)?\s*(없|부과되지|받지|면제)|면제|비용(은|이)?\s*(들지|없)|(?<![\d,.])0\s*원")


def sentences(text):
    return [s for s in re.split(r"(?<=[.!?。])\s+|\n+", text) if s.strip()]


def period_claims(text):
    """답에서 처리기간 주장값을 모은다: '즉시' 또는 'N일'."""
    claims = set()
    for s in sentences(text):
        if not PERIOD_KW.search(s) or REJECT_RE.search(s):
            continue
        for m in re.finditer(r"(\d+)\s*주일?\s*(?:이내|정도|안팎|가량|내외|소요|걸)", s):  # v1.1: '1주일 이내' = 7일
            claims.add(f"{int(m.group(1)) * 7}일")
        if re.search(r"즉시|당일|바로 (처리|발급)|그 자리에서", s):
            claims.add("즉시")
        for m in re.finditer(r"(\d+)\s*시간", s):
            if int(m.group(1)) <= 8 and not re.search(r"\d+\s*시간\s*(이상|교육|이수)", s[m.start():m.end() + 6]):
                claims.add("즉시")
        for m in re.finditer(r"(\d+)\s*[~∼〜-]\s*(\d+)\s*(?:일|영업일|근무일|업무일)", s):  # 범위 표기 3~5일은 두 끝값을 다 센다
            claims.add(f"{int(m.group(1))}일")
            claims.add(f"{int(m.group(2))}일")
        for m in re.finditer(r"(\d+)\s*(?:일|영업일|근무일|업무일|working day)", s):
            before = s[max(0, m.start() - 3):m.start()]
            if re.search(r"월\s*$|\d{4}[.-]\s*$|\d\.\s*$", before):  # 날짜(11월 3일, 2026.11.3)는 뺀다
                continue
            if re.search(r"위생교육|교육|이수|영업\s*개시|개시\s*후|전까지|전에|이전|유효", s[max(0, m.start() - 15):m.end() + 12]) and not PERIOD_KW.search(s[max(0, m.start() - 12):m.start()]):
                continue
            tail = s[m.end():m.end() + 6]
            if not PERIOD_TAIL.search(tail) and not PERIOD_KW.search(s[max(0, m.start() - 20):m.start()]):
                continue
            claims.add(f"{int(m.group(1))}일")
    return claims


def fee_claims(text):
    """답에서 수수료 주장값을 모은다: '무료' 또는 'N원'."""
    claims = set()
    for s in sentences(text):
        if not FEE_KW.search(s) or REJECT_RE.search(s):
            continue
        # v1.1: 제외 낱말 뒤(25자 안)에 오는 금액 구간을 지운다
        s = re.sub(r"(" + FEE_EXCL.pattern + r")[^.;)]{0,25}?(\d[\d,.]*\s*(?:만\s*(?:\d+\s*천)?\s*)?(?:천\s*)?(?:백\s*)?원)", " ", s)
        if FREE_RE.search(s):
            claims.add("무료")
        for m in re.finditer(r"(\d+(?:\.\d+)?)\s*만\s*(?:(\d+)\s*천)?\s*원", s):
            v = float(m.group(1)) * 10000 + (int(m.group(2)) * 1000 if m.group(2) else 0)
            claims.add(f"{int(round(v))}원")
        s = re.sub(r"(\d+(?:\.\d+)?)\s*만\s*(?:(\d+)\s*천)?\s*원", " ", s)  # 이미 센 '만 원' 표기는 지운다
        for m in re.finditer(r"(?<![\d.,만])(\d{1,3}(?:,\d{3})+|\d+)\s*원", s):
            v = int(m.group(1).replace(",", ""))
            if v > 0:
                claims.add(f"{v}원")
            else:
                claims.add("무료")
        for m in re.finditer(r"(?<![\d만])(\d+)\s*천\s*원", s):
            claims.add(f"{int(m.group(1)) * 1000}원")
    return claims


def grade(claims, truth):
    if not claims:
        return "unknown", 0, 0
    loose = int(truth in claims)
    strict = int(claims == {truth})
    return ("correct" if loose else "wrong"), loose, strict


def main():
    truth = {r["qid"]: r for r in csv.DictReader(open(ROOT / "sampling" / "sample.csv", encoding="utf-8"))}
    answers = {}
    for f in sorted((ROOT / "collect" / "raw" / "S-search").glob("*.jsonl")):
        for line in f.read_text(encoding="utf-8").splitlines():
            if line.strip():
                a = json.loads(line)
                answers[a["qid"]] = a
    out = []
    for qid, t in truth.items():
        a = answers.get(qid)
        flags = []
        if a is None or not (a.get("answer") or "").strip():
            flags.append("empty")
            text = ""
        else:
            text = a["answer"]
            if int(a.get("searches") or 0) == 0 or LIMIT_RE.search(text):
                flags.append("invalid-no-search")
        pc, fc = period_claims(text), fee_claims(text)
        pv, pl, ps = grade(pc, t["period"])
        fv, fl, fs = grade(fc, t["fee"])
        out.append({"qid": qid, "city": t["city"], "pgroup": t["pgroup"], "paid": t["paid"],
                    "period_true": t["period"], "period_claims": "|".join(sorted(pc)), "period_verdict": pv,
                    "period_loose": pl, "period_strict": ps,
                    "fee_true": t["fee"], "fee_claims": "|".join(sorted(fc)), "fee_verdict": fv,
                    "fee_loose": fl, "fee_strict": fs,
                    "both_strict": int(ps and fs), "both_loose": int(pl and fl),
                    "hedged": int(bool(HEDGE_RE.search(text))),
                    "searches": (a or {}).get("searches", ""), "flags": "|".join(flags)})
    cols = list(out[0].keys())
    with open(HERE / "judged.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(out)
    n = sum(1 for r in out if not r["flags"])
    print(f"판정 {len(out)}건, 유효 {n}건, 무효·빈 답 {len(out) - n}건")


if __name__ == "__main__":
    main()
