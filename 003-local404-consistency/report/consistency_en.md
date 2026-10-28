# Same Shop, 5 Languages: Does the Shop Information an AI Gives Depend on the Language of the Question?

This is a translation. The reference version is the Korean original, version 1: https://define404.com/report/003-local404-language-consistency/

Local404 data note. Claude's answers about 800 ordinary restaurants in Korea, compared again across 5 languages

- Author: Hawon Kim (Define404 Research)
- Date: 2026-10-28
- Type: Data note. The answers collected in Report 2 (Local404) were re-analyzed with new questions. No new queries were made and no new judgments were added.
- Preregistration: research repository commit 7169864 (2026-10-28 23:39 ICT). prereg.md, holding the hypotheses and the analysis plan, was committed before the analysis was run.
- DOI: https://doi.org/10.5281/zenodo.23739008
- Competing interests: the author's organization, Define404, is preparing an AI answer monitoring service and a per-shop AI visibility diagnostic. The company's own products were not included in the study.

## Summary

We asked whether the same shop, put to the same AI in five languages, yields the same amount of shop information. We reused Claude's answers collected in Report 2 (Local404): 800 shops under the Haiku 5.5 memory condition and 100 shops under the two web search conditions, Haiku 5.5 and Sonnet 5.5, together with their judgment labels. In the memory condition, among the 612 shops with answers in all 5 languages, the Korean question named the business type for 38.2% of shops, while the average of the other 4 languages was 20.6%, a gap of 17.6 percentage points (pp; 95% confidence interval 15.1 to 20.2). H1 was supported. In the two web search conditions (70 shops), the gaps were 3.9 pp and 3.2 pp, and their confidence intervals included 0. When the business type was named, it was correct 71.6 to 79.1% of the time, similar across languages.

### Key findings

- Across 612 shops in the memory condition, the Korean question named the business type for 38.2% of shops and the other 4 languages averaged 20.6%. Gap 17.6 pp (15.1 to 20.2), Holm-adjusted p < 0.001, preregistered hypothesis H1 supported.
- By language: Vietnamese 29.2%, Chinese 24.2%, Japanese 18.0%, English 10.9%. Korean and English diverged most often (187 of 612 shops, 30.6%).
- In the web search conditions with 70 shops, the gaps were small: 3.9 pp (-0.9 to 8.8) and 3.2 pp (-5.1 to 11.5). With 70 shops, small differences cannot be detected.
- Among answers that named a business type, the share that was correct was Korean 77.4%, English 71.6%, Japanese 76.4%, Chinese 79.1%, Vietnamese 73.2%. Naming it more often did not mean getting it right more often.

<!-- src: 003-local404-consistency/analysis/out/h1.csv; h2.csv; holm.csv; explore_correctness.csv; explore_pairs.csv -->

## 1 Introduction

When a foreign customer asks an AI in their own language, "What kind of restaurant is this?", do they get the same answer as someone asking in Korean? Report 2 (Local404) asked about the operating status, address, and business type of 800 restaurants in 5 languages and checked the answers against public licensing records. The Claude models almost never committed to an operating status, so cross-language agreement on that judgment (Report 2, H5) sat near the floor. Business type appeared in 18 to 30% of answers, but it was reported only as totals per system. Whether answers diverged by language within the same shop was not examined.

This note fills that gap. It asks no new questions; it reuses the answers and judgment labels from Report 2, but the questions and the analysis plan were recorded in the repository before the analysis began. There are three questions. Does the Korean question name the business type more often than the other languages (H1, and H2 for the web search conditions)? Is cross-language disagreement more common among shops registered on Kakao Places (H3)? Which language pairs diverge, and when they do, which side is correct (exploratory)?

## 2 Related work

Several studies report that multilingual language models recall the same fact differently depending on the language. Jiang et al. (2020) found across 23 languages that factual recall is higher for languages with more data, and Kassner et al. (2021) reported language bias in factual recall across 53 languages. Qi et al. (2023) proposed a metric that separates cross-language consistency from accuracy, and Chua et al. (2024) reported that even recent large models fail to carry deep knowledge across languages. These studies measured encyclopedic facts with fill-in-the-blank or multiple-choice formats. Within the scope we checked, we found no report that compared free-form answers about small businesses in a specific region across languages under real usage conditions.

