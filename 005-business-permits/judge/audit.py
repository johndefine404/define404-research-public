#!/usr/bin/env python3
# [Define404] 005 판정 규칙 검수: 허브가 답 원문을 읽고 적은 주장값(사람 판독)과 규칙 추출값을 대조한다.
# dev 30건은 v1.0 결함을 찾는 데 썼고(그래서 v1.1 평가에 쓰지 않는다), validation 30건으로 v1.1을 잰다.
# 사람 판독은 정답을 보지 않고 답 원문만 읽고 적었다. 아래 MANUAL에 없는 qid는 사람 판독이 규칙 추출값과 같다.
import csv, json
from pathlib import Path
HERE = Path(__file__).resolve().parent
MANUAL = {  # validation 표본 중 규칙 추출값과 사람 판독이 다른 답 (qid: (처리기간, 수수료))
    "B129": ({"10일"}, set()),        # '면제 여부는 확인하지 못했습니다'를 무료로 읽음
    "B173": (set(), set()),           # 변경신고 기한 '30일 이내'를 처리기간으로 읽음
    "B141": ({"3일"}, {"10000원"}),   # 변경·폐업 신고 값(5,000원, 수수료 없음)까지 셈
    "B038": ({"3일"}, {"25200원", "28000원"}),  # '3일, 28,000원' 의 3일을 놓침
    "B030": ({"14일"}, set()),        # '약 2주가 걸리고'를 놓침
    "B075": ({"15일"}, {"30000원"}),  # 업종 이름 '무료직업소개'를 무료로 읽음
    "B021": (set(), set()),           # 재교부 수수료라고 스스로 배제한 금액을 셈
    "B023": (set(), set()),           # 다른 업무라 적용할 수 없다고 한 7일을 셈
}


def grade(claims, truth):
    if not claims:
        return "unknown"
    return "correct" if truth in claims else "wrong"


def main():
    sample = json.loads((HERE / "audit_sample.json").read_text())
    rows = {r["qid"]: r for r in csv.DictReader(open(HERE / "judged.csv", encoding="utf-8"))}
    n_ans = len(sample["validation"])
    err_ans, cells, changed = 0, 0, 0
    for q in sample["validation"]:
        r = rows[q]
        rule_p = set(filter(None, r["period_claims"].split("|")))
        rule_f = set(filter(None, r["fee_claims"].split("|")))
        man_p, man_f = MANUAL.get(q, (rule_p, rule_f))
        if (man_p, man_f) != (rule_p, rule_f):
            err_ans += 1
        for man, rule, truth in ((man_p, rule_p, r["period_true"]), (man_f, rule_f, r["fee_true"])):
            cells += 1
            if grade(man, truth) != grade(rule, truth):
                changed += 1
    out = {"rule_version": "1.1", "n_answers": n_ans, "answers_with_extraction_error": err_ans,
           "verdict_cells": cells, "verdict_cells_changed": changed, "dev_v10_answers_with_error": 10, "dev_n": 30}
    (HERE / "audit_result.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
    print(out)


if __name__ == "__main__":
    main()
