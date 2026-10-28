# When You Ask an AI for the Foreign-Language Name of a Korean Dish, How Often Does It Match the Government Standard?

This is a translation. The reference text is the Korean original, version 1: https://define404.com/report/004-hansik-menu-translation/

A study that asked a web-search-enabled Claude for the English and Japanese menu names of 180 Korean dishes and compared the answers with the Korean Food Promotion Institute's standard romanization and translation

- Author: Define404 Research
- Date: 2026-10-29
- Preregistration: research repository commit 9f84ace (2026-10-28 23:41 ICT)
- DOI: https://doi.org/10.5281/zenodo.23739014
- Competing interests: The author's organization, Define404, is preparing an AI audit service for small shops and is considering a foreign-language menu check as one of its items. Its own product was not a subject of this study.

## Summary

We examined whether a shop owner who asks an AI assistant for the English or Japanese name of a Korean dish receives the same answer as the standard published by the government. The reference answers were the 778 entries of the "Foreign-Language Names of Korean Dishes" list on the Korean Food Promotion Institute's Hansik Portal. We drew 180 dishes stratified across 11 food categories and, in the setting of an owner preparing a menu, asked Claude Sonnet 5.5 with web search 180 questions each in English and in Japanese. We extracted one menu name from each answer and compared it with the standard by rule. After normalization, the share of answers identical to the standard (strict match) was 18.3% for English and 18.3% for Japanese, the same. The primary hypothesis that English would be higher than Japanese was not supported. When similar answers were also counted (loose match or better), the two diverged: 75.0% for English and 40.0% for Japanese. Only 2 of 360 answers cited the government standard site as a source, so the secondary hypothesis was not interpreted.

### Key results

- Answers written exactly as the government standard: 33 of 180 in English (18.3%; 95% confidence interval 13.4~24.6) and likewise 33 of 180 in Japanese (18.3%; 13.4~24.6). The paired difference between the two languages was 0.0%p (-8.2~8.2).
- Counting answers similar to the standard as well: 135 of 180 in English (75.0%; 68.2~80.8) and 72 in Japanese (40.0%; 33.1~47.3). In Japanese, six in ten (60.0%; 52.7~66.9) were names different from the standard.
- Answers that cited the Korean Food Promotion Institute site as a source: 2 of 360 (0.6%; 0.2~2.0). 2 in English, 0 in Japanese.
- The registered rule strips parentheses and compares the main name only. When the explanation inside parentheses is also inspected, answers that contain the standard name are 37.2% in English (30.5~44.5) and 28.3% in Japanese (22.3~35.3) (an exploratory analysis added after seeing the results).

<!-- src: 002-menu-translation/analysis/out/results.json#preregistered.rates_en, rates_ja, H1_en_minus_ja_strict_paired; exploratory.cites_hansik_rate; 002-menu-translation/analysis/out/explore_contains.csv -->

## 1 Introduction

As foreign customers increase, neighborhood restaurants are also making English and Japanese menus. With only a handful of dishes, hiring a translation agency is hard to justify, so the owner asks an AI assistant, "How do I write this dish in English?" To unify foreign-language menu spelling, the government has published standard names under the names of the Ministry of Agriculture, Food and Rural Affairs and the Korean Food Promotion Institute. If the AI gives a name that differs from that standard, the owner ends up with a menu that departs from the standard without knowing it.

This study turned that gap into something measurable. We took the standard names published by the Korean Food Promotion Institute as the reference, asked for the same dishes in English and Japanese, and compared the answers with the standard by rule. Sampling, questioning, judging, and analysis are all code, so the same procedure can be run again. The hypotheses and analysis were committed to the research repository before data collection.

This study measures only whether an answer matches the government standard. An answer that differs from the standard is not necessarily a wrong translation. Still, the standard is the government's published reference for unifying menu spelling, so an owner who copies the AI's answer as is will end up with a menu that departs from the standard.

The contributions are three. First, to the best of our knowledge (within the scope checked in Section 2), this is the first measurement comparing AI answers about Korean dish names with the official government standard. Second, English and Japanese were compared on the same dishes, as pairs. Third, the source collection, seed-fixed sampling, rule-based judging, and analysis code are public, so the same study can be repeated with another AI or at another time.

## 2 Related work

