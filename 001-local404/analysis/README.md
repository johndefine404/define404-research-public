# analysis/ : 사전 등록 분석 파이프라인

수집이 끝나면 바로 돌리도록 만든 코드. 모델·검색·네트워크를 부르지 않는다. collect/, sampling/, judge/, prereg 는 읽기만 한다.

## 실행

```
pip install -r analysis/requirements.txt      # numpy, pandas, scipy
python analysis/tests/test_stats_lib.py       # 통계 도구 자체 점검 (알려진 답이 있는 장난감 입력)
python analysis/run_analysis.py --dryrun      # 시험 실행 -> analysis/out_dryrun/  (DRYRUN_NOT_FOR_PUBLICATION.txt 포함). 공개본은 --out analysis/out_final 로 쓴다
python analysis/run_analysis.py --final       # 확정 실행 -> analysis/out_final/ . 시스템별 유효 답이 4,000씩 안 차거나 미해결(review) 답이 있으면 거부
python analysis/human_sample.py draw  --out analysis/out_final            # 사람 200답 시트만 따로 (run_analysis 가 자동으로도 씀)
python analysis/human_sample.py kappa --out analysis/out_final --a A.csv --b B.csv
```
옵션: `--search-validity strict|searches_only` (모호성 A1).

## 단계와 파일

| 단계 | 파일 | 하는 일 |
|---|---|---|
| (a) 적재·검증 | load_data.py | raw/ + raw_retry/(재수집, _partial 제외) 합치기, 시범(P-) 제외, W-mem 제외, 검색 조건 무효 처리, 결측률 |
| (b) 판정 | auto_judge.py | rules.md 1~4절의 결정적 부분(다국어 사전). 확정 못 하는 답은 `review`로 두고 review_queue.jsonl 에 씀. LLM 보조 분류는 스텁(호출 안 함): `build_llm_prompt`, `write_review_queue`, `load_llm_labels` |
| (b) 사람 표본 | human_sample.py | 시드 20261021 무작위 200답, 평가자 시트(A·B), 코헨 카파(+부트스트랩 CI) 자동 vs 사람, 사람 vs 사람 |
| (c) 분석 | run_analysis.py, stats_lib.py | H1~H5, 종합 모형, Holm |
| (d) 결과 | out_*/results.json + CSV | 원고가 읽는 파일 |

LLM 보조 분류를 하려면: out_*/review_queue.jsonl 을 `auto_judge.build_llm_prompt` 의 프롬프트(rules.md 원문, 정답 없음)로 한 줄씩 분류해 `out_*/llm_labels.jsonl` (스키마 `LLM_LABEL_SCHEMA`) 로 저장 후 다시 실행. 정답 대조는 코드가 한다.

## prereg 대 코드

| prereg | 코드 | 출력 |
|---|---|---|
| 7절 H1 (폐업→"영업 중" 비율 − 영업→"폐업" 비율, 시스템별, 가게 군집 SE, 95% CI) | run_analysis.tbl_h1, stats_lib.diff_independent / cluster_mean | h1.csv |
| H2 (언어별 정답률, 한국어 대비 같은 가게 짝 차이) | tbl_h2, paired_cluster_diff | h2.csv (느슨한=확증, 엄격한=병행) |
| H3 (H-search 대 H-mem 오류율, 같은 가게·언어 짝) | tbl_h3 | h3.csv (전체 = 확증, 언어별 = 탐색) |
| H4 (폐업 가게, "영업 중" 단정 ~ log(폐업 뒤 일수), 가게 임의절편 로지스틱) | tbl_h4, stats_lib.fit_glmm_logit | h4.csv |
| H5 (5개 언어 판정이 모두 같지 않은 가게 비율 + CI) | tbl_h5 (Wilson, Clopper-Pearson) | h5.csv |
| 종합 모형 (정답 ~ 언어+영업상태+카카오+지역+시스템+(1|가게)) | tbl_model | model_coefficients.csv |
| Holm 보정, 40 미만 칸 비해석 | tbl_holm, `interpretable` 열 | holm.csv |
| 8절 결측 보고 | load_data 인벤토리 | data_inventory.csv |
| 6절 사람 200답 카파 | human_sample | human_sample/, kappa.csv |
| "그 밖은 탐색" | `confirmatory=False` 열 | 모든 표 |

혼합효과 로지스틱은 statsmodels 가 아니라 직접 구현(Gauss-Hermite 구적 최대우도, stats_lib.fit_glmm_logit). 시뮬레이션 복원 검사와 statsmodels Logit 교차 검사가 tests/ 에 있다. 사건이 10 미만이거나 분리(separation)면 추정치를 내지 않고 사유를 적는다.

## 공개본 out_final 에 대하여