## 3 Method

Figure 1. How the study was done

![The 4,000 answers from the previous study were taken out again, the questions were recorded first, each answer was marked for whether it named a business type, and then languages were compared within the 612 shops that had answers in all 5 languages](figures/fig1-flow.svg)

<!-- src: 003-local404-consistency/analysis/make_figures.py; analysis/out/data_inventory.csv -->

### 3.1 Data

No new sample was drawn. The inputs were the Report 2 sample of 800 shops (400 open, 400 closed), the web search subsample of 100 shops, and the single judgment results file that Report 2 published (judgments.csv, 7,312 rows). The raw answer text was not used. The question was a single sentence asking about operating status, address, and business type together, and the shop name and district were written in Korean in every language (Report 2, Appendix A).

Table 1. Data composition

| Condition | Model | Answers | Shops | Answers excluded as "other" business category | Shops with all 5 languages |
|---|---|---|---|---|---|
| Memory condition | Claude Haiku 5.5, no tools | 4,000 | 800 | 940 | 612 |
| Search condition (Haiku) | Claude Haiku 5.5, web search | 500 | 100 | 150 | 70 |
| Search condition (Sonnet) | Claude Sonnet 5.5, web search | 500 | 100 | 150 | 70 |
| Memory condition (Llama) | Llama 3.1 8B, English, Japanese, Korean only | 2,312 | 800 | 539 | 0 |

<!-- src: 003-local404-consistency/analysis/out/data_inventory.csv -->

Llama was excluded from the confirmatory analysis because it lacks all 5 languages; only the 3-language consistency of its operating status judgments was examined as an exploratory check. Undetermined labels numbered 0 for both business type and address in all three Claude conditions.

### 3.2 Measurement and judgment

The judgment labels were taken directly from Report 2's dictionary-based judgment and LLM-assisted judgment, with no new judge added. A business type mention is coded 1 if the business type label is correct or incorrect, and 0 if absent. Answers that Report 2 excluded from business type judgment because the true category was "other" (940 answers in the memory condition) were treated as missing. Shop-level comparisons used only shops with values in all 5 languages (612 shops in the memory condition, 70 in each search condition). A shop with a mention disagreement is one where only some of the 5 languages named the business type.

### 3.3 Analysis

The analysis follows the preregistration (commit 7169864). H1 is the mean of the paired difference, computed for each shop in the memory condition as the Korean mention (0/1) minus the mean mention of the other 4 languages, with a 95% confidence interval from shop-clustered standard errors. H2a (Sonnet search) and H2b (Haiku search) use the same statistic. H3 compares the share of shops with a mention disagreement in the memory condition between Kakao-registered and unregistered shops as two independent groups. The 4 two-sided p-values were Holm-adjusted as one family, and a hypothesis was judged supported when the adjusted p < 0.05 and the sign of the difference matched the hypothesized direction. Cells with fewer than 40 observations were not interpreted, and analyses not in the preregistration are marked as exploratory. The smallest detectable difference was recorded in advance as about 4 to 7 pp for the 800 shops in the memory condition and about 11 to 20 pp for the 100 shops in the search conditions (5% two-sided significance level, 80% power).

## 4 Results

### 4.1 Preregistered hypotheses

Table 2. Results of the preregistered hypothesis tests (differences in pp, 95% confidence intervals in parentheses)

| Hypothesis | Condition | Comparison | Shops | Difference | Two-sided p | Holm p | Verdict |
|---|---|---|---|---|---|---|---|
| H1 | Memory condition | Korean 38.2% vs. mean of other 4 languages 20.6% | 612 | 17.6 (15.1 to 20.2) | < 0.001 | < 0.001 | Supported |
| H2a | Search condition (Sonnet) | Korean 45.7% vs. mean of others 41.8% | 70 | 3.9 (-0.9 to 8.8) | 0.112 | 0.240 | Not supported |
| H2b | Search condition (Haiku) | Korean 42.9% vs. mean of others 39.6% | 70 | 3.2 (-5.1 to 11.5) | 0.447 | 0.447 | Not supported |
| H3 | Memory condition | Share of disagreeing shops, Kakao-registered 39.0% (310 shops) vs. unregistered 46.0% (302 shops) | 612 | -7.0 (-14.8 to 0.8) | 0.080 | 0.240 | Not supported (opposite direction) |

