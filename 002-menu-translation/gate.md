# 주제 게이트 점검: 메뉴 번역 (AI의 한식 메뉴 외국어 표기 오류)

점검일 2026-10-28 (ICT). 스킬 3절 0~6번. 결과: 통과 (6번은 탈락 사유 아님). 아래 "사람이 정할 것" 2건은 사전 등록 커밋 전에 결정이 필요하다.

## 0. 갈래

- 소상공인과 AI. 가게 사장님이 AI에 메뉴 외국어 이름을 물었을 때 정부 표준과 얼마나 다른 답을 받는지 측정한다. 통과.

## 1. 정답을 공개 자료로 객관적으로 정할 수 있는가

- 원천: 한식진흥원 한식포털 "한식메뉴 외국어 표기법"(한식메뉴 외국어표기법 길라잡이 800선). 주소 https://www.hansik.or.kr/board/dn/list/017?menuSn=12
- 2026-10-28 확인 내용: 공개 HTML 표, 로그인 없음, 전체 778건, 열 = 번호·요리명·Latina(로마자)·English·日本語·中文(简体)·中文(繁體). 50건씩 16페이지(GET 인자 curPage·rowSize)로 기계 수집 가능. 상세 페이지(bbsSeq)에 5개 언어 설명문이 있으나 받지 않았다. 출처 표기: 농림축산식품부 / 한식진흥원 / 문화체육관광부 / 국립국어원 / 한국관광공사 / 농촌진흥청.
- 받은 파일: sampling/raw/hansik_menu_800_20261028.csv (778행, 빈 칸 0, 요리명 중복 0, 영어 표기 중복 28쌍). SHA256 620f0fc8be6918a7a5482e66f86086bf7991505bb679e046d28fa837bf4cc26f (sampling/raw/SHA256SUMS). 수집 코드 sampling/fetch_source.py.
- 한계: 표준이 "유일한 정답"은 아니다. 표준과 다르다고 해서 틀린 번역은 아니며, 이 편이 재는 것은 "정부 표준 표기와의 일치"다. 원고 제목·본문에 이 뜻을 분명히 적는다. 통과.
- 저작권: 한식포털 저작권정책(https://www.hansik.or.kr/contents/contentsDetail.do?cntntsSeq=27&menuSn=115, 2026-10-28 확인)은 자료의 저작권이 한식진흥원에 있고 수익 목적 이용은 사전 협의, 출처 표시 필수라고 적는다. 공공누리 표시는 없다. 공공데이터포털에는 이 표가 올라 있지 않다(2026-10-28 검색, 한식진흥원 제공 파일은 정밀레시피뿐).

## 2. 남이 같은 방법으로 다시 해 볼 수 있는가

- 원천 수집 코드, 시드 고정 추출 코드, 질문 틀, 배치, 규칙 판정 코드, 분석 코드를 전부 공개한다. 원천 표는 재배포하지 않고 수집 코드와 해시로 재현한다(저작권 결정 전 기본값). 통과.

## 3. 기존 연구의 빈자리 (원문을 연 것만, 확인일 2026-10-28)

- Yao, Jiang, Bobinac, Yang, Hu. Benchmarking Machine Translation with Cultural Awareness. arXiv 2305.14328 (v3 2024-10-19). https://arxiv.org/abs/2305.14328 : 문화 특정 항목(CSI) 주석 병렬 말뭉치 6개 언어쌍, CSI 번역 지표 2개 제안, LLM이 신경망 기계번역보다 CSI 번역에 외부 문화 지식을 잘 쓴다는 결과. 한식 메뉴 전용은 아니다.
- Zhang, He, Iyer, Birch. Cultural Adaptation of Menus: A Fine-Grained Approach. arXiv 2408.13534 (2024-08-24, WMT 2024). https://arxiv.org/abs/2408.13534 : 중국어-영어 메뉴 데이터셋 ChineseMenuCSI, CSI 자동 식별과 번역 전략, COMET 최대 7점 향상. 중국어 메뉴만 다룬다.
- Yuan 외. Culture-Aware Machine Translation in Large Language Models: Benchmarking and Investigation. arXiv 2604.24361 (2026-04-27, ACL 2026 본회의). https://arxiv.org/abs/2604.24361 : 소설 기반 문화 인식 번역 데이터셋 CanMT, 다차원 평가 틀, LLM 판정자 신뢰도. 한국어 포함 여부는 초록에 없다.
- Zeng 외. CulturalMenuBench: Probing the Knowledge-Application Gap in Multimodal Culinary Reasoning. arXiv 2609.03526 (2026-09-03). https://arxiv.org/abs/2609.03526 : 메뉴·조리 이미지 4,870문항, 10개 언어, 12개 멀티모달 모델, 객관식 평가. 번역 정답을 정부 표준과 대조하지 않는다.
- Lee, Jeong-Hwa. A Comparative Study of ChatGPT and Papago Korean-to-English Translations of Dialogue from the Adaptation of Pachinko. International Journal of Contents 21(3), 2025, 138-151. https://www.accesson.kr/ijcon/v.21/3/138/57464 : 드라마 대사 590쌍, ChatGPT 58.1% 대 파파고 37.8% 정확. 음식명이 아니다.
- 빈자리: 한식 메뉴명을 정부 공식 표준(길라잡이 800선)과 대조해 AI 비서(웹 검색 조건)의 표기 일치율을 잰 연구는 위 5편 어디에도 없다. 통과.

## 4. 한 줄로 인용할 숫자

- "AI 비서에 한식 메뉴 180개의 영어 메뉴명을 물었더니 정부 표준 표기와 똑같이 답한 비율은 N% (95% 신뢰구간 a~b)" 와 "일본어는 M%". 통과.

## 5. 무료 한도 안에서 표본을 채울 수 있는가

- 표본 180 메뉴 x 2개 언어 x 1개 시스템 = 360문항, 10문항 배치 36개. 응답자는 Claude Sonnet 하위 에이전트(웹 검색), 구독 안에서 돈다.
- 1편 실측: 웹 검색 한도는 약 1,228회 뒤 바닥, 이후 회복 시간당 약 200회. 360문항은 문항마다 검색 1~2회로 잡아 최대 약 720회, 한 번의 한도 안이거나 회복 2~3시간 안이다. 3배치씩 병렬. 통과.

## 6. Define404 사업과 이어지는가

- 가게냥 점검 항목 후보: "메뉴판 외국어 표기가 정부 표준과 맞는지". 대행사가 고객에게 보여 줄 숫자: 언어별 일치율. 이어진다.

## 사람이 정할 것 (사전 등록 커밋 전)

1. 원천 표 재배포 범위. 기본값은 "재배포 안 함, 수집 코드·해시·링크(bbsSeq)만 공개, 결과 파일에는 메뉴 번호와 우리 판정만". 표본 180개의 표준 표기 문자열을 결과 파일에 함께 싣고 싶으면 한식진흥원(한식확산팀 02-6320-8451)에 연구 인용 범위를 문의해야 한다.
2. 언어 2개(영어·일본어) 확정. 중국어(간체)는 표준에 있지만 간체·번체·표기 변형 때문에 규칙 판정이 거칠어져 뺐다. 영어 1개만으로 줄이면 1차 가설을 언어 비교가 아닌 다른 것으로 바꿔야 한다.
