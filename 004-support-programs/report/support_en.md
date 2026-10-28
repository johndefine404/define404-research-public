# When You Ask an AI About a Government Support Program, Does It Get the Deadline Right?

This is a translation. The reference version is the Korean original, version 1: https://define404.com/report/005-support-program-deadlines/

We asked a web-search-enabled AI assistant about 200 support program notices from Bizinfo (기업마당), in Korean, and checked the deadline, application status, and implementing agency in each answer against the official notice list

- Author: Hawon Kim (Define404 Research)
- Date: 2026-10-29
- Type: Measurement report. 200 notices were newly queried and judged by rule.
- Preregistration: research repository commit 35fac08 (2026-10-28 23:41 ICT). The prereg.md file, containing the hypotheses, sample, judging rules, and analysis method, was committed before data collection.
- DOI: https://doi.org/10.5281/zenodo.23739022
- Conflicts of interest: the author's company, Define404, is preparing an AI answer monitoring service and a per-shop AI visibility check. Its own products were not included in the study.

## Summary

We measured whether a small business owner who asks an AI assistant "Can I still apply for this support program? When is the deadline?" gets a correct answer. The ground truth was the notice list of Bizinfo (기업마당, bizinfo.go.kr), the Korean government's support program portal. We drew a stratified sample of 200 notices, with 100 ongoing and 100 expired, and 100 from central ministries and 100 from local governments, and asked Claude Sonnet 5.5 with web search once per notice, in Korean. Answers were judged by rules fixed before collection. 78 of 200 answers (39.0%) stated the correct deadline; the gap between central ministry notices (40.0%) and local government notices (38.0%) was -2.0 percentage points, so the preregistered hypothesis H1 (local government notices are worse) was not supported. On application status, 142 of 200 answers (71.0%) said they could not confirm it, and all 58 answers that did reach a conclusion were in the correct direction. Not a single answer said an expired notice was still open, and not a single answer said an ongoing notice had closed, so H2 was not supported either. The rule for judging application status was found to be defective after collection and was revised; the results under the original rule are reported unchanged in the appendix.

### Key results

- 78 of 200 answers stated the correct deadline, 39.0% (95% confidence interval 32.5–45.9). Central ministry notices 40.0% (30.9–49.8), local government notices 38.0% (29.1–47.8), a gap of -2.0 percentage points (-15.5–11.5). H1 not supported.
- On application status, 142 of 200 answers (71.0%; 64.4–76.8) gave no conclusion and said they could not confirm it. All 58 answers that reached a conclusion (29.0%; 23.2–35.6) were in the correct direction.
- 0 of the 100 expired notices were described as still open, and 0 of the 100 ongoing notices were described as closed. With both error counts at 0, H2 (answers calling an expired notice open outnumber the reverse) was not supported.
- The strict score, requiring the deadline, application status, and implementing agency all to be correct, was 46 of 200 (23.0%; 17.7–29.3). The paired difference from the loose score, which looks at the deadline only, was 16.0 percentage points (10.9–21.1).

<!-- src: 004-support-programs/analysis/out/results.json#preregistered.cells.all, H1, H2; analysis/out/results.json#exploratory.loose_minus_strict_paired -->

## 1 Introduction

Support programs for small businesses in Korea are numerous and short-lived. Bizinfo alone listed 1,445 ongoing notices as of 2026-10-28. Reading the whole list is hard for a shop owner, so more and more of them ask an AI assistant "Can I still apply for this?" If the AI gets the deadline wrong, the owner either fails to submit the documents they prepared or spends time on a program that has already ended.

There is research measuring the accuracy of AI answers about US welfare programs (Section 2), but within the scope we checked, we found no report that asked a general web-search-enabled AI assistant about Korean support program notices and measured items whose ground truth is fixed by a public list (deadline, implementing agency, whether the program is ongoing).

This study set out to measure that gap. It makes three contributions. Using the Bizinfo notice list as ground truth, we drew a stratified sample of 200 notices and measured the AI assistant's deadline accuracy. We examined in which direction the AI errs on application status for expired versus ongoing notices. And we committed the sampling code, judging rules, and analysis code to the repository before collection so that the same procedure can be rerun.

