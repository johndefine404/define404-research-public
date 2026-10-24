# Local404 사전 등록 편차 공지

- 연구: AI는 폐업한 동네 가게를 아직 영업 중이라고 말하는가 (Local404, Define404, 저자 김하원)
- 대상 사전 등록: prereg.md 버전 1.0 (2026-10-21), OSF 등록본
- 공지 작성일: 2026-10-24. 아래 변경은 모두 검색 조건 결과를 분석하기 전에 정했다.

## English summary

Decision made on 2026-10-24, before any analysis of search-condition results: the two web-search conditions (H-search = Claude Haiku 5.5 with web search, S-search = Claude Sonnet 5.5 with web search) are reduced from all 800 shops to a stratified random subsample of 100 shops x 5 languages (500 questions per condition). Reason: the web-search tool has a usage cap, and collecting the full 4,000 questions per condition would take more than 35 hours of capped throughput. The subsample was drawn with fixed seed 20261024, proportionally on the 8 preregistered strata (open/closed x Kakao-registered/not x metropolitan/province; 12 or 13 shops per stratum, exactly 50 open and 50 closed). The memory conditions (H-mem, L-mem) remain at all 800 shops; the H3 paired comparison (H-search vs H-mem) uses the same 100 shops for both. Consequence: lower power for search-condition analyses, especially H4 (closed shops only, about 50 shops). The preregistered files (prereg.md, sample_v2.csv and their hashes) are unchanged. Other deviations are listed below: W-mem replaced by L-mem; re-collection of search-limit-invalidated answers (batch size 25 to 10); re-collection of language-drifted answers; LLM-assisted judging with Claude Sonnet (the rules file named Claude Haiku); the Claude conditions received a common instruction (including "Answer honestly. If you cannot confirm something, say so.") while L-mem received only the question, so Claude-vs-Llama differences confound model and instruction; H5 is excluded from the Holm correction because no p-value is defined at a null rate of 0 (decided by the confidence-interval lower bound); the H4 mixed-effects logistic model uses an own Gauss-Hermite maximum-likelihood implementation (checked by simulation recovery and a statsmodels Logit cross-check). Per preregistration section 8, dictionary-only judging results (no LLM labels) are reported in the manuscript appendix D.

## 1. 이번 편차: 검색 2조건 부표본

| 항목 | 사전 등록 | 변경 |
|---|---|---|
| H-search, S-search 대상 | 800곳 x 5언어 = 4,000문항 | 100곳 x 5언어 = 500문항 (층화 무작위 부표본) |
| H-mem, L-mem(사전 등록 W-mem 대체) 대상 | 800곳 x 5언어 | 변경 없음 (800곳 전부) |

- 결정일: 2026-10-24. 검색 조건 결과를 분석하기 전이다.
- 사유: 웹 검색 도구에 사용 한도가 있다. 1차 수집에서 한도로 검색 없이 답한 문항이 무효가 되었고, 재수집 속도(시간당 약 200회 남짓)로 전수(조건당 4,000문항)를 채우려면 35시간 이상 걸린다.
- 추출: sampling/sample_v2.csv의 800곳에서, 사전 등록 8층(영업상태 x 카카오 등록 x 지역; 층마다 100곳)에 비례해 배분하고 최대잉여법을 썼다. 100/8 = 12.5라서 층마다 12곳 + 나머지 4곳을 더 배정했다. 영업 400 대 폐업 400 비율을 지키려고 영업 쪽 2층과 폐업 쪽 2층에 한 곳씩 더 주었다(동률은 시드로 가름). 층 안에서는 item_id 정렬 뒤 시드 20261024로 섞어 앞에서부터 뽑았다. 결정적이며 코드로 재현된다.
- 결과 배분: 영업|카카오없음|광역 13, 영업|카카오없음|도 13, 영업|카카오있음|광역 12, 영업|카카오있음|도 12, 폐업|카카오없음|광역 12, 폐업|카카오없음|도 12, 폐업|카카오있음|광역 13, 폐업|카카오있음|도 13. 영업 50·폐업 50, 광역 50·도 50, 카카오 있음 50·없음 50.
- 파일: sampling/subsample_search.py (코드), sampling/subsample_search_v1.csv (가게 100곳), sampling/subsample_search_v1.sha256 (SHA256: bf4d552a240718610ae1053f6c9ad1ecdbd03fa80b1fa67d0376ac22c40b4d23).
- 사전 등록 파일은 바꾸지 않았다: prereg.md, prereg.sha256, REGISTERED_FILES.sha256, sampling/sample_v2.csv는 그대로다.

### 분석에 미치는 영향

