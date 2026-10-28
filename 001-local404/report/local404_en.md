# Local404: Does AI Say That Closed Neighbourhood Shops Are Still Open?

This is a translation. The reference version is the Korean original, version 1: https://define404.com/report/002-local404-closed-shops/

A survey of AI responses for 800 ordinary restaurants in Korea, in 5 languages and 4 response conditions

- Author: Define404 Research
- Date: 2026-10-24
- Preregistration: OSF https://osf.io/5qnxu (registered 2026-10-20)
- DOI: https://doi.org/10.5281/zenodo.23740040
- Competing interests: the author's organisation Define404 is preparing an AI answer monitoring service and a per-shop AI exposure diagnostic service. Its own products were not included in the study.

## Abstract

We examined how AI assistants answer when asked whether a neighbourhood shop is still open and what its address and business type are. Public licensing data served as ground truth. We drew a stratified sample of 400 open and 400 closed restaurants, sent questions automatically in 5 languages, classified the answers with a rule-based dictionary and LLM-assisted judgment, and tested the preregistered hypotheses. Across the three conditions of Claude Haiku 5.5 and Sonnet 5.5 (5,000 valid answers), only 1 answer gave a definite answer on open status, and no answer said a closed shop was open. Hypotheses H1, H3, and H4 therefore could not be tested. Llama 3.1 8B gave a definite answer in 186 of 1,641 determined judgments (11.3%), with an accuracy of 48.4%. The proportion of closed shops described as open was higher than the proportion of open shops described as closed (H1 supported).

### Key results

- In the three Claude conditions, 99.98% of questions (4,999/5,000) received no definite answer on open status; the model said it could not confirm. There were 0 answers that said a closed shop was open (Wilson 95% upper bound among answers about closed shops: 1.51% in the web search condition, 0.19% in the memory condition).
- The web search conditions were no different. Among 1,000 answers in the web search conditions, only 1 was a definite answer, and that 1 was correct.
- Of the 112 Claude answers that stated an address, nearly all concerned open shops, and 95.5% (107) were correct.
- Llama 3.1 8B said open (127 answers) more often than it said closed (59). The proportion of closed shops described as open (7.3%) was higher than the proportion of open shops described as closed (4.4%) (difference 2.9 percentage points, Holm-adjusted p=0.039).

<!-- src: 001-local404/analysis/out_final/exploratory_summary.csv; 001-local404/analysis/out_final/h1.csv; 001-local404/analysis/out_final/holm.csv; 001-local404/analysis/out_final/judgments.csv (L-mem, status in open/closed: 186건, 정답 90건) -->

## 1 Introduction

People ask AI assistants whether a neighbourhood shop is still open. Asking a conversational AI "Is this restaurant still around?" before opening a map app is already common. If the AI says a closed shop is open, the customer makes a wasted trip; if it says an open shop is closed, the shop loses a customer. Yet shop owners have almost no way to check what AI says about their shop.

This study turned that problem into something measurable. Ground truth was the open status recorded in local-government licensing data, and the same question about the same shop was sent in five languages and compared across AI response conditions. Sample design, query collection, judgment, and statistical analysis were all written as code, so the same procedure can be run again. The hypotheses and analysis methods were preregistered on OSF before collection.

The research questions were organised into five hypotheses. H1 asks whether the proportion of closed shops described as open is higher than the proportion of open shops described as closed. H2 asks whether the correct rate for non-Korean questions is lower than for Korean, H3 whether web search lowers the error rate, H4 whether wrong "open" answers for closed shops decrease as more time passes after closure, and H5 whether answers about the same shop differ by language.

## 2 Methods

Figure 1. How the study was run

![The sequence: 800 restaurants were sampled and asked about in 5 languages, and the answers of four AI systems were sorted into open, closed, and unknown and matched against actual open status](figures/fig1-flow.svg)

<!-- src: 001-local404/analysis/make_figures.py; 001-local404/analysis/out_final/exploratory_summary.csv -->

### 2.1 Sample