There are two hypotheses. H1 (primary) is that the share of answers stating the correct deadline is lower for local government notices than for central ministry notices. H2 (secondary) is that the share of answers asserting that an expired notice is still open is higher than the share asserting that an ongoing notice has closed.

## 2 Related work

Most research measuring the accuracy of AI answers about public programs concerns US welfare programs. Gosciak et al. (2026) had experts label 770 questions about US SNAP (food assistance) and ran an experiment on how chatbot accuracy affects caseworker accuracy. Vals AI (2026) built 459 SNAP scenarios with an expert rubric of 2,931 items, scored with an LLM judge; the best model reached 76.93%. Simpson et al. (2026) reported cases in which frontier models mishandled exception clauses across 225 regulatory rule scenarios. Kennan et al. (2025) compared chatbots' plain answers with retrieval-augmented answers for SNAP and Medicaid in 7 states.

Those studies set the ground truth by expert judgment and dealt with questions that require interpretation, such as eligibility rules. This study does the opposite and picks only items that need no interpretation. Deadlines and implementing agencies are values printed in the notice list, so they can be checked by rule. For scoring we followed the loose and strict scores of FreshQA (Vu et al. 2023); for confidence intervals and paired differences we followed Miller (2024). The convention of not interpreting cells with fewer than 40 samples comes from PopQA (Mallen et al. 2023). The design continues from our report No. 2, Local404 (Define404 Research 2026), which measured whether neighborhood shops were still open using the same approach.

## 3 Method

Figure 1. How the study was run

![200 Bizinfo notices were sampled, an AI assistant was asked about each in Korean, and the deadline, application status, and implementing agency were extracted from each answer by rule and checked against the notice list](figures/fig1-flow.svg)

<!-- src: 004-support-programs/analysis/make_figures.py; analysis/out/results.json -->

### 3.1 Population and sample

The ground truth source is the Bizinfo support program notice spreadsheet download (received 2026-10-28; 1,445 ongoing rows, 26,425 past rows). Its columns are supervising ministry, implementing agency, support field, notice title, application start date, application end date, registration date, and notice detail URL. The ground truth was frozen to the values in this file; even if Bizinfo edited a notice during collection, the ground truth was not changed.

Rows were excluded as follows: 699 whose notice title appeared more than once, 68 with no application dates, 16 whose application period had not yet started, 360 ongoing notices whose deadline fell outside 2026-11-18 to 2027-06-30 (including rolling and year-round notices), and 23,522 past notices whose deadline fell outside 2026-08-01 to 10-21. The deadline windows leave a 7-day margin on each side so that no notice changes status during the collection period.

The strata are the 4 cells formed by status (ongoing, expired) times jurisdiction (central ministry, local government). A supervising ministry whose name ends in a Korean local government suffix (special city, metropolitan city, special self-governing city, special self-governing province, or province) was treated as local government; everything else, including agencies and commissions, as central ministry. In each cell, candidates were sorted by notice ID, shuffled with seed 20261028, and the first 50 taken, for 200 in total. The sample size was set to 98 per group, which is what is needed to detect a 20 percentage point difference under H1 at a 5% significance level with 80% power. Each notice gets one answer, so the 200 notices are the effective sample.

Table 1. Sample composition (seed 20261028)

| Cell | Candidates | Sample |
|---|---|---|
| Ongoing x Central ministry | 265 | 50 |
| Ongoing x Local government | 752 | 50 |
| Expired x Central ministry | 718 | 50 |
| Expired x Local government | 1,470 | 50 |
| Total | 3,205 | 200 |

<!-- src: 004-support-programs/sampling/sample_log.txt; 004-support-programs/prereg.md#3 -->

### 3.2 Questions