- 검색 조건의 확증 분석(H1~H5 중 검색 조건 부분)은 부표본 100곳만 쓴다. 이미 모인 부표본 밖 가게의 검색 답은 분석하지 않는다.
- H3(H-search 대 H-mem): 같은 100곳, 같은 (가게, 언어) 짝으로 비교한다. H-mem·L-mem만 쓰는 분석(H1·H2·H4·H5의 기억 조건 부분)은 800곳 전부.
- 검정력이 낮아진다. 특히 H4(폐업 가게 하위 표본)는 검색 조건에서 폐업 가게가 약 50곳뿐이라 "영업 중" 오답과 폐업 뒤 기간의 관계를 검정하기 어렵다. 검색 조건 언어별 칸은 가게 100곳(영업 50·폐업 50)이라 신뢰구간이 넓고, 표본 40 미만 칸은 해석하지 않는다는 사전 등록 규칙은 그대로다. 결과 보고에서 검색 조건의 한계로 밝힌다.
- 종합 모형은 검색 조건(100곳)과 기억 조건(800곳)의 가게 구성이 달라 해석에 주의한다.

## 2. 앞서 기록한 다른 편차 (참고, HANDOFF 7절과 같음)

1. W-mem(Cloudflare Workers AI) 대신 L-mem(같은 모델 가중치, 로컬 Ollama q8_0)으로 실행 경로를 바꿨다. 이유: 무료 한도. 수집 기기가 맥에서 윈도우로 바뀌는 점도 방법 절에 적는다.
2. 검색 조건 재수집: 한도로 무효가 된 문항을 다른 시간대에 다시 받았다. 배치 크기 25 → 10, 지시문에 문항별 검색 필수를 추가.
3. 시범 수집 80답(4곳)은 분석에서 뺀다(사전 등록 문구대로).
4. 검색 한도 문구 답변을 무효로 재분류했다: searches가 1 이상이어도 본문이 검색 한도·미실행을 말하는 답은 무효로 보고 다시 받는다(판정식 analysis/load_data.py LIMIT_RE). 원본은 그대로 두고 재수집 답이 유효하면 그것을 쓴다.
5. 언어 이탈 답변을 무효로 재분류했다(2026-10-24): 질문 언어가 아닌 문자 체계로 쓰인 검색 조건 답은 무효로 보고 질문 언어를 명시한 지시문으로 다시 받는다. 부표본 일본어 100문항 중 재수집 시점에 유효 답이 한국어였던 54문항(가나 없이 한글)이 대상이었다. 원인은 수집 에이전트가 Claude Code 환경에서 돌아 사용자 수준 메모리('한국어로만 답하라')의 영향을 받은 것이다. 판정식은 analysis/load_data.py script_ok(ja: 가나 있음, zh: 한자 있고 한글 우세 아님, ko: 한글 있음, en·vi: 라틴 글자 우세이고 한글 우세 아님). 원본 raw는 그대로 두고, 재수집 답이 유효하면 그것을 쓴다(재수집 배치 H-search_ja_r091~r096은 이 54문항을 담았고 지금은 모두 유효한 답이다. 지시문에 답변 언어 명시 추가). 최종 엄격 기준의 H-search 일본어 집합에서 언어 이탈 답은 0건이다.
6. LLM 보조 판정 추가(2026-10-24): 판정 규칙(judge/rules.md 5절)은 다국어 표현 사전과 Claude Haiku 보조 분류로 자동 판정한다고 적었다. 사전이 확정하지 못하는 답은 미판정으로 남는데, 실제 보조 분류는 Haiku가 아니라 Claude Sonnet이 규칙 원문과 질문, 답만 보고 영업 상태·주소·업종을 분류하는 방식으로 수행했다(analysis/llm_judge/, 15개 배치 J001~J015, 1,437항목, 병합 라벨 1,418개). 판정자는 정답과 응답 시스템을 보지 못하고 정답 대조는 코드가 한다. 보조 판정이 최종 판정에 쓰인 답은 492건(H-mem 214, H-search 171, S-search 107)이며 L-mem에는 아직 적용하지 않았다. 한계: 판정자가 응답자와 같은 모델 계열(Claude)이라 계열 편향 가능성이 있고, 사전 판정(사전 등록 이후 작성, analysis/auto_judge.py)과 보조 판정 모두 사람 2인 판정과 코헨 카파로 검증하기 전이다. 판정 코드는 judge/ 폴더가 아니라 analysis/auto_judge.py에 두었다(judge/ 폴더 수정 금지). 사전 등록 8절에 따라 보조 판정을 쓰지 않은 사전 판정 단독 결과를 별도로 냈다(analysis/out_dictonly/, 원고 부록 D). 사전 판정만 쓰면 Claude 세 조건의 영업 상태 단정은 0건이고(원고의 유일한 단정 1건은 보조 판정으로 해소된 답) H5는 어느 시스템에서도 지지되지 않는다.
7. 응답자 입력(지시문) 차이(기록 2026-10-24): Claude 세 조건(H-mem, H-search, S-search)의 응답자는 collect/collect_claude.workflow.js의 공통 지시문을 받았다. 평범한 AI 비서로서 질문과 같은 언어로 답하고, 문항마다 별개의 대화로 다루며, "Answer honestly. If you cannot confirm something, say so."라는 문구와 도구 규칙(기억 조건은 도구 금지, 검색 조건은 문항마다 검색)을 포함한다. 한 응답자가 질문 10~25개를 맡았다. 반면 L-mem(collect/run_lmem.py)은 Ollama /api/chat에 질문 문장 하나만 사용자 메시지로 보내며 시스템 프롬프트와 지시문이 없고 질문마다 독립 호출이다(옵션은 최대 300토큰과 seed 20261021뿐). 사전 등록은 시스템 간 동일한 지시문을 규정하지 않았으나 collect/PROTOCOL.md는 응답자가 질문 문장만 받는다고 했으므로 이 차이를 편차로 기록한다. 효과: Claude 계열과 Llama의 차이에 모델과 지시문, 호출 방식(배치 대 단건) 차이가 섞여 있어 순수한 모델 차이로 읽을 수 없다. 이 효과를 분리하는 대조 수집은 하지 않았다. 원고 2.3절, 논의, 한계 h에 적는다. Ollama 모델 파일에 내장된 기본 템플릿이나 시스템 문구는 이 점검에서 확인하지 못했다.
8. H5를 Holm 보정에서 제외(2026-10-24, 분석 코드 작성 시): H5의 귀무가설은 불일치 비율 0이라 p값이 정의되지 않는다. H5는 Holm 입력에서 빼고 신뢰구간 하한이 0을 넘는지로 판단한다(analysis/README.md A8). 나머지 검정(H1~H4)은 Holm 보정한다.
9. H4의 혼합효과 로지스틱 직접 구현(2026-10-24, 분석 코드 작성 시): 사전 등록은 가게 무작위 절편을 둔 혼합효과 로지스틱을 정했으나 구현은 정하지 않았다. statsmodels 대신 가우스-에르미트 구적 최대우도를 직접 구현했고(analysis/stats_lib.py fit_glmm_logit), 시뮬레이션 복원 검사와 statsmodels Logit 교차 검사로 점검했다(analysis/tests/test_stats_lib.py). 사건이 10 미만이거나 분리면 추정치를 내지 않는다(analysis/README.md A9).
10. 판정 신뢰도 평가 방식 변경(2026-10-24): 사전 등록의 사람 2인 판정(200건)을 서로 다른 두 LLM 판정자 간 일치도 평가로 변경했다. 주 판정은 Claude Sonnet(사전 판정과 결합), 독립 판정은 별도 문구의 Claude Haiku가 하며, 200답 표본에서 필드별 코헨 카파와 부트스트랩 신뢰구간을 보고한다(analysis/llm_judge/rater_b.workflow.js).