The source of ground truth is the nationwide file of the local-government licensing dataset 식품_일반음식점 (food service, ordinary restaurants) (file.localdata.go.kr, received on 2026-10-21 with 2,305,461 rows). Rows were excluded if they had no address, if the shop name was shorter than 2 characters, if the same shop name appeared in 2 or more rows within the same district, or if the shop was marked closed but had no closure date.

The strata are the 8 combinations of open status (open, closed), Kakao place registration (listed, not listed), and region (metropolitan city, province), and 100 shops were drawn from each stratum for a total of 800 (open 400, closed 400). Candidates in each stratum were sorted by licence number, shuffled with seed 20261021 and filled from the top. In a pilot, every system answered that it did not know randomly chosen shops, so no differences could be seen. That is why Kakao registration was added as a stratum variable standing in for online visibility. The sample size was set to the roughly 392 shops per group needed to detect a 10 percentage point difference in H1 at a 5% significance level with 80% power.

The web search conditions were collected from a stratified subsample of 100 of the 800 shops (open 50, closed 50, allocated proportionally across the 8 strata, seed 20261024).

Table 1. Sample composition

| Set | Shops | Composition | Seed |
|---|---|---|---|
| Full sample (memory condition) | 800 | 8 strata x 100 (open 400, closed 400) | 20261021 |
| Search subsample (web search condition) | 100 | Proportional across 8 strata (open 50, closed 50) | 20261024 |

<!-- src: 001-local404/prereg.md#3; 001-local404/DEVIATIONS.md; 001-local404/analysis/out_final/results.json#inputs.sample_v2_sha256 -->

### 2.2 Questions

For each shop, one question asking together whether it is open, its address, and its business type was written in Korean, English, Japanese, Simplified Chinese, and Vietnamese. The shop name and district are given in Korean script in every language. The business type was not included in the question because it is itself a judged item. The question templates are in Appendix A (collect/question_templates.json v1.1).

### 2.3 Response systems

Table 2. Response systems and valid answers

| Code | Model | Condition | Shops | Valid answers |
|---|---|---|---|---|
| H-mem | Claude Haiku 5.5 | No tools | 800 | 4,000 |
| H-search | Claude Haiku 5.5 | Web search | 100 | 500 |
| S-search | Claude Sonnet 5.5 | Web search | 100 | 500 |
| L-mem | Llama 3.1 8B Instruct (Ollama q8_0, max 300 tokens, seed 20261021) | No tools | 800 | 2,312 (English 800, Japanese 800, Korean 712) |

<!-- src: 001-local404/analysis/out_final/data_inventory.csv; 001-local404/collect/PROTOCOL.md; 001-local404/collect/run_lmem.py -->

Claude responses were collected through an automated query procedure. A common instruction (system prompt) was attached to every query, and it contained the sentence "Answer honestly. If you cannot confirm something, say so." The memory condition added an instruction not to use tools; the web search condition added an instruction to use web search for every question. Each question was answered separately, and the respondent did not know the purpose of the study or the ground truth. Llama was run locally and received only the question as a user message; no common instruction was attached.

### 2.4 Judgment

The judgment rules (judge/rules.md v1.0) were fixed before collection. Open status takes one of three values: says open, says closed, or unknown (could not confirm or no conclusion). An answer whose conclusion is open, even with caveats, is an open assertion. Address is correct if the road name or legal-dong matches the ground truth, wrong if it differs, and absent if not stated. Business type is compared with the ground truth in 8 groups (Korean, Chinese, Japanese, Western, snack bar, chicken/pub/bar, cafe/dessert, other). Lenient correct means the open status is correct; strict correct means the open status and any stated address and business type are all correct.

The 1st-pass judgment is done by rule-based code using a multilingual expression dictionary (analysis/auto_judge.py). Items the dictionary cannot settle are passed to LLM-assisted judgment. The assisting judge sees only the rule text, the question, and the answer, classifies answers one at a time, and cannot see the ground truth or the response system. Comparison with ground truth is done by code. In the three Claude conditions, LLM-assisted judgment settled 492 items (H-mem 214, H-search 171, S-search 107). For L-mem only dictionary judgment was applied; the 671 items (29.0%) the dictionary could not settle were left undetermined and excluded from all tests and accuracy calculations.

### 2.5 Analysis