out_final/ 이 리포트에 실린 수치의 공개본이다(리포트 `report/local404_ko.md`가 인용한다). 수집이 끝난 자료와 LLM 보조 판정 라벨로 만들었다. 실행 옵션은 `--dryrun`이고 결과 파일의 `mode` 열도 dryrun이지만, 시험 결과라는 뜻이 아니다. Llama(L-mem) 수집이 계획(800곳 x 5언어)보다 적어 `--final`의 완전성 검사를 통과하지 못해서 이 옵션으로 만들었다. 시험 결과 안내 문구(`DRYRUN_NOT_FOR_PUBLICATION.txt`, results.json 의 `banner`)는 지웠고 수치는 바뀌지 않았다. 다시 실행하면 생성 시각과 `answers_fingerprint`가 달라질 수 있다.

out_dictonly/ 는 사전 판정만 쓴 결과(리포트 부록 D)다. Claude 세 조건 칸만 인용하며, L-mem 칸은 수집 도중 자료라 쓰지 않는다.

## 검색 2조건 부표본 (사전 등록과 달라진 점, 결과 분석 전 결정 2026-10-24)

H-search·S-search는 sampling/subsample_search_v1.csv의 100곳 x 5언어(조건당 500문항, 시드 20261024)만 분석한다(config.SUBSAMPLE_*, load_data.subsample_ids / expected_qids). 부표본 밖 가게의 답은 raw에 있어도 쓰지 않고 data_inventory.csv의 `outside_subsample_dropped`로 센다. `--final`은 검색 조건 500, 기억 조건 4,000이 차야 돈다. H-mem·L-mem 단독 분석은 800곳 전부. H3(H-search 대 H-mem)는 같은 100곳의 H-mem 답과 (가게, 언어)로 짝짓는다.

검정력: 검색 조건 H4(폐업 가게만, "영업 중" 단정 ~ log 폐업 뒤 일수)는 폐업 가게가 약 50곳(조건당 250답, 가게 군집)뿐이라 800곳 때(폐업 400곳)보다 검정력이 크게 낮다. 검색 조건의 H1 한 방향 비율, 언어별 칸(가게 100곳, 폐업 50·영업 50)도 CI가 넓다. 표본 40 미만 칸은 해석하지 않는다는 규칙은 그대로이며, 검색 조건의 영업·폐업 칸(언어별 50곳)이 40 근처라 결측이 늘면 비해석 칸이 생긴다. 확증 H4는 기억 조건 800곳 결과를 중심으로 읽고, 검색 조건 H4는 부표본 한계를 붙여 보고한다.

## 모호성 / 결정이 필요한 곳

(results.json 의 `ambiguities_needing_confirmation` 과 같은 목록. 아래는 코드가 택한 해석이며 확인 전까지 잠정이다.)

1. A1 검색 조건 무효 기준: HANDOFF 는 searches==0. 실제로는 searches==1 이어도 본문이 검색 한도 소진·미실행인 답이 있다(H-search 원본 978답 중 약 950). 기본 strict 는 그런 답도 결측으로 본다. 판정 사전 밖의 정규식(load_data.LIMIT_RE)이라 누락·오탐 가능성이 있으니 표본 확인 필요.
2. A2 4번째 시스템은 L-mem(로컬). W-mem 은 탐색 전용으로 제외.
3. A3 분모에 '모름' 포함. 단정한 답만의 비율은 탐색 열.
4. A4 정답률은 모름을 0(정답 아님)으로 합산.
5. A5 H3 오류율 = 틀림 비율(모름 제외 아님, 분모는 전체).
6. A6 양측 p 로 Holm, 방향 단측 p 병기.
7. A7 Holm 가족 정의(전체 확증 검정 한 가족 / 가설별).
8. A8 H5 에서 '모름'을 별개 판정 값으로 취급, p 값 대신 CI 하한으로 판단, Holm 제외.
9. A9 H4 일수 정의와 모형 직접 구현.
10. A10 종합 모형 기준 범주.
11. A11 사람 200답: 모집단·층화·평가 방식. 지금 시트는 시험용, 수집 완료 뒤 다시 뽑아야 한다(같은 시드).
12. A12 rules.md 가 말한 judge/auto_judge.py 대신 analysis/auto_judge.py (judge/ 수정 금지). 사전은 사전 등록 이후 작성 -> 사람 표본 검증 필수.
13. A13 업태 철자 '패밀리레스트랑' 처리, 표에 없는 업태는 기타.
14. A14 40 미만 칸의 단위.
15. A15 미해결(review) 답 처리.
16. 표본 파일에 폐업 일자가 측정일과 같은 가게는 없음(최소 5일)이라 log(0) 문제는 없지만 코드는 1일 미만을 1일로 올린다.