One question in Korean was written for each notice. The template was "'{notice title}' 지원사업, 지금 신청할 수 있나요? 신청 마감일이 언제이고 어느 기관이 사업을 수행하는지도 알려 주세요." (Can I apply for the '{notice title}' support program now? Please also tell me the application deadline and which agency runs the program.) The notice title was inserted exactly as registered on Bizinfo, including any regional prefix; the deadline, agency, and status were not included in the question because they are what is being judged. The questions were split into 20 batches of 10, and the batch files contain only the questions.

### 3.3 Response system

There was one response system: Claude Sonnet 5.5 with web search, chosen because it is close to what people actually use. One call handled one batch (10 questions), and the respondent did not know the purpose of the study or the ground truth. The instructions told it to search for every question, to answer in the language of the question, and, if a search limit message appeared, to stop and record only the questions it had searched. Collection ran from the night of 2026-10-28 into 10-29; all 200 answers involved at least 1 search, so there were no invalid answers. The raw answers and search sources were saved in per-batch files.

### 3.4 Judging

Judging used rule code fixed before collection. There are three items.

- Application status: one of three values, asserted open, asserted closed, or unknown (could not confirm, or no conclusion). The ground truth is the status of the stratum.
- Deadline: among the dates in the answer, those appearing in a deadline context (within 40 characters of the Korean words for deadline, until, close, application period, or acceptance period, or at the end of a date range) are compared with the ground-truth application end date. A match is correct; only other dates is wrong; no date in a deadline context is none.
- Implementing agency: if the implementing agency (for notices run by a basic local government or directly by the ministry, the supervising ministry and the city, county, or district at the head of the notice title) appears in the answer, including common abbreviations, it is correct; if only a different agency is named, it is wrong.

The loose score is a correct deadline. The strict score requires a correct deadline, a correct application status, and an implementing agency that is not wrong. No LLM judge and no two-person human judging were used.

The application status judgment was revised once after collection (Section 3.6). Under the revised rule (v1.1), 0 answers were judged manually by the hub. Under the original rule (v1.0), 1 answer had both open and closed expressions in the same sentence and was flagged for manual judgment; that answer is counted as unknown in the v1.0 results (Appendix B).

### 3.5 Analysis

Every proportion is given with a Wilson 95% confidence interval. Each notice has one answer, so this equals a cluster interval at the notice level. H1 is tested by the 95% confidence interval and one-sided z test of the difference between the loose score rate for local government notices and that for central ministry notices. H2 is the difference between the rate of asserting an expired notice open and the rate of asserting an ongoing notice closed. The p values of the two hypotheses were Holm-corrected. The difference between the loose and strict scores of the same notice is reported as a paired difference. The 4 cells of status times jurisdiction (50 per cell) and the split between wrong and none for deadlines are exploratory analyses not in the preregistration. Cells with fewer than 40 samples are not interpreted.

### 3.6 Departures from the preregistration

While reading the judged sample after collection, we found that the implementation of the registered application status rule (v1.0) was defective. v1.0 split the answer into sentences and took the last sentence containing an open or closed expression as the conclusion; it read "신청 가능성은 사실상 없어 보입니다" (there is effectively no chance of applying) as open, and it read a mention that a previous round of the same program had closed as a conclusion that the target notice was closed. We therefore revised the rule to v1.1 before interpreting the analysis results. v1.1 treats the first sentence of the answer as the conclusion: if the first sentence contains a closed-side expression (such as "cannot apply", "closed", "ended", "has passed", "no chance"), it is asserted closed; if it contains an open-side expression (such as "can apply", "applications open", "accepting"), it is asserted open; if neither, unknown. All 200 answers put either a conclusion or a statement that they could not confirm in the first sentence. The deadline and implementing agency rules were not changed.

In accordance with Section 8 of the preregistration, the v1.0 results are reported unchanged in Appendix B. Under v1.0, H2 is supported with +34.0 percentage points; under v1.1, both errors are 0 and it is not supported. The difference between the two results comes from the judging defect, and it is the part of this study that must be read most carefully (Section 5).

## 4 Results

### 4.1 Deadline

Table 2. Share of answers with the correct deadline (loose score) and strict score (Wilson 95% confidence intervals in parentheses)

