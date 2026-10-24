# 최종 실행 절차 (L-mem 수집 완료 후)

작업 폴더: `C:\Dev\define404-research\001-local404`. 판정 호출([ ] 표시)만 오케스트레이터가 Workflow로 돌리고, 나머지는 로컬 파이썬이다.

(a) 수집 점검: L-mem 4,000 유효 답과 언어 이탈(drift)이 없는지 확인한다.
`python analysis/load_data.py`  (L-mem valid 4000/4000, lang_drift 보고 확인; 미달이면 중단)

(b) 주 판정 입력 추가: L-mem 사전 미확정(review) 답 전부 + 무작위 200답 + 판정자 B 표본 200답이 J016 이후 배치로 붙는다. 먼저 `--dry`로 개수 확인.
`python analysis/llm_judge/build_inputs.py --include-lmem --dry`
`python analysis/llm_judge/build_inputs.py --include-lmem`   (출력의 new_batches 와 마지막 배치 번호 N 을 기록)

(c) [오케스트레이터가 실행] `analysis/llm_judge/judge.workflow.js`. 기존 J001~J015는 건너뛴다.
args: `{"dir":"C:/Dev/define404-research/001-local404/analysis/llm_judge","from":16,"count":<N>,"sizes":{"J016":<n>,...}}`
(sizes는 in/MANIFEST.json 의 n; 생략 가능, 최종 검증은 merge.py)

(d) 병합·검증: `python analysis/llm_judge/merge.py` (문제 0건이어야 한다. llm_labels.jsonl 갱신)

(e) 판정자 B 입력(최종 풀에서 200답, L-mem 4,000 미만이면 거부):
`python analysis/llm_judge/build_rater_b.py --dry` 후 `python analysis/llm_judge/build_rater_b.py`
→ in_b/B001.jsonl, B002.jsonl, rater_b_key.jsonl(비공개 열쇠)

(f) [오케스트레이터가 실행] `analysis/llm_judge/rater_b.workflow.js` (Haiku)
args: `{"dir":"C:/Dev/define404-research/001-local404/analysis/llm_judge","count":2,"sizes":{"B001":100,"B002":100}}`
출력: out_b/B001.jsonl, B002.jsonl

(g) 확정 분석: `python analysis/run_analysis.py --final --rater-b`  → analysis/out_final/
- 거부 조건: 4개 시스템 중 하나라도 유효 답 미달, 미판정(review) 1건 이상(목록은 out_final/unresolved_items.csv), 판정자 B 출력 누락·무효·표본 불일치.
- 미판정이 남으면 그 항목만 build_inputs.py 로 다시 붙여 (c)(d) 반복한다. 통과시키지 않는다.
- 산출: kappa_rater_b.csv(필드별 카파+부트스트랩 CI; B 대 주 판정, B 대 Sonnet 단독), results.json 의 rater_b 항목.