The preregistered analyses are as follows. H1 is the difference between the proportion of closed shops described as open and the proportion of open shops described as closed, with shop-level clustered standard errors. H2 is the paired difference in correct rate between Korean and each other language for the same shop. H3 is the paired difference between Haiku web search and Haiku memory. H4 is a logistic mixed model (shop random intercept) regressing whether a closed shop was described as open on the log of days since closure. H5 is the proportion of shops whose answers across the 5 languages are not all the same. Confidence intervals are Wilson intervals. H1 to H4 were corrected for multiplicity with the Holm method, and cells with fewer than 40 samples or an undefined p-value were excluded from the correction family. Because the null hypothesis for H5 is a disagreement proportion of 0 and its p-value is therefore undefined, it was excluded from the Holm correction and judged by whether the lower bound of the confidence interval exceeds 0 (Appendix C). Analyses not in the preregistration are marked as exploratory analysis.

## 3 Results

### 3.1 Response distribution: the Claude systems withhold judgment

Table 3. Open status judgment by system (Wilson 95% confidence interval in parentheses)

| System | n | Says open | Says closed | Unknown | Undetermined |
|---|---|---|---|---|---|
| H-mem | 4,000 | 0 (0%) | 0 (0%) | 4,000 (100%; 99.90~100) | 0 |
| H-search | 500 | 0 (0%) | 0 (0%) | 500 (100%; 99.24~100) | 0 |
| S-search | 500 | 1 (0.2%; 0.04~1.12) | 0 (0%) | 499 (99.8%; 98.88~99.96) | 0 |
| L-mem | 2,312 | 127 (5.5%; 4.6~6.5) | 59 (2.6%; 2.0~3.3) | 1,455 (62.9%; 60.9~64.9) | 671 (29.0%) |

<!-- src: 001-local404/analysis/out_final/exploratory_summary.csv (scope=all) -->

Figure 2. If you ask the AI 100 times (answer counts were scaled down to 100 cells and rounded. The 1 definite answer from the Claude systems is 1 out of 5,000 and smaller than one cell)

![The Claude systems answered could not confirm in all 100; Llama answered open 5 times, closed 3 times, unknown 63 times, and unclassifiable 29 times out of 100](figures/fig2-100-answers.svg)

<!-- src: 001-local404/analysis/make_figures.py; 001-local404/analysis/out_final/exploratory_summary.csv -->

Among the 5,000 valid answers in the three Claude conditions, only 1 gave a definite answer on open status: a Chinese-language question in S-search. That answer was also correct, saying an open shop was open. In the 2,500 answers about closed shops there were 0 open assertions, and in the 2,500 answers about open shops there were 0 closed assertions. The Wilson 95% upper bound for the closed-shop cell is 1.51% for each web search condition with 250 answers, and 0.19% for H-mem with 2,000 answers. The result was the same in all five languages. Even in the web search conditions, only 1 of 1,000 answers was a definite answer.

<!-- src: 001-local404/analysis/out_final/exploratory_summary.csv (scope=truth, scope=lang); 001-local404/analysis/out_final/status_distribution.csv -->

### 3.2 Preregistered hypotheses H1 to H5

In the three Claude conditions there were practically no definite answers, so the tests for H1, H3, and H4 could not be carried out. When every proportion being compared is exactly 0 and the standard error is therefore 0 as well, the p-value of a confidence-interval-based test is undefined. This does not mean the hypotheses are wrong. It means the responses in these conditions had no variation on which to test them.

Table 4. Results of the preregistered hypothesis tests