| Group | n | Deadline correct | Deadline, status, and agency all correct |
|---|---|---|---|
| All | 200 | 78 (39.0%; 32.5–45.9) | 46 (23.0%; 17.7–29.3) |
| Central ministry | 100 | 40 (40.0%; 30.9–49.8) | 28 (28.0%; 20.1–37.5) |
| Local government | 100 | 38 (38.0%; 29.1–47.8) | 18 (18.0%; 11.7–26.7) |
| Ongoing | 100 | 45 (45.0%; 35.6–54.8) | 18 (18.0%; 11.7–26.7) |
| Expired | 100 | 33 (33.0%; 24.6–42.7) | 28 (28.0%; 20.1–37.5) |

<!-- src: 004-support-programs/analysis/out/tables.md#표1; analysis/out/results.json#preregistered.cells -->

Figure 2. Out of 100 questions, how many answers gave the correct deadline (200 answers scaled to 100 squares and rounded)

![39 of 100 squares are answers with the correct deadline; central ministry notices 40 of 100, local government notices 38 of 100](figures/fig2-deadline-100.svg)

<!-- src: 004-support-programs/analysis/make_figures.py; analysis/out/results.json#preregistered.cells -->

78 of 200 answers (39.0%) stated the correct deadline. Of the remaining 122, 58 gave only other dates in a deadline context and 64 gave no date in a deadline context. For ongoing notices the split was 45 correct, 20 wrong, 35 none; for expired notices, 33 correct, 38 wrong, 29 none. This breakdown is exploratory. The wrong answers include some that gave the date of a similarly named notice or of a previous round (Section 6).

<!-- src: 004-support-programs/judge/judged.csv (deadline 열: correct 78, wrong 58, none 64; ongoing 45/20/35, expired 33/38/29) -->

### 4.2 Preregistered hypothesis H1: are local government notices worse?

Table 3. Preregistered hypothesis tests (differences in percentage points, 95% confidence intervals in parentheses)

| Hypothesis | Comparison | Difference | One-sided p | Holm p | Verdict |
|---|---|---|---|---|---|
| H1 | Local government loose score 38.0% vs central ministry 40.0% | -2.0 (-15.5–11.5) | 0.386 | 0.772 | Not supported |
| H2 | Asserted open among expired 0% vs asserted closed among ongoing 0% | 0.0 (0.0–0.0) | 0.500 | 0.772 | Not supported (both errors 0) |

<!-- src: 004-support-programs/analysis/out/tables.md#표2; analysis/out/results.json#preregistered.H1, H2 -->

The deadline accuracy for local government notices was 2.0 percentage points lower than for central ministry notices, but the confidence interval runs from -15.5 to 11.5 and comfortably contains 0. The sample was sized to detect a 20 percentage point difference, so a smaller difference may exist and have gone unseen. The hypothesis that local government notices are harder is not supported by these data.

### 4.3 Application status and hypothesis H2

Table 4. Distribution of application status answers (judging rule v1.1, Wilson 95% confidence intervals in parentheses)

| Group | n | Asserted, correct direction | Asserted, wrong direction | Unknown |
|---|---|---|---|---|
| All | 200 | 58 (29.0%; 23.2–35.6) | 0 | 142 (71.0%; 64.4–76.8) |
| Ongoing | 100 | 23 (23.0%; 15.8–32.2) | 0 | 77 (77.0%; 67.8–84.2) |
| Expired | 100 | 35 (35.0%; 26.4–44.7) | 0 | 65 (65.0%; 55.3–73.6) |
| Central ministry | 100 | 34 (34.0%; 25.5–43.7) | 0 | 66 (66.0%; 56.3–74.5) |
| Local government | 100 | 24 (24.0%; 16.7–33.2) | 0 | 76 (76.0%; 66.8–83.3) |

<!-- src: 004-support-programs/analysis/out/results.json#preregistered.cells (status_ok, unknown); H2 diff 0 -->

Figure 3. Asked whether you can still apply, the AI says "I couldn't confirm" 7 times out of 10 (200 answers scaled to 100 squares and rounded)