Only studies whose full text we opened and checked are listed (checked 2026-10-28).

Yao et al. (2024) built a parallel corpus containing culture-specific items for 6 language pairs and reported that large language models use cultural knowledge in translation better than neural machine translation does[1]. Korean menus were not treated separately. Zhang et al. (2024) built a Chinese-English menu dataset and proposed automatic identification of culture-specific items and translation strategies[2]. Only Chinese menus were covered. Yuan et al. (2026) proposed a novel-based culture-aware translation dataset and evaluation framework; whether Korean is included is not stated in the abstract[3]. Zeng et al. (2026) evaluated 12 multimodal models in 10 languages with 4,870 multiple-choice questions on menu and cooking images[4]. Translation answers were not compared with a government standard. Lee (2025) compared ChatGPT and Papago on Korean-to-English translation of 590 pairs of drama dialogue and did not cover food names[5].

None of the five measured how closely a web-search-enabled AI assistant matches the official government standard for Korean dish names. This study fills that gap.

<!-- src: 002-menu-translation/gate.md#3 -->

## 3 Methods

Figure 1. How we did the study

![The order of steps: draw 180 Korean dishes, ask in English and Japanese, and sort the 360 answers from a web-search-enabled Claude against the government standard into identical, similar, and different](figures/fig1-flow.svg)

<!-- src: 002-menu-translation/analysis/make_figures.py; 002-menu-translation/analysis/out/results.json -->

### 3.1 Reference source and sample

The reference source is the "Foreign-Language Names of Korean Dishes" table on the Korean Food Promotion Institute's Hansik Portal (hansik.or.kr, collected 2026-10-28, 778 entries). Its columns are number, dish name, romanization, English, Japanese, and Simplified and Traditional Chinese, and the listed sources are the Ministry of Agriculture, Food and Rural Affairs, the Korean Food Promotion Institute, the Ministry of Culture, Sports and Tourism, the National Institute of Korean Language, the Korea Tourism Organization, and the Rural Development Administration. There were no empty cells or duplicate dish names, so no rows were removed. The SHA-256 of the collected file is in Section 8.

The strata are 11 food categories determined by the final word of the Korean dish name. Each stratum was allocated in proportion to the population with a minimum of 5, for 180 dishes in all. Candidates within a stratum were sorted by number, shuffled with seed 20261028, and filled from the front. The sample size was set to 180 to cover the 175 needed to detect a paired difference of 15%p between the two languages in the primary hypothesis at a 5% significance level (one-sided) with 80% power. The variance of the paired difference was taken at its worst case, with the two languages' answers uncorrelated and a proportion of 0.5.

Table 1. Sample composition (food categories were assigned by a final-word rule on the dish name and may differ from official classifications)

| Food category | Population | Sample |
|---|---|---|
| Grilled, stir-fried, and deep-fried | 174 | 40 |
| Seasoned vegetables, kimchi, and side dishes | 133 | 30 |
| Soups | 106 | 24 |
| Rice and porridge | 92 | 21 |
| Steamed, braised, and boiled meat | 74 | 17 |
| Noodles | 51 | 11 |
| Other | 44 | 10 |
| Stews and hot pots | 39 | 9 |
| Rice cakes, confections, and drinks | 38 | 8 |
| Set meals | 7 | 5 |
| Sauces and seasonings | 20 | 5 |
| Total | 778 | 180 |

<!-- src: 002-menu-translation/prereg.md#3; 002-menu-translation/sampling/sample_v1_log.txt -->

### 3.2 Questions

One question per dish per language: 180 in English and 180 in Japanese. Each question was written from the standpoint of an owner running a Korean restaurant in Korea who is making a foreign-language menu, and asked for one menu name on the first line in the form "NAME: ..." followed by one or two sentences of explanation. The dish name was inserted in its Korean spelling for both languages. The words standard, Korean Food Promotion Institute, and guide did not appear in the questions. The question templates are in Appendix A (collect/question_templates.json v1.0).

For each language, the questions were shuffled with seed 20261028 and split into 18 batches of 10. Each batch is one language and distinct dishes.

### 3.3 Response system

Table 2. Response system

| Model | Condition | Questions | Valid answers |
|---|---|---|---|
| Claude Sonnet 5.5 | Web search, search required for every question | 360 (180 English, 180 Japanese) | 360 |