| Hypothesis | System | Result |
|---|---|---|
| H1 | S-search, H-search, H-mem | Open assertions for closed shops 0%, closed assertions for open shops 0%. Test not possible (0 vs 0) |
| H1 | L-mem | 7.3% (59/803; 95% CI 5.5 to 9.2) vs 4.4% (37/838; 3.0 to 5.8). Difference 2.9 percentage points (0.6 to 5.2), two-sided p=0.013, Holm-adjusted p=0.039. Supported |
| H2 | S-search, H-search, H-mem | Correct rate 0%, no difference from Korean. Test not possible. Exception: S-search Chinese, +1 percentage point (1 answer, p=0.317) |
| H2 | L-mem | English -15.1 percentage points (-19.0 to -11.2; Holm p=2.0e-13), Japanese -10.2 percentage points (-15.7 to -4.7; Holm p=0.0010). No Chinese or Vietnamese responses. Supported for English and Japanese |
| H3 | H-search vs H-mem | 500 pairs (100 shops), 0 errors in both conditions. Test not possible |
| H4 | S-search, H-search, H-mem | 0 wrong "open" answers (out of 250, 250, and 2,000). Test not possible |
| H4 | L-mem | 59 open assertions among 803 answers about closed shops. Odds ratio per log day since closure 1.04 (0.84 to 1.30), p=0.70. Not supported |
| H5 | S-search | Shops where judgments differed across the 5 languages: 1/100 (1.0%; Wilson 0.18 to 5.45%). Formally met but rests on one case |
| H5 | H-search, H-mem | 0/100 (upper bound 3.70%), 0/800 (upper bound 0.48%). Every shop had the same judgment in all 5 languages |
| H5 | L-mem | No shop had answers in all 5 languages; test not possible |

<!-- src: 001-local404/analysis/out_final/h1.csv; 001-local404/analysis/out_final/h2.csv; 001-local404/analysis/out_final/h3.csv; 001-local404/analysis/out_final/h4.csv; 001-local404/analysis/out_final/h5.csv; 001-local404/analysis/out_final/holm.csv (holm_p_two_all) -->

The 1 S-search case for H5 is a shop where only the Chinese answer said open and the other four languages said unknown. No system had a shop where open and closed answers collided. This one case is the same item as the only answer that said open.

Llama's H2 result is a correct rate that counts unknown as incorrect, so the differences between languages largely reflect differences in the rate of definite answers. On determined judgments, Llama gave a definite answer on open status in 120 of 380 Korean answers (31.6%), 61 of 524 Japanese answers (11.6%), and 5 of 737 English answers (0.7%).

### 3.3 Address and business type

Address and business type appeared even in answers that gave no definite answer on open status. This section is exploratory analysis.

Table 5. Address and business type mention rate and accuracy (Wilson 95% confidence interval in parentheses)

| System | Address stated | Address accuracy | Business type stated | Business type accuracy |
|---|---|---|---|---|
| S-search | 26/500 (5.2%) | 25 (96.2%; 81.1~99.3) | 149/500 (29.8%) | 124 (83.2%; 76.4~88.4) |
| H-search | 34/500 (6.8%) | 30 (88.2%; 73.4~95.3) | 141/500 (28.2%) | 120 (85.1%; 78.3~90.1) |
| H-mem | 52/4,000 (1.3%) | 52 (100%; 93.1~100) | 738/4,000 (18.5%) | 561 (76.0%; 72.8~79.0) |
| L-mem | 70/2,312 (3.0%) | Not computed because of undetermined items | 285/2,312 (12.3%) | Not computed because of undetermined items |

<!-- src: 001-local404/analysis/out_final/exploratory_summary.csv (scope=all, address_*, type_*) -->

Figure 3. Claude answers that stated an address (three conditions combined)

![Across the three Claude conditions, answers stating an address: open shops 105 (101 correct), closed shops 7 (6 correct)](figures/fig3-claude-address.svg)

<!-- src: 001-local404/analysis/make_figures.py; 001-local404/analysis/out_final/exploratory_summary.csv -->

Across the three Claude conditions, 107 of the 112 answers that stated an address (95.5%) matched the ground truth address. Most answers that stated an address concerned open shops. S-search stated an address in 26 of 250 answers about open shops and in 0 of 250 about closed shops. H-search stated it in 31 open versus 3 closed, and H-mem in 48 open versus 4 closed. Closed shops appear to leave less information online, which makes their address harder to confirm and raises the share of unknown answers accordingly. This is an observed pattern, not a result of testing the cause directly.

Business type was stated more often than address. The web search conditions (28 to 30%) stated it more often than the memory condition (18.5%), and accuracy was 76 to 85%.

### 3.4 Llama results