![71 of 100 squares are answers that could not confirm, 29 are assertions in the correct direction, and 0 are assertions in the wrong direction](figures/fig3-status-100.svg)

<!-- src: 004-support-programs/analysis/make_figures.py; analysis/out/results.json#preregistered.cells.all -->

142 of 200 answers (71.0%) said in the first sentence that the notice could not be found or confirmed. All 58 answers that reached a conclusion were in the correct direction. Among the 100 expired notices, 0 answers said the program was still open (Wilson 95% upper bound 3.7%), and among the 100 ongoing notices, 0 answers said it had closed (upper bound 3.7%). With both rates at 0, the H2 difference is 0.0 percentage points and the hypothesis is not supported. This does not show the hypothesis to be false; it shows that the answers under this condition contained no errors to compare.

Figure 4. Flat assertions in the wrong direction: 0

![Among 100 expired notices: "closed" 35 times, "still open" 0 times, unknown 65 times. Among 100 ongoing notices: "still open" 23 times, "closed" 0 times, unknown 77 times](figures/fig4-wrong-direction.svg)

<!-- src: 004-support-programs/analysis/make_figures.py; analysis/out/results.json#preregistered.cells (ongoing, expired) -->

For expired notices, 35 answers concluded that the program had closed, while for ongoing notices only 23 concluded that it was still open. Unknown was more common for ongoing notices, at 77. Even when the AI found the notice, it more often referred the user to the agency than put a conclusion that the program was ongoing in its first sentence.

<!-- src: 004-support-programs/analysis/out/results.json#preregistered.cells.ongoing.unknown, expired.status_ok -->

### 4.4 Exploratory: strict score and the 4-cell comparison

Within the same notices, the paired difference between the loose score (39.0%) and the strict score (23.0%) is 16.0 percentage points (10.9–21.1). Of the 78 answers with the correct deadline, 47 also asserted the correct application status, and 1 of those named the wrong implementing agency, so the strict score is 46. The implementing agency was correct in 161 of 200 answers, and 39 named a different agency. The figures in this section are exploratory.

<!-- src: 004-support-programs/analysis/out/results.json#exploratory.loose_minus_strict_paired; judge/judged.csv (loose=1 and status_ok=1: 47건, agency correct 161, wrong 39) -->

Table 5. The 4 cells of status x jurisdiction (50 per cell, not preregistered, Wilson 95% confidence intervals in parentheses)

| Cell | Deadline correct | All correct | Unknown |
|---|---|---|---|
| Ongoing x Central ministry | 40.0% (27.6–53.8) | 22.0% (12.8–35.2) | 72.0% (58.3–82.5) |
| Ongoing x Local government | 50.0% (36.6–63.4) | 14.0% (7.0–26.2) | 82.0% (69.2–90.2) |
| Expired x Central ministry | 40.0% (27.6–53.8) | 34.0% (22.4–47.8) | 60.0% (46.2–72.4) |
| Expired x Local government | 26.0% (15.9–39.6) | 22.0% (12.8–35.2) | 70.0% (56.2–80.9) |

<!-- src: 004-support-programs/analysis/out/tables.md#표3; analysis/out/results.json#exploratory.by_cell -->

Ongoing local government notices had the highest deadline accuracy at 50.0% but also the most unknowns at 82.0%, giving the lowest all-correct rate at 14.0%. In other words, many answers found the deadline but did not conclude that the program could still be applied for. With 50 per cell, the confidence intervals of the between-cell differences are wide, and this table should be read only as a source of hypotheses for the next study.

## 5 Discussion

In this study the AI assistant got the deadline of a support program notice right about four times in ten, and said it could not confirm the application status about seven times in ten. There were no assertions in the wrong direction. This points the same way as our report No. 2, Local404, where Claude models rarely asserted whether a neighborhood shop was open. This time, however, because the exact notice title was supplied and web search was used, concrete values such as the deadline were found close to half the time.