<!-- src: 003-local404-consistency/analysis/out/h1.csv; h2.csv; h3.csv; holm.csv -->

H1 was supported. For the same 612 shops, the Korean question named the business type for 38.2% of shops and the other 4 languages averaged 20.6%. The confidence interval of the paired difference of 17.6 pp (15.1 to 20.2) is well above the detectable difference recorded in advance (4 to 7 pp). Paired differences by language are given in Table 3.

Figure 2. Which language gets the business type named?

![In the memory condition, for the same 612 shops, the share of answers that named a business type was Korean 38.2%, Vietnamese 29.2%, Chinese 24.2%, Japanese 18.0%, English 10.9%. Korean is 17.6 pp above the average of the others](figures/fig2-h1-by-language.svg)

<!-- src: 003-local404-consistency/analysis/make_figures.py; analysis/out/h1.csv -->

Table 3. Business type mention rate by language in the memory condition and paired difference from Korean (612 shops, descriptive statistics outside the preregistration)

| Language | Mention rate | Difference from Korean (pp, 95% CI) |
|---|---|---|
| Korean | 38.2% | Reference |
| Vietnamese | 29.2% | 9.0 (6.4 to 11.6) |
| Chinese | 24.2% | 14.1 (10.5 to 17.6) |
| Japanese | 18.0% | 20.3 (17.0 to 23.5) |
| English | 10.9% | 27.3 (23.5 to 31.1) |

<!-- src: 003-local404-consistency/analysis/out/h1.csv (confirmatory=False 행) -->

H2a and H2b were not supported. In the two conditions with web search turned on, the gaps were 3.9 pp and 3.2 pp and the confidence intervals included 0. Since the detectable difference with 70 shops is about 11 to 20 pp, this should be read not as "there is no difference" but as "differences below this size cannot be seen." In both search conditions the mention rate itself was higher than in the memory condition (the sets of shops differ, so this is not a paired comparison).

Figure 3. What happens with web search turned on?