Unlike the Claude systems, Llama 3.1 8B did give definite answers on open status. It gave a definite answer in 186 of the 1,641 determined judgments (11.3%; 9.9 to 13.0): 127 open assertions and 59 closed assertions. Of the 186 definite answers, 90 were correct, an accuracy of 48.4% (41.3 to 55.5). That is not far from a coin toss.

Table 6. Llama open status judgment by language

| Language | n | Says open | Says closed | Unknown | Undetermined |
|---|---|---|---|---|---|
| English | 800 | 5 (0.6%) | 0 (0%) | 732 (91.5%) | 63 (7.9%) |
| Japanese | 800 | 37 (4.6%) | 24 (3.0%) | 463 (57.9%) | 276 (34.5%) |
| Korean | 712 | 85 (11.9%) | 35 (4.9%) | 260 (36.5%) | 332 (46.6%) |

<!-- src: 001-local404/analysis/out_final/exploratory_summary.csv (system=L-mem, scope=lang); 001-local404/analysis/out_final/judgments.csv (L-mem, 확정 단정 186건 중 정답 90건: 한국어 57/120, 일본어 31/61, 영어 2/5) -->

Of the 81 definite answers about closed shops, 59 (72.8%) wrongly said open, and of the 105 definite answers about open shops, 37 (35.2%) wrongly said closed. Llama leaned towards saying open, and for closed shops that lean becomes an error. This comparison conditional on a definite answer (difference 37.6 percentage points) is exploratory analysis. The accuracy of determined definite answers was 47.5% for Korean (57/120) and 50.8% for Japanese (31/61), a small difference between languages.

Figure 4. Llama's definite answers (determined judgments only)

![Of 81 definite answers about closed shops, 59 wrongly said open; of 105 definite answers about open shops, 37 wrongly said closed. 90 correct, 96 wrong](figures/fig4-llama-right-wrong.svg)

<!-- src: 001-local404/analysis/make_figures.py; 001-local404/analysis/out_final/exploratory_summary.csv -->

### 3.5 Judgment agreement

Judgment reliability was assessed by whether dictionary judgment and LLM-assisted judgment reached the same conclusion on the same answer. Answers classified by both methods in the three Claude conditions were compared.

Table 7. Agreement between dictionary judgment and LLM-assisted judgment

| Item | n | Agreement rate | Cohen's kappa (95% CI) |
|---|---|---|---|
| Open status | 1,364 | 100% | Not computable (almost all answers in one category) |
| Address | 1,239 | 95.7% | 0.35 (0.22~0.48) |
| Business type | 722 | 73.0% | 0.46 (0.39~0.52) |

<!-- src: 001-local404/analysis/out_final/llm_dictionary_agreement.csv (group=all) -->

Open status agreed on all 1,364 answers. However, almost all answers were unknown, so the categories are concentrated on one side and kappa is undefined. The 100% agreement only shows that the unknown judgment is stable; it does not show that the definite-answer judgments are valid. Kappa for address is computed low because answers stating an address are rare. Business type had the lowest agreement, at 73%. Business type accuracy (Table 5) should be read with this judgment uncertainty in mind.

## 4 Discussion

The most striking result of this study is not wrong answers but withheld judgment. The Claude systems almost always answered that they could not confirm open status, and in 5,000 answers there was no case of a closed shop being described as open. For a shop this is both reassuring and disappointing. The risk of a customer making a wasted trip on wrong open information is low. But an open shop also remains a "shop that cannot be confirmed" to the AI. Of the 2,500 answers about open shops, only 1 said the shop was open.

Address and business type point in the same direction. Addresses appeared mostly for open shops only, and accuracy was high. The AI speaks accurately about shops it knows and says it does not know the ones it does not. It is natural to conclude that for a shop to appear in AI answers, its information must be public in a form the AI can confirm. This is an interpretation drawn from an observed pattern, not a hypothesis-tested result.

Web search did not change the withholding either. Even in the web search conditions, only 1 of 1,000 answers was definite. Search may not have reached sources that directly confirm open status, or the instruction not to assert without sufficient evidence may have been at work. This design cannot separate the two possibilities.