<!-- src: 002-menu-translation/log.md; 002-menu-translation/analysis/out/results.json#n_items -->

The respondent was invoked as a sub-agent and was not told the purpose of the study or the reference answers. The instructions opened by stating that the task was unrelated to any previous conversation and that answers should be in the language of the question. Batches ran 3 at a time in parallel, and collection took place from the night of 2026-10-28 into the 29th. All 360 questions received answers, and no answer skipped the search. One answer noted that its second search was blocked by a limit, but the first search had run, so it was kept as valid. No separate pilot was run; the format was checked on the first 2 batches and those answers were used as data as well.

### 3.4 Judging

The judging rules (judge/rules.md v1.0) were fixed before collection, and only the rule-based automatic judging code (judge/auto_judge.py) was used. One menu-name candidate is extracted from the first "NAME:" line of the answer. If there is more than one candidate, as in "A / B", the first is used, and anything in parentheses is removed. No extraction failed, so the number of answers judged by hand was 0.

For English, the candidate is lowercased, Unicode-normalized (NFKC), stripped of parentheses and punctuation, stripped of articles and of the words and and with, and its romanization variants unified (kimchi/gimchi, tteok/ddeok/dduk, and so on); if it then equals the standard English name, it is a strict match. If the Jaccard coefficient of the word sets is 0.5 or higher, or the candidate contains the standard's romanization in full, it is a loose match. Anything else is a mismatch. For Japanese, the candidate goes through NFKC, removal of spaces, middle dots, long-vowel marks, and parentheses, and the presence or absence of the sokuon is ignored; if it then equals the standard Japanese name it is a strict match, and if the character 2-gram Dice coefficient is 0.5 or higher or it contains the standard in full it is a loose match. An answer that gives no name or only says it does not know is "not given". If hansik.or.kr appears in the answer's source list, it is marked "cited the standard source".

