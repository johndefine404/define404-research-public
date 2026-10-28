# Define404 Research 공개 자료

[Define404]

Define404 Research 리포트의 분석 코드와 결과 자료예요. 리포트 본문은 https://define404.com/report/ 에 있어요.

## 001-local404

리포트 2호 "Local404: AI는 폐업한 동네 가게를 아직 영업 중이라고 말하는가"(2026-10-24)의 자료예요.

- 사전등록: OSF https://osf.io/5qnxu
- 원고(한국어 기준본): `001-local404/report/local404_ko.md`
- 사전등록 원문과 변경 공지: `001-local404/prereg.md`, `001-local404/DEVIATIONS.md`
- 판정 규칙: `001-local404/judge/rules.md`
- 분석 코드: `001-local404/analysis/` (`run_analysis.py`, `load_data.py`, `auto_judge.py`, `stats_lib.py`)
- 분석 결과: `001-local404/analysis/out_final/` (가설별 표, 답별 판정 `judgments.csv`, `results.json`)
- 그림: `001-local404/report/figures/` (`analysis/make_figures.py`가 `out_final` 결과에서 다시 만들어요)
- 수집 절차: `001-local404/collect/` (질문 틀, 수집 스크립트)
- 표본: `001-local404/sampling/` (추출 코드, 상호·주소를 뺀 표본 `sample_v2_public.csv`, 검색 부표본 목록)

### 리포트에 적힌 해시와 대조

| 파일 | SHA-256 |
|---|---|
| `prereg.md` | 87be279e17ebc0922ca079845ea3959ee04ca1379033f7b2c5e5fd8a21abc02b |
| `judge/rules.md` | a4ddb1efe5bd50c8d74e64a9678773646c9d05da0af73e749bf3f55f79386209 |
| `analysis/out_final/results.json` | f9a4dbdcf88ac7aff3e32d13cea971ddbaa224332fbcaa176f995c6a79ea6123 |
| `sampling/sample_v2_public.csv` (공개본) | e4d465b9c39aed50958e5b65807a8f352358f737adcf2459a714dced51296af8 |

### 공개하지 않은 것

개인사업자의 상호와 주소가 들어 있는 파일은 올리지 않았어요.

- 원 표본 `sampling/sample_v2.csv`(상호, 주소, 관리번호, 카카오 장소 번호 포함). 공개본은 가게 번호(item_id)와 층, 영업 상태, 날짜, 시군구, 업태만 남겼어요. 원 표본의 SHA-256은 리포트에 적혀 있어요.
- 질문 묶음과 AI 답변 원문(`collect/batches*`, `collect/raw*`). 질문과 답에 상호와 주소가 들어 있어요.
- LLM 보조 판정 입력(`analysis/llm_judge/in/`)과 사람 판정용 시트, 검토 대기열.
- LLM 보조 판정 결과의 메모 칸과 AI가 말한 주소 칸은 비우거나 가렸어요. 맞음·틀림 판정 결과는 `judgments.csv`에 그대로 있어요.

그래서 이 저장소만으로는 분석을 처음부터 다시 돌릴 수 없어요. 연구 목적으로 원자료가 필요하면 john@define404.com 으로 연락해 주세요.

### 원자료 출처

정답 원천은 행정안전부 지방행정 인허가 데이터 "식품_일반음식점"(file.localdata.go.kr, 2026-10-21 수신)이에요.

## 인용

Define404 Research (2026). Local404: AI는 폐업한 동네 가게를 아직 영업 중이라고 말하는가. https://define404.com/report/002-local404-closed-shops/

## 이용 조건

- 코드: MIT License
- 자료와 원고: CC BY 4.0 (출처를 밝히면 자유롭게 쓸 수 있어요)

## 003-local404-consistency

리포트 3호 "같은 가게, 5개 언어 답의 일관성"(2026-10-28, 데이터 노트)의 자료예요. 2호 판정 결과 `001-local404/analysis/out_final/judgments.csv`를 입력으로 써요.

- 사전등록: 연구 저장소 커밋 7169864(2026-10-28 23:39 ICT), 원문 `003-local404-consistency/prereg.md`
- 원고: `003-local404-consistency/report/consistency_ko.md`
- 분석 코드와 결과: `003-local404-consistency/analysis/` (`run_analysis.py`, `out/`)

## 002-menu-translation

리포트 4호 "AI에게 한식 메뉴의 외국어 이름을 물으면 정부 표준과 얼마나 같을까"(2026-10-29)의 자료예요.

- 사전등록: 연구 저장소 커밋 9f84ace(2026-10-28 23:41 ICT), 원문 `002-menu-translation/prereg.md`
- 원고: `002-menu-translation/report/menu_ko.md`
- 표본 추출·질문·판정·분석 코드, 결과 파일, 메뉴별 판정(`judge/judged_public.csv`)
- 공개하지 않은 것: 한식진흥원 표준 표기 원천 표와 표준 문자열(저작권은 한식진흥원), AI 답 원문. 원천 표는 `sampling/fetch_source.py`로 받을 수 있고 해시는 `sampling/SHA256SUMS`에 있어요.

## 004-support-programs

리포트 5호 "AI에게 지원사업 공고를 물으면 마감일을 맞게 알려 줄까요"(2026-10-29)의 자료예요.

- 사전등록: 연구 저장소 커밋 35fac08(2026-10-28 23:41 ICT), 원문 `004-support-programs/prereg.md`
- 원고: `004-support-programs/report/support_ko.md`
- 판정 규칙 개정: 신청 가능 여부 판정을 수집 뒤 v1.1로 고쳤어요(`judge/rules.md` 7절). v1.0 결과는 `judge/judged_v10.csv`, `analysis/out_v10/`에 그대로 있어요.
- 표본(기업마당 공개 공고 목록), 판정 결과, 분석 코드. AI 답 원문은 공개하지 않아요.