Llama 3.1 8B is the contrast. The small local model gave definite answers, and its accuracy was 48.4%. In particular, 72.8% of its definite answers about closed shops wrongly said open. It shows the risk on the side of speaking confidently while being wrong. Withholding judgment and asserting wrongly are two different failures. In this data the Claude systems were close to the former and Llama to the latter. However, the two families differ in both model and instruction (limitation 1 in Section 5), so it cannot be determined how much is a property of the model and how much is the effect of the instruction.

Figure 5. The AI that withholds judgment and the AI that asserts wrongly (the two families also differ in instruction, so this cannot be read as a difference between models alone; limitation 1 in Section 5)

![The Claude systems never said a closed shop was open but also told almost nothing about open shops; for Llama, most definite answers about closed shops wrongly said open](figures/fig5-two-failures.svg)

<!-- src: 001-local404/analysis/make_figures.py; 001-local404/analysis/out_final/exploratory_summary.csv -->

Within Llama, Korean questions had the highest rate of definite answers (relative to all answers: Korean 120/712, Japanese 61/800, English 5/800). This may be because Korean-language material about Korean shops is relatively plentiful. However, the accuracy of definite answers was similar across languages, so speaking more did not mean being more accurate.

## 5 Limitations

1. The instruction conditions differ by response system. The Claude systems were instructed to say so when they could not confirm, while Llama received only the question. Differences between the families therefore contain both model differences and instruction differences.
2. The web search conditions were collected from a stratified subsample of 100 shops, and Llama responses are limited to 800 English, 800 Japanese, and 712 Korean answers.
3. The study was run at a single point in time, from 2026-10-21 to the 24th, and judgment relied on rule-based classification and LLM judgment.

## 6 Conclusion

Under the instruction conditions of this study, Claude Haiku 5.5 and Sonnet 5.5 practically never gave a definite answer on whether a neighbourhood restaurant in Korea is open. There were 0 cases in 5,000 answers where a closed shop was described as open. In these conditions, the real problem is not the risk of wrong answers but that shops do not appear in AI answers because there is no information. Adding web search made no difference. By contrast, the small open model Llama 3.1 8B did give definite answers, and nearly half of them were wrong. Preregistered hypothesis H1 was supported by its tendency to describe closed shops as open. For AI to state open status, address, and business type accurately, public information the AI can confirm must exist first. That is the direction this data points to.

## Data availability

- Public repository: https://github.com/johndefine404/define404-research-public/tree/main/001-local404 (path 001-local404/). Analysis code and results are released. The raw sample with shop names and addresses and the raw answer texts are withheld; a sample with names and addresses removed is included.
- Report-fixing commit in the (private) research repository: b52ee75cd1fb6f35f8aed6381e866a3e3a54887c (later tidy-up commits renamed the results folder from analysis/out_dryrun to analysis/out_final, removed the trial-result notice, and changed sentence endings to the polite conversational style. No numbers were changed)
- Seeds: sample 20261021, search subsample 20261024, Llama 20261021
- Sample file sampling/sample_v2.csv SHA-256: 4aaf1ecd22963e703e3283c9223206e3cde2aa1e9daf6fde24f53fc8abc24871
- Preregistration prereg.md SHA-256: 87be279e17ebc0922ca079845ea3959ee04ca1379033f7b2c5e5fd8a21abc02b
- Judgment rules judge/rules.md SHA-256: a4ddb1efe5bd50c8d74e64a9678773646c9d05da0af73e749bf3f55f79386209
- Raw response fingerprint (SHA-256 of the hashes of 510 files): 71bee2b3dc6dd3af61c09f5334b840f12798f40043cea9eec57c99bda10a4ed0
- Analysis results analysis/out_final/results.json SHA-256: f9a4dbdcf88ac7aff3e32d13cea971ddbaa224332fbcaa176f995c6a79ea6123
- Reproduction: python analysis/run_analysis.py --dryrun --out analysis/out_final (the run option is named dryrun, and the mode column in the result files also reads dryrun. This is because Llama collection fell short of plan and does not pass the completeness check of --final. Re-running changes the generation time and the fingerprints)

Names and addresses of sole proprietors are removed from the public data, and the examples in Appendix A use fictitious names.

<!-- src: 001-local404/analysis/out_final/results.json#inputs -->

## Appendix A Question examples