Two things put the shop owner at risk. One is an answer with the wrong deadline: 58 of 200 answers gave a date other than the correct one in a deadline context. Some of these were the dates of similarly named notices or previous rounds, so an owner who takes that date as this year's deadline for this notice will submit too late. The other is the absence of an answer: for 77 of the 100 ongoing notices there was no conclusion on whether one could apply, in which case the owner has to open the original notice anyway.

The post-collection revision of the judging rule deserves its own note. Run exactly as registered, the rule counts 43 of the 100 expired notices as described as still open, and H2 is supported (Appendix B). But those 43 included answers with the opposite meaning, such as "신청 가능성은 사실상 없어 보입니다" (there is effectively no chance of applying). The revised rule looks only at the conclusion in the first sentence, and the result is 0 assertions in the wrong direction. We believe the revised rule is closer to what the answers mean, but the fact remains that the result flipped against the hypothesis after the rule was changed. The next study should preregister the first-sentence rule before collection and rerun the same design to confirm.

Figure 5. The deadline was right, but far fewer answers got everything right

![Of 200 questions, 78 answers gave the correct deadline, and of those, 46 also got the application status and implementing agency right](figures/fig5-loose-strict.svg)

<!-- src: 004-support-programs/analysis/make_figures.py; analysis/out/results.json#preregistered.cells.all -->

### What a shop owner can do today

- Double-check any deadline the AI gives you against the original notice on Bizinfo. In this study, 78 of 200 answers gave the correct deadline and 58 gave a different date.
- When the AI says "I couldn't confirm", that does not mean the program has ended. For 77 of the 100 ongoing notices, the AI reached no conclusion on whether you could apply.
- Use the exact notice title as registered on Bizinfo when you ask. Even asked that way, the AI got the deadline right only about four times in ten. If you shorten the name, you may get the date of a different, similarly named notice.

## 6 Limitations