Table 3. Judging examples (5 of the 180 sampled dishes; standard names quoted from the Korean Food Promotion Institute's Hansik Portal)

| Dish | Language | Standard name | Menu name in the AI answer | Judgment |
|---|---|---|---|---|
| 어간장 (eo-ganjang) | English | Fish Soy Sauce | Fish Soy Sauce (Eo-ganjang) | Strict match |
| 비빔밥 (bibimbap) | Japanese | ビビンバ | ビビンバ | Strict match |
| 새우튀김 (saeu-twigim) | English | Deep-fried Shrimp | Crispy Fried Shrimp | Loose match |
| 계란찜 (gyeran-jjim) | Japanese | 茶碗蒸し | ケランチム(韓国式卵蒸し) | Mismatch |
| 따로국밥 (ttaro-gukbap) | Japanese | タロクッパ | タログッパ(別盛りクッパ) | Mismatch |

<!-- src: 002-menu-translation/judge/judged.csv (M134-en, M014-ja, M148-en, M066-ja, M011-ja) -->

### 3.5 Analysis

The analysis code is analysis/run_analysis.py and uses only the standard library. Every proportion carries a Wilson 95% confidence interval. Because each dish has one answer per language, the dish-level proportion is also the cluster-level proportion. The primary hypothesis H1 computes, for each dish, (English strict match - Japanese strict match) and reports the mean paired difference, its standard error, confidence interval, and a one-sided test. The secondary hypothesis H2 is the difference in strict match rate, among English questions, between answers that cited the standard source and those that did not. The two hypotheses were corrected with the Holm method. Cells with fewer than 40 observations are not interpreted. Analyses not in the preregistration are labeled exploratory, and analyses added after seeing the results are labeled as such.

The preregistration is the commit of prereg.md to the research repository (commit 9f84ace, 2026-10-28 23:41 ICT). Neither prereg.md nor the judging rules were changed after registration.

## 4 Results

### 4.1 Answers identical to the government standard (H1)

Table 4. Judgment distribution by language (parentheses show Wilson 95% confidence intervals; n is 180 for each)

| Judgment | English | Japanese |
|---|---|---|
| Strict match | 33 (18.3%; 13.4~24.6) | 33 (18.3%; 13.4~24.6) |
| Loose match | 102 (56.7%; 49.4~63.7) | 39 (21.7%; 16.3~28.2) |
| Mismatch | 45 (25.0%; 19.2~31.8) | 108 (60.0%; 52.7~66.9) |
| Not given | 0 (0.0%; 0.0~2.1) | 0 (0.0%; 0.0~2.1) |
| Loose or better (strict + loose) | 135 (75.0%; 68.2~80.8) | 72 (40.0%; 33.1~47.3) |

<!-- src: 002-menu-translation/analysis/out/results.json#preregistered.rates_en, rates_ja -->

Figure 2. If you asked about 100 dishes (answer counts scaled to 100 cells and rounded)

![In English, out of 100: 18 identical, 57 similar, 25 different. In Japanese: 18 identical, 22 similar, 60 different](figures/fig2-100-menus.svg)

<!-- src: 002-menu-translation/analysis/make_figures.py; 002-menu-translation/analysis/out/results.json -->

The share of answers whose menu name was identical to the government standard after normalization was 18.3% for English and 18.3% for Japanese, the same. The mean paired difference across the 180 dishes was 0.0%p (95% confidence interval -8.2~8.2), one-sided p=0.500, Holm-adjusted p=1.000. H1, that the English strict match rate is higher than the Japanese, was not supported. Both languages gave a menu name for every question.

Table 5. Results of the preregistered hypothesis tests

| Hypothesis | Result |
|---|---|
| H1 English > Japanese (strict match, paired) | 18.3% vs 18.3%. Paired difference 0.0%p (-8.2~8.2), one-sided p=0.500, Holm p=1.000. Not supported |
| H2 Cited the standard source > did not cite (English strict match) | Cited: 2 questions (0/2); not cited: 178 questions (33/178, 18.5%; 13.5~24.9). The cited cell has fewer than 40, so not interpreted |

<!-- src: 002-menu-translation/analysis/out/results.json#preregistered.H1_en_minus_ja_strict_paired, H2_strict_by_hansik_citation_en -->

### 4.2 Counting similar answers too (loose match)

Figure 3. When similar answers also count, English rises a lot and Japanese rises less

![Answers written identically are 18% in English and 18% in Japanese, the same, but answers written at least similarly are 75% in English and 40% in Japanese](figures/fig3-strict-vs-loose.svg)

<!-- src: 002-menu-translation/analysis/make_figures.py; 002-menu-translation/analysis/out/results.json -->

The "loose or better" share, strict plus loose matches, was 75.0% for English (68.2~80.8) and 40.0% for Japanese (33.1~47.3). English answers often shared more than half their words with the standard or contained the standard's romanization (loose match 56.7%). In Japanese, names different from the standard were the largest cell at 60.0% (52.7~66.9). Cases like gyeran-jjim in Table 3, where the standard is a Japanese translation (茶碗蒸し) but the answer writes the Korean pronunciation in katakana (ケランチム), fall here. The difference in loose-or-better rates between languages is an exploratory analysis, not a preregistered hypothesis.

### 4.3 Answers that cited the government standard site (H2)

Figure 4. Almost no answer cited the government standard site as a source

![When the 360 answers are laid out as dots, only 2 cited the Korean Food Promotion Institute site as a source](figures/fig4-cited-hansik.svg)

<!-- src: 002-menu-translation/analysis/make_figures.py; 002-menu-translation/analysis/out/results.json -->

Of the 360 answers, 2 (0.6%; 0.2~2.0) had the Korean Food Promotion Institute site (hansik.or.kr) in their source list. That is 2 of 180 in English (1.1%; 0.3~4.0) and 0 of 180 in Japanese (0.0%; 0.0~2.1). The 2 were the English answers for dongtae-jeon (동태전) and ttaro-gukbap (따로국밥), and both were loose matches. With only 2 questions in the cited group, H2 was not interpreted. The strict match rate among the 178 questions that did not cite was 18.5% (13.5~24.9). Even though a web search was run for every question, the answers almost never reached the government standard site.

<!-- src: 002-menu-translation/analysis/out/results.json#exploratory.cites_hansik_rate; 002-menu-translation/analysis/out/explore_contains.csv (all, cites_hansik_or_kr); 002-menu-translation/judge/judged.csv (cites_hansik=1: M145-en, M011-en) -->

### 4.4 Exploratory analyses

English strict match rates by food category are in Table 6. The only cell with 40 or more observations is grilled, stir-fried, and deep-fried (40), and its strict match rate is 25.0% (14.2~40.2). The remaining cells have fewer than 40 and are not interpreted.

Table 6. English strict match by food category (exploratory; cells under 40 not interpreted)

| Food category | n | Strict match | Rate (95% CI) | Interpretation |
|---|---|---|---|---|
| Grilled, stir-fried, and deep-fried | 40 | 10 | 25.0% (14.2~40.2) | Interpreted |
| Seasoned vegetables, kimchi, and side dishes | 30 | 1 | 3.3% (0.6~16.7) | Under 40 |
| Soups | 24 | 8 | 33.3% (18.0~53.3) | Under 40 |
| Rice and porridge | 21 | 5 | 23.8% (10.6~45.1) | Under 40 |
| Steamed, braised, and boiled meat | 17 | 6 | 35.3% (17.3~58.7) | Under 40 |
| Noodles | 11 | 0 | 0.0% (0.0~25.9) | Under 40 |
| Other | 10 | 0 | 0.0% (0.0~27.8) | Under 40 |
| Stews and hot pots | 9 | 1 | 11.1% (2.0~43.5) | Under 40 |
| Rice cakes, confections, and drinks | 8 | 1 | 12.5% (2.2~47.1) | Under 40 |
| Set meals | 5 | 0 | 0.0% (0.0~43.4) | Under 40 |
| Sauces and seasonings | 5 | 1 | 20.0% (3.6~62.4) | Under 40 |

<!-- src: 002-menu-translation/analysis/out/results.json#exploratory.strict_by_category_en -->

Among the 45 English mismatches, "ingredient mismatches", where the standard's key ingredient word is missing and a different ingredient word appears, number 2 (4.4%; 1.2~14.8). Most English mismatches differed in phrasing, not in ingredient. Multiple names and extraction failures were both 0.

<!-- src: 002-menu-translation/analysis/out/results.json#exploratory.ingredient_mismatch_among_en_mismatch, flags -->

What follows is an exploratory analysis added after seeing the results. The registered rule strips parentheses and compares the main name only. So an answer with an explanation in parentheses, like "ケランチム(韓国式卵蒸し)", is judged by the name outside the parentheses alone. Counting separately the answers whose entire menu-name line, parentheses included, contains the standard name gives 67 of 180 in English (37.2%; 30.5~44.5) and 51 of 180 in Japanese (28.3%; 22.3~35.3) (analysis/explore_contains.py).

Figure 5. Looking inside the parentheses too (exploratory analysis added after seeing the results)

![Looking at the main name only, answers identical to the standard are 18% in English and 18% in Japanese, but including the explanation in parentheses, answers that contain the standard name are 37% in English and 28% in Japanese](figures/fig5-with-parentheses.svg)

<!-- src: 002-menu-translation/analysis/make_figures.py; 002-menu-translation/analysis/out/explore_contains.csv; 002-menu-translation/analysis/out/results.json -->

## 5 Discussion

Two points are central. First, the probability of receiving a menu name identical to the government standard was about one in five (18.3%) in both English and Japanese, and did not differ by language. Second, once similar answers are counted, English (75.0%) and Japanese (40.0%) diverge sharply. English answers were often descriptive names that shared words with the standard (loose match 56.7%). Japanese answers included names that transcribed the Korean pronunciation into katakana, like gyeran-jjim in Table 3, and such answers share few characters with the standard's Japanese translation. With the same AI, the same dishes, and the same setting, how close the answer came to the standard still changed with the language.

Read from the shop's side, it comes to this. The English menu names the AI gives often carry the same meaning as the standard but are rarely spelled identically. In Japanese, identical spelling is rare, and fewer than half are even written in a form that carries the same meaning. A menu name that differs from the standard is not necessarily a wrong translation, but an owner who wants the menu to follow the government standard should not copy the AI's answer and should check the standard directly.

It stands out that the web search did not reach the government standard site. A search was run for every question, yet only 2 of 360 answers cited the Korean Food Promotion Institute site as a source. Several answers wrote that they could not find an official standard English name (for example, the English answer for usamgyeop-sukju-bokkeum (우삼겹숙주볶음): "I found no official standard English name for this dish"). Even when a standard is public, if it does not rank high in search results, the AI makes up its own name without knowing the standard exists. We did not count these cases, and we did not test the cause.

Looking inside the parentheses raises the share of answers containing the standard name to 37.2% in English and 28.3% in Japanese. That many answers wrote the main name their own way and added the standard name in parentheses. Even so, six in ten English answers and seven in ten Japanese answers had no standard name even inside the parentheses. This analysis was added after seeing the results and is not a hypothesis test.

## 6 Limitations

1. The response system is a single condition, Claude Sonnet 5.5 with web search. The results cannot be generalized to other AI assistants or to conditions without search.
2. There is a single question template. The "NAME:" format requirement and the owner setting may affect the answers, and asking in other words could change the results.
3. Rule-based judging has limits. Because parentheses are stripped and only the main name is compared, an answer that writes the standard name in parentheses becomes a mismatch or a loose match (explored in Section 4.4). Also, an answer with the same meaning but different words is a mismatch. The ttaro-gukbap case in Table 3 (タロクッパ vs タログッパ) became a mismatch over a one-character difference. The loose-match thresholds (Jaccard and Dice 0.5) were set before collection but are arbitrary values.
4. The standard name is one official reference, not the only correct answer. This study did not measure the translation quality of answers that differ from the standard.
5. Food categories were assigned by a final-word rule on the dish name and may differ from official classifications, and only one category cell has 40 or more observations.
6. The responding agent ran inside a Claude Code environment (including user settings and memory), and one agent answered 10 questions in a row, so context effects are possible.
7. The study was run at a single point in time, between 2026-10-28 and the 29th. If the model or the search results change, the results may change too.

## 7 Ethics and competing interests

- No personal data was handled. The questions and answers contain no person names, shop names, or addresses.
- The copyright of the reference source belongs to the Korean Food Promotion Institute (Hansik Portal copyright policy, checked 2026-10-28: copyright held by the Korean Food Promotion Institute, prior consultation required for commercial use, attribution required). For that reason we do not redistribute the source table or the standard names of the 180 sampled dishes; reproduction is through the collection code and file hashes. In the text, only 5 examples are quoted with attribution.
- The author's organization, Define404, is preparing an AI audit service for small shops and is considering a foreign-language menu check as one of its items. Its own product was not a subject of this study, and the study received no external funding.
- Response collection was done within the author's Claude subscription at no additional cost.

## 8 Reproduction

- Public repository: https://github.com/johndefine404/define404-research-public (path 002-menu-translation/). It contains the source collection code, seed-fixed sampling code, question templates, batches, rule-based judging code, analysis code, result files, and our judgments (dish number and judgment only). The source table, the standard name strings, and the raw answers are not included.
- Preregistration: research repository commit 9f84ace0f6d74576686023187776c5c752f7c5ad (2026-10-28 23:41 ICT). prereg.md SHA-256: 4cd0480d1af8b2b66bb10cfc4332a53ecd5806cf9dc3256d209c816a6c912596 (unchanged after registration)
- Judging rules judge/rules.md SHA-256: 76370cd882e392dafe6b093f3d11406acadbcdddb3c91ffde8559d87c5ae7908
- Source table sampling/raw/hansik_menu_800_20261028.csv SHA-256: 620f0fc8be6918a7a5482e66f86086bf7991505bb679e046d28fa837bf4cc26f (re-download with the collection code sampling/fetch_source.py and compare)
- Sample sampling/sample_v1.csv SHA-256: ec8992250598de301cf4acf5872476fcc67912c31a4be47084a303d70517868f, seed 20261028
- Fingerprint of the raw answers (SHA-256 over the hashes of the 36 batch files): b13052316b77ed6865a0cd299816b9eb8d2867187918623dea066321a25faae9
- Analysis results analysis/out/results.json SHA-256: b8b256647b25b729f4f51b42d7d0aff1e8a30167be15925040266355ff8fccab
- Reproduction order: python sampling/fetch_source.py (collect the source, compare hashes) → python sampling/draw_sample.py → python collect/build_batches.py → collect responses → python judge/auto_judge.py → python analysis/run_analysis.py → python analysis/explore_contains.py → python analysis/make_figures.py
- Public summary data (CSV): contains only the rate, confidence interval, and sample size for each indicator. No standard name text is included.
- DOI: to be registered on Zenodo after publication and added here.

<!-- src: 002-menu-translation/log.md; 002-menu-translation/prereg.md#3; shasum -a 256 -->

## What a shop can do right away

1. Do not put the AI's answer on the menu as is; look up the foreign-language dish name yourself in the "Foreign-Language Names of Korean Dishes" list on the Korean Food Promotion Institute's Hansik Portal. In this study, the AI's answer matched the standard exactly about one time in five, in English and in Japanese alike.
2. Check Japanese menus with particular care. Six in ten Japanese answers were names different from the standard, and in some cases the standard was a Japanese translation while the answer wrote the Korean pronunciation in katakana.
3. If the AI's answer has another name added in parentheses, look at that too. Some answers put the standard name in the parentheses. Still, even counting the parentheses, six in ten English answers and seven in ten Japanese answers had no standard name.
4. Asking the AI to "give the Korean Food Promotion Institute's standard name" was not tested in this study. Its effect has not been measured.

## References

1. Yao B., Jiang M., Bobinac T., Yang D., Hu J. Benchmarking Machine Translation with Cultural Awareness. arXiv 2305.14328, v3 2024-10-19. https://arxiv.org/abs/2305.14328
2. Zhang Z., He C., Iyer V., Birch A. Cultural Adaptation of Menus: A Fine-Grained Approach. arXiv 2408.13534, 2024-08-24 (WMT 2024). https://arxiv.org/abs/2408.13534
3. Yuan et al. Culture-Aware Machine Translation in Large Language Models: Benchmarking and Investigation. arXiv 2604.24361, 2026-04-27 (ACL 2026). https://arxiv.org/abs/2604.24361
4. Zeng et al. CulturalMenuBench: Probing the Knowledge-Application Gap in Multimodal Culinary Reasoning. arXiv 2609.03526, 2026-09-03. https://arxiv.org/abs/2609.03526
5. Lee J.-H. A Comparative Study of ChatGPT and Papago Korean-to-English Translations of Dialogue from the Adaptation of Pachinko. International Journal of Contents 21(3), 2025, 138-151. https://www.accesson.kr/ijcon/v.21/3/138/57464
6. Korean Food Promotion Institute. Foreign-Language Names of Korean Dishes (Guide to Foreign-Language Names of 800 Korean Dishes). Hansik Portal, collected 2026-10-28. https://www.hansik.or.kr/board/dn/list/017?menuSn=12

<!-- src: 002-menu-translation/gate.md#1, #3 -->

## Appendix A Question templates

Examples with the fictional dish "하늘비빔밥" inserted. In the actual questions, the Korean name of each sampled dish was inserted in the dish-name slot as is.

| Language | Question |
|---|---|
| English | I run a Korean restaurant in Korea and I'm making an English menu. How should I write the dish '하늘비빔밥' on the menu? Put one English menu name on the first line in the form 'NAME: ...', then add one or two short sentences of explanation. |
| Japanese | 韓国で韓国料理店をやっていて、日本語のメニューを作っています。「하늘비빔밥」という料理はメニューにどう書けばいいですか。1行目に「NAME: ...」の形でメニュー名を1つだけ書いて、そのあとに1〜2文で短く説明してください。 |

<!-- src: 002-menu-translation/collect/question_templates.json v1.0 -->

## Appendix B Summary of judging rules

- Unit: one question is 1 dish x 1 language. The object of judgment is the single menu-name candidate extracted from the answer; the explanatory sentences are not judged.
- Candidate extraction: the text of the first "NAME:" line, otherwise a short first line, otherwise an extraction failure (0 cases in this study). If there is more than one, the first is used and parentheses are removed.
- English normalization: lowercase, NFKC, removal of parentheses, removal of punctuation, hyphens, and slashes, removal of articles and of and, &, and with, unification of romanization variants.
- Japanese normalization: NFKC, removal of spaces, middle dots, long-vowel marks, and parentheses, sokuon ignored.
- Strict match: the normalized candidate equals the normalized standard. Loose match: for English, word-set Jaccard of 0.5 or higher or containing the standard's romanization; for Japanese, character 2-gram Dice of 0.5 or higher or containing the standard. Mismatch: neither. Not given: no answer.
- Cited the standard source: hansik.or.kr appears in the answer's source list.

<!-- src: 002-menu-translation/judge/rules.md#1-5 -->