### 방법의 한계: 수집 환경

- 수집 에이전트(H-search, S-search, H-mem)는 Claude Code 환경 안에서 실행되었고, 이 환경은 사용자 수준 설정·메모리(예: 한국어로만 답하라)를 함께 싣는다. 순수한 API 호출과 같은 조건이 아니다. 언어 이탈은 위 5번처럼 검사해 거르고 재수집했지만, 설정·메모리가 답의 내용(말투, 단서 문구, 확신 정도)에 미친 영향은 따로 검사하지 못했다. 방법 절과 한계 절에 적는다.
- 같은 검사에서 H-mem 일본어 배치 H-mem_ja_001(200답)도 전부 한글이다. 결정(2026-10-24): H-mem_ja_001 200답도 답변 언어를 명시한 지시문으로 재수집한다(Haiku, 도구 없음, 원래 프로토콜과 같고 언어 지시만 추가, 20문항 x 10배치로 나눔). 원본 파일은 기록으로 두고 분석에서는 한글 답을 빼며 재수집 답이 유효하면 그것을 쓴다.

## 3. 확인 방법

- 저장소: johndefine404/define404-research (비공개) 001-local404/. 이 편차 결정의 커밋 기록과 위 파일의 해시로 사후에 검증할 수 있다.
- 부표본 파일 해시를 다시 계산하려면 `sha256sum sampling/subsample_search_v1.csv`. 코드를 다시 돌리면(`python sampling/subsample_search.py`) 같은 목록이 나오는지 확인만 하고 파일을 덮어쓰지 않는다.