1. There was a single response system, Claude Sonnet 5.5 with web search, so there is no comparison across models. One agent answered 10 questions in sequence, so earlier questions may have influenced later ones.
2. The application status judging rule was revised after collection (Section 3.6). Because the revised rule looks only at the first sentence, an answer that says it could not confirm in the first sentence and then reaches a conclusion in the body is counted as unknown. The results under the original rule are in Appendix B.
3. The deadline judgment treats every date in a deadline context as a claim about the target notice's deadline. Answers that gave the deadline of a similarly named notice or a previous round, or that introduced a different notice instead and gave its deadline, are therefore counted as wrong. The present rule could not separate out how many of the 58 wrong answers are of this kind.
4. There is a single ground truth source, Bizinfo. Notices not on Bizinfo (those only on Sobiz24 (소상공인24) or only on a local government's own site) are outside the population. Sobiz24 was under maintenance on the collection date and could not be checked.
5. The exact notice title was used in the question. This is an easier condition than the vague way owners actually ask.
6. Eligibility requirements, interest rates, and loan limits are free text and were not judged. A correct deadline and agency do not mean that everything the owner needs was correct.
7. Collection took place at a single point in time, 2026-10-28 to 29. Search results change daily, so asking the same questions again may give different numbers.

## 7 Ethics and conflicts of interest

Notice titles and notice URLs are information that Bizinfo publishes, so they are included as is in the public data. No personally identifiable information was handled. The raw AI answers are not included in the public data. The author's company, Define404, is preparing an AI answer monitoring service and a per-shop AI visibility check. Its own products were not included in the study. There was no external funding.

## 8 Reproducibility

- Public repository: https://github.com/johndefine404/define404-research-public (path 004-support-programs/). The sample, judgments, analysis code, and figure scripts are public. The raw AI answers are excluded.
- Ground truth source: Bizinfo support program notice spreadsheet (received 2026-10-28), sampling/raw/bizinfo_ongoing_20261028.xlsx and bizinfo_expired_20261028.xlsx. Hashes in sampling/raw/SHA256SUMS
- Sample: sampling/draw_sample.py (seed 20261028), output sampling/sample.csv (SHA-256 893f36426392a7fddee39ed59d8a960df959dbc2df6603a8ed0b919fe4a86df5, identical across two runs)
- Questions: collect/question_templates.json v1.0, batches in collect/batches/
- Judging: judge/auto_judge.py (registered rule v1.0, output judge/judged_v10.csv), judge/status_v11.py (revised v1.1, output judge/judged.csv). Rule text in judge/rules.md
- Analysis: analysis/run_analysis.py. Outputs in analysis/out/ (v1.1) and analysis/out_v10/ (v1.0): results.json and tables.md. Every number in the manuscript was copied from these files only
- Figures: analysis/make_figures.py reads the numbers from analysis/out/results.json and produces report/figures/*.svg
- Preregistration: research repository commit 35fac08415747034b71e0be72186a46c8964a352 (2026-10-28 23:41 ICT). prereg.md was committed before collection
- Dependencies: standard library only
- Per-notice summary data (CSV): notice ID, status, jurisdiction, notice title, application period, URL, and judgments (v1.1 and v1.0). The raw AI answers are not included

## References

- Gosciak, J. et al. (2026). LLMs in social services: How does chatbot accuracy affect human accuracy? arXiv:2603.11213. https://arxiv.org/abs/2603.11213
- Vals AI (2026). Public Benefits Bench v1.1. https://www.vals.ai/benchmarks/snap (accessed 2026-10-28)
- Simpson, R. et al. (2026). Confidently Wrong: Exception Chain Collapse in Frontier LLM Rule Evaluation. arXiv:2607.23386. https://arxiv.org/abs/2607.23386
- Kennan, E. et al. (2025). AI-Powered Rules as Code: Experiments with Public Benefits Policy. Georgetown Beeck Center. https://beeckcenter.georgetown.edu/the-digital-benefits-network-and-massive-data-institute-experiment-with-ai-to-translate-public-benefits-policies-into-software-code/
- Vu, T. et al. (2023). FreshLLMs: Refreshing Large Language Models with Search Engine Augmentation. arXiv:2310.03214. https://arxiv.org/abs/2310.03214
- Mallen, A. et al. (2023). When Not to Trust Language Models: Investigating Effectiveness of Parametric and Non-Parametric Memories. arXiv:2212.10511. https://arxiv.org/abs/2212.10511
- Miller, E. (2024). Adding Error Bars to Evals: A Statistical Approach to Language Model Evaluations. arXiv:2411.00640. https://arxiv.org/abs/2411.00640
- Define404 Research (2026). Local404: Does AI say closed neighborhood shops are still open? (Korean). https://define404.com/report/002-local404-closed-shops/

## Appendix A Summary of judging rules

- Application status (v1.1): the first sentence of the answer is taken as the conclusion. A closed-side expression in the first sentence means asserted closed, an open-side expression means asserted open, and neither means unknown. Tentative conclusions such as "it appears that" are counted in their direction. The ground truth is the status of the stratum (open if ongoing, closed if expired).
- Application status (v1.0, registered rule): the answer is split into sentences and the last sentence containing an open or closed expression is taken as the conclusion. Conditional sentences ("if the deadline has passed, you cannot apply") are not conclusions. A sentence containing both expressions is flagged for manual judgment.
- Deadline: all dates in Korean formats such as 2026-11-09, 2026.11.09, 2026년 11월 9일, and 11월 9일 are extracted. A date is in a deadline context if one of the Korean words for deadline, until, close, application period, acceptance period, "applications are", or "acceptance is" appears within 40 characters of it, or if it is immediately preceded by a range marker (~ or "from"). If a date equal to the ground-truth application end date appears in a deadline context, the answer is correct; if only other dates appear, wrong; if none, none.
- Implementing agency: the implementing agency name is the reference. For notices run by a basic local government or directly by the ministry, the supervising ministry and the city, county, or district at the head of the notice title are added to the reference. Spaces, parentheses, and markers such as "foundation" are stripped, and common abbreviations (소진공, 중기부, 중진공, KOTRA, and so on) are treated as equivalent. If the reference name appears in the answer, correct; if only a different agency is named as the implementing or supervising body, wrong.
- Scores: the loose score is a correct deadline; the strict score requires a correct deadline, a correct application status, and an implementing agency that is not wrong.

<!-- src: 004-support-programs/judge/rules.md#1-4, 7 -->

## Appendix B Results under the registered rule v1.0

In accordance with Section 8 of the preregistration, this appendix reports the results of applying the registered judging rule (v1.0) unchanged. The deadline and implementing agency judgments are identical in both versions, so the loose score is the same as in the main text; only the application status and the strict score differ.

Table 6. Rates under the registered rule v1.0 (Wilson 95% confidence intervals in parentheses)

| Group | n | Deadline correct | All correct | Application status correct | Unknown |
|---|---|---|---|---|---|
| All | 200 | 39.0% (32.5–45.9) | 22.5% (17.3–28.8) | 54.5% (47.6–61.3) | 19.5% (14.6–25.5) |
| Central ministry | 100 | 40.0% (30.9–49.8) | 24.0% (16.7–33.2) | 59.0% (49.2–68.1) | 19.0% (12.5–27.8) |
| Local government | 100 | 38.0% (29.1–47.8) | 21.0% (14.2–30.0) | 50.0% (40.4–59.6) | 20.0% (13.3–28.9) |
| Ongoing | 100 | 45.0% (35.6–54.8) | 24.0% (16.7–33.2) | 72.0% (62.5–79.9) | 19.0% (12.5–27.8) |
| Expired | 100 | 33.0% (24.6–42.7) | 21.0% (14.2–30.0) | 37.0% (28.2–46.8) | 20.0% (13.3–28.9) |

<!-- src: 004-support-programs/analysis/out_v10/tables.md#표1 -->

Table 7. Hypothesis tests under the registered rule v1.0 (differences in percentage points, 95% confidence intervals in parentheses)

| Hypothesis | Difference | One-sided p | Holm p | Verdict |
|---|---|---|---|---|
| H1 | -2.0 (-15.5–11.5) | 0.386 | 0.386 | Not supported |
| H2 | +34.0 (22.8–45.2) | 0.000 | 0.000 | Supported |

<!-- src: 004-support-programs/analysis/out_v10/tables.md#표2 -->

Under v1.0, the 100 expired notices were counted as 43 asserted open, 37 asserted closed, and 20 unknown, and the 100 ongoing notices as 72 asserted open, 9 asserted closed, and 19 unknown. The H2 difference is therefore 43.0% minus 9.0%, or +34.0 percentage points. Under v1.1 the same answers give, for expired notices, 0 asserted open, 35 asserted closed, and 65 unknown, and for ongoing notices, 23 asserted open, 0 asserted closed, and 77 unknown. The paired differences between the loose and strict scores under the two versions are 16.5 percentage points (11.3–21.7) and 16.0 percentage points (10.9–21.1) respectively. The 1 answer flagged for manual judgment under v1.0 is counted as unknown in this table; under the v1.1 rule its first sentence is on the closed side, so the rule alone judged it asserted closed.

<!-- src: 004-support-programs/judge/judged_v10.csv (status_claim x status); judge/judged.csv; analysis/out_v10/tables.md#표3; analysis/out/tables.md#표3 -->

## Appendix C Changes from the preregistration

| Item | Preregistered | Executed |
|---|---|---|
| Application status judgment | Last conclusion sentence (v1.0) | First-sentence conclusion (v1.1). v1.0 results in Appendix B |
| Manual judgment by the hub | Judge manually only answers the rule cannot classify, and report the count | 0 cases under v1.1. The 1 answer flagged under v1.0 is counted as unknown in the v1.0 results |
| Collection period | From 2026-10-28, no later than 11-11 | 2026-10-28 to 10-29, all 200 valid |
| Ongoing notices whose deadline passed before the answer time | Exclude from analysis and report the count | None (0 cases) |

<!-- src: 004-support-programs/judge/rules.md#7; 004-support-programs/log.md; 004-support-programs/prereg.md#5, 8 -->