![In the web search conditions with 70 shops, the share that named a business type was Sonnet Korean 45.7% vs. others' mean 41.8%, Haiku Korean 42.9% vs. 39.6%. The differences are within the margin of error](figures/fig3-search-no-gap.svg)

<!-- src: 003-local404-consistency/analysis/make_figures.py; analysis/out/h2.csv -->

H3 went in the opposite direction. The share of shops with a mention disagreement was 39.0% for Kakao-registered shops (310 shops) and 46.0% for unregistered shops (302 shops), so registered shops were actually 7.0 pp lower (-14.8 to 0.8). This contradicts the premise of the preregistration, that unregistered shops would be easier to agree on because the model would stay silent in every language.

### 4.2 Exploratory: which language pairs diverge

Among the 612 shops in the memory condition, 260 (42.5%; Wilson 95% confidence interval 38.6 to 46.4) had only some of the 5 languages naming the business type. For open shops (282), the share was 51.4% (45.6 to 57.2); for closed shops (330), 34.8% (29.9 to 40.1). In the search conditions, it was 27 of 70 shops for Haiku (38.6%; 28.0 to 50.3) and 26 of 70 for Sonnet (37.1%; 26.8 to 48.9).

Table 4. Business type mention disagreement by language pair (memory condition, 612 shops, Wilson 95% confidence intervals in parentheses)

| Language pair | Disagreeing shops | Only the first language named it | Only the second language named it |
|---|---|---|---|
| Korean, English | 187 (30.6%; 27.0 to 34.3) | 177 | 10 |
| Korean, Chinese | 134 (21.9%; 18.8 to 25.3) | 110 | 24 |
| Korean, Japanese | 130 (21.2%; 18.2 to 24.7) | 127 | 3 |
| Korean, Vietnamese | 69 (11.3%; 9.0 to 14.0) | 62 | 7 |
| English, Chinese | 153 (25.0%; 21.7 to 28.6) | 36 | 117 |
| English, Vietnamese | 150 (24.5%; 21.3 to 28.1) | 19 | 131 |
| English, Japanese | 129 (21.1%; 18.0 to 24.5) | 43 | 86 |
| Japanese, Chinese | 124 (20.3%; 17.3 to 23.6) | 43 | 81 |
| Chinese, Vietnamese | 115 (18.8%; 15.9 to 22.1) | 42 | 73 |
| Japanese, Vietnamese | 105 (17.2%; 14.4 to 20.3) | 18 | 87 |

<!-- src: 003-local404-consistency/analysis/out/explore_pairs.csv (system=H-mem) -->

In pairs that include Korean, it was almost always only the Korean side that named the business type. Of the 187 shops where Korean and English diverged, 177 were shops where only Korean named it.

### 4.3 Exploratory: when named, was it correct?

Table 5. Share of correct answers among those that named a business type (memory condition, answer level, shop-clustered 95% confidence intervals)

| Language | Answers naming a business type | Share correct |
|---|---|---|
| Korean | 234 | 77.4% (72.0 to 82.7) |
| English | 67 | 71.6% (60.8 to 82.5) |
| Japanese | 110 | 76.4% (68.4 to 84.3) |
| Chinese | 148 | 79.1% (72.5 to 85.6) |
| Vietnamese | 179 | 73.2% (66.7 to 79.7) |

<!-- src: 003-local404-consistency/analysis/out/explore_correctness.csv (system=H-mem, kind=match_rate_among_said) -->

The share correct ranged from 71.6 to 79.1% across languages, with overlapping confidence intervals. Among the 210 shops where two or more languages named a business type, only 4 (1.9%; 0.7 to 4.8) had one language correct and another incorrect. Pair-level counts of which language was the correct one come to 2 to 6 cases per language, and the number of answers naming a type per language in the two search conditions is 26 to 32, so these are not interpreted.

Figure 4. Was the named business type correct?

![In the memory condition, among answers that named a business type, the share correct was Korean 77.4%, English 71.6%, Japanese 76.4%, Chinese 79.1%, Vietnamese 73.2%. The differences between languages are small](figures/fig4-correct-when-said.svg)

<!-- src: 003-local404-consistency/analysis/make_figures.py; analysis/out/explore_correctness.csv -->

### 4.4 Exploratory: address and Llama

Addresses were almost never given, whichever language was used. Across the 800 shops in the memory condition, the share of answers giving an address was 1.2% for Korean and 1.3% on average for the other 4 languages, a gap of -0.1 pp (-0.4 to 0.3), and 7 shops (0.9%; 0.4 to 1.8) had an address in only some languages. In the search conditions, it was 11 of 100 shops for Haiku (11.0%; 6.3 to 18.6) and 8 for Sonnet (8.0%; 4.1 to 15.0). Fewer than 40 answers per language gave an address, so accuracy is not interpreted. For Llama 3.1 8B, among the 230 shops where the operating status judgment was determined in all of Korean, English, and Japanese, 97 (42.2%; 36.0 to 48.6) had judgments that differed between languages, and 0 shops had "open" and "closed" directly contradicting each other.

<!-- src: 003-local404-consistency/analysis/out/explore_address.csv; explore_lmem_status.csv -->

## 5 Discussion

In the memory condition, Claude Haiku named the business type of the same shop most often when asked in Korean and least often when asked in English. That Vietnamese came second after Korean is hard to explain by the earlier finding alone that recall is higher for languages with more data (Jiang et al. 2020).

Figure 5. Same shop, different answers by language

![In the memory condition, 260 of 612 shops (42%) had the business type named in some languages and not in others, while the rest had all 5 languages either naming it or not naming it](figures/fig5-split-shops.svg)

<!-- src: 003-local404-consistency/analysis/make_figures.py; analysis/out/explore_inconsistency.csv -->

How often the business type was named differed by language, but the share correct was similar. Among shops where two or more languages named it, judgments diverged in only 1.9%. Language changed whether the model answered, and barely changed whether the answer was right. The reason Qi et al. (2023) gave for looking at consistency and accuracy separately shows up in this data too. With web search turned on, the language gap shrank and the mention rate rose. This may be because search reached the same sources regardless of language, but with a sample of 70 shops the possibility of a small remaining difference stays open.

Some of the answers that named a business type in the memory condition may have guessed it from the shop name. If the name contains a word like "chicken" or "sashimi house," the AI can name a business type without knowing the shop, and that guess may come more easily with a Korean question. This possibility was not checked with the present data.

### What a shop can do right away

- Ask an AI about your shop directly, in the language your foreign customers use. For 177 of 612 shops, the business type that was named when asked in Korean was not named when asked in English.
- If the Korean answer is wrong, the answers in other languages are probably wrong too. Among the 210 shops where two or more languages named a business type, judgments diverged for only 4.
- An AI with web search turned on showed small differences by language (based on 70 shops). The result depends on which kind of AI is describing the shop.

## 6 Limitations

1. The judgments are Report 2's dictionary-based and LLM-assisted judgments. Agreement between the two methods on business type was 73% (kappa 0.46, Report 2, Table 7), so both whether a type was mentioned and whether it was correct carry judgment error.
2. The two search conditions have 70 shops, so their power is low. "Not supported" does not mean "no difference."
3. Whether the Korean question named the type more often because of the model's language-specific knowledge, because of differences in the question wording (the shop name and district were written in Korean in every language), or because the type was guessed from the shop name cannot be determined. The effects of Report 2's collection environment and instructions cannot be separated either.
4. Collection took place at a single point in time, from 2026-10-21 to 24.

## 7 Ethics and competing interests

Shop names and addresses of sole proprietors were removed from the public data, and this note did not use the raw answer text. The author's organization, Define404, is preparing an AI answer monitoring service and a per-shop AI visibility diagnostic. The company's own products were not included in the study. There was no external funding.

## 8 Reproduction

- Input: the judgment results from the Report 2 public repository, 001-local404/analysis/out_final/judgments.csv (SHA-256 37220e4ee92e815a968f91d1b4c80f4b3e84aa0d95e3415fc269bb3fab01bf26). https://github.com/johndefine404/define404-research-public
- Statistics code: Report 2's 001-local404/analysis/stats_lib.py (SHA-256 206d5e4191f0c436305866daa90ca328b92afde972cb908aefac0f0101ae94fb), used without modification
- Analysis code: 003-local404-consistency/analysis/run_analysis.py. Run with python analysis/run_analysis.py. Fake-input test: analysis/tests/test_fake_input.py
- Results: h1.csv, h2.csv, h3.csv, holm.csv, explore_*.csv, data_inventory.csv, results.json in analysis/out/. Every number in the manuscript was copied from these files only
- Figures: analysis/make_figures.py reads the numbers from the results files and produces report/figures/*.svg
- Preregistration: research repository commit 7169864742847ee54118b42f23ef2285f705e97d (2026-10-28T23:39:04+07:00). prereg.md was committed before the analysis was run
- Dependencies: numpy, pandas, scipy (analysis/requirements.txt)

## References

- Chua, L. et al. (2024). Crosslingual Capabilities and Knowledge Barriers in Multilingual Large Language Models. arXiv:2406.16135. https://arxiv.org/abs/2406.16135
- Jiang, Z., Anastasopoulos, A., Araki, J., Ding, H., Neubig, G. (2020). X-FACTR: Multilingual Factual Knowledge Retrieval from Pretrained Language Models. arXiv:2010.06189. https://arxiv.org/abs/2010.06189
- Kassner, N., Dufter, P., Schütze, H. (2021). Multilingual LAMA: Investigating Knowledge in Multilingual Pretrained Language Models. arXiv:2102.00894. https://arxiv.org/abs/2102.00894
- Qi, J., Fernández, R., Bisazza, A. (2023). Cross-Lingual Consistency of Factual Knowledge in Multilingual Language Models. arXiv:2310.10378. https://arxiv.org/abs/2310.10378
- Define404 Research (2026). Local404: Does AI say closed neighborhood shops are still open? (Korean). https://define404.com/report/002-local404-closed-shops/