가상의 가게 "하늘식당"(서울 마포구)을 묻는 질문 틀이에요.

| Language | Question |
|---|---|
| Korean | 마포구에 있는 음식점 '하늘식당', 지금도 영업하나요? 주소와 어떤 종류의 음식점인지도 알려 주세요. |
| English | Is the restaurant '하늘식당' in 마포구 still open? Please also tell me its address and what kind of restaurant it is. |
| Japanese | 마포구にある「하늘식당」という飲食店は今も営業していますか？住所と、どんな種類のお店かも教えてください。 |
| Chinese | 位于마포구的餐厅“하늘식당”现在还在营业吗？请同时告诉我它的地址和它是什么类型的餐厅。 |
| Vietnamese | Nhà hàng '하늘식당' ở 마포구 hiện còn mở cửa không? Cho tôi biết luôn địa chỉ và đây là loại nhà hàng gì. |

## Appendix B Summary of judgment rules

- Open status: three values, says open, says closed, or unknown. A conclusion with caveats still counts as a definite answer. If open and closed both appear, the final concluding sentence governs; with no conclusion it is unknown. An answer that only introduces a shop with a different name or in a different area is also unknown.
- Ground truth: open if the licensing status name is open or normal, closed if it is closed.
- Address: correct if the road name (down to the street name) or the legal-dong or eup/myeon matches; wrong if a different place is presented as the target shop's address; absent if not stated or if only another shop's address is given.
- Business type: compared in 8 groups (Korean, Chinese, Japanese, Western, snack bar, chicken/pub/bar, cafe/dessert, other). If the ground truth is other, the item is excluded from business type judgment.
- Scoring: lenient correct means the open status is correct; strict correct additionally requires any stated address and business type to be correct.
- Judgment order: multilingual expression dictionary, LLM-assisted judgment (ground truth withheld), comparison with ground truth by code.

<!-- src: 001-local404/judge/rules.md#1-5 -->

## Appendix C Changes from the preregistration

| Item | Preregistration | As run |
|---|---|---|
| Local model | Llama 3.1 8B on Cloudflare Workers AI (W-mem) | Llama 3.1 8B Instruct on local Ollama (L-mem) |
| Web search condition sample | All 800 shops | Stratified subsample of 100 shops |
| Judgment | Rule-based dictionary judgment | LLM-assisted judgment added to dictionary judgment |
| Judgment reliability assessment | Agreement and Cohen's kappa of 2 human judges on 200 random answers | Replaced by agreement between dictionary judgment and LLM-assisted judgment (Table 7) |
| H5 and the Holm correction | Holm correction for H1 to H5 | H5 excluded from the Holm family because its p-value is undefined; judged by the lower confidence bound |
| Llama response languages | 5 languages | English, Japanese, Korean |
| Response instruction | No identical instruction across systems was specified | Common instruction for the three Claude conditions; question text only for Llama |
| Response re-collection | Retry only failed and empty answers | Some responses re-collected (replacing language-mismatched and invalid responses) |

<!-- src: 001-local404/DEVIATIONS.md; 001-local404/prereg.md#5-6 -->

## Appendix D Dictionary judgment only results

Because the judgment rules were supplemented after collection (LLM-assisted judgment was added), in line with section 8 of the preregistration we also report results using only the original rule, dictionary judgment. With dictionary judgment alone, the number of answers giving a definite answer on open status in the three Claude conditions is 0 for all of S-search (500 answers), H-search (500 answers), and H-mem (4,000 answers). Answers the dictionary could not settle were 15 for S-search, 25 for H-search, and 0 for H-mem. The single open assertion in the main text (S-search Chinese) is 1 answer settled by assisted judgment. With dictionary judgment alone, no system had a shop whose judgments differed across the 5 languages, so H5 is not supported (0 shops out of 91 for S-search, 81 for H-search, and 800 for H-mem among shops with determined judgments in all 5 languages). Llama did not use assisted judgment, so the main text results are the dictionary judgment results.

<!-- src: 001-local404/analysis/out_dictonly/exploratory_summary.csv (Claude 세 조건, scope=all); 001-local404/analysis/out_dictonly/h5.csv -->
