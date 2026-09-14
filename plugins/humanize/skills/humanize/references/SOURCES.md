# Sources

Maintainer registry for every study cited in the reference docs. Never loaded
by the skill at runtime — entries carry their citation inline as
`(Author et al. YEAR [key])`. `tests/test_manifests.py` checks that every
`[key]` in `references/*.md` resolves here. "May support" is the rule Bugbot
enforces: only `storyscope-2026` may back a `Base rate:` line; everything else
is cited on `Scan:` / `Rule of thumb:` lines, and model-vs-model sources never
appear as a human/AI rate.

## `storyscope-2026`
Russell, Rajendhran, Pham, Iyyer, Wieting. *StoryScope: Investigating idiosyncrasies in AI fiction.* arXiv:2604.03136, 2026.
URL: https://arxiv.org/abs/2604.03136
Corpus: 61,575 stories — 10,239 human (Books3 anthologies) and five 2026 LLMs; 304 features.
May support: `Base rate:` lines via `data/storyscope_feature_gaps.csv`.
Caveats: fiction only; amateur/anthology human baseline.
Verified: 2026-09-13 (data file computed from the released parquet).

## `reinhart-2025`
Reinhart, Markey, Laudenbach, Pantusen, Yurko, Weinberg, Brown. *Do LLMs write like humans? Variation in grammatical and rhetorical styles.* PNAS 122, 2025 (arXiv:2410.16107).
URL: https://www.pnas.org/doi/10.1073/pnas.2422455122
Corpus: 8,290 parallel human/LLM texts across six registers; Biber features; GPT-4o and Llama 3 (2024-era).
May support: ratios and directions on `Scan:` lines — participial modifiers 5.3×, d = 1.38; nominalization 2.1×, d = 1.23; agentless passives lower in GPT-4o. Never `Base rate:`.
Caveats: 2024-era models; news/academic registers; SI tables not open.
Verified: 2026-09-14 (author list and title confirmed via the arXiv:2410.16107 abstract page; PNAS page returned 403).

## `herbold-2023`
Herbold, Hautli-Janisz, Heuer, Kikteva, Trautsch. *A large-scale comparison of human-written versus ChatGPT-generated essays.* Scientific Reports 13:18617, 2023.
URL: https://www.nature.com/articles/s41598-023-45644-9
Corpus: 90 argumentative topics × human / ChatGPT-3.5 / ChatGPT-4; 658 expert ratings.
May support: direction on nominalization (monotonic 1.06 → 1.56 → 1.73) and the lexical-diversity reversal between model generations.
Caveats: non-native high-school writers; 2023 models; unit of the nominalization measure unstated.
Verified: 2026-09-14 (author list and title confirmed against the Nature article page).

## `jakesch-2023`
Jakesch, Hancock, Naaman. *Human heuristics for AI-generated language are flawed.* PNAS 120(11), 2023 (arXiv:2206.07271).
URL: https://www.pnas.org/doi/10.1073/pnas.2208839120
Corpus: six experiments, N = 4,600, 53,411 judgments on short self-presentation texts.
May support: repeated phrases as the strongest true-source predictor (OR 1.47) and the three backwards reader cues (contractions; grammar errors; long or rare words).
Caveats: GPT-3-era; short bios; reader-belief-vs-reality gaps, not model rates.
Verified: 2026-09-14 (author list and title confirmed via the arXiv:2206.07271 abstract page; PNAS page returned 403).

## `munoz-ortiz-2024`
Muñoz-Ortiz, Gómez-Rodríguez, Vilares. *Contrasting Linguistic Patterns in Human and LLM-Generated News Text.* Artificial Intelligence Review 57:265, 2024.
URL: https://doi.org/10.1007/s10462-024-10903-2
Corpus: 13,371 NYT lead paragraphs (≤ 200 tokens) vs six base (non-instruction-tuned) LLMs.
May support: direction only — humans 31.2% of sentences over 30 words vs 17.5–21.0%; never a threshold.
Caveats: asymmetric prompt; 2023 base models; news register.
Verified: 2026-09-14 (author list and title confirmed via the Semantic Scholar record for this DOI; Springer page sat behind a login wall).

## `rudnicka-2026`
Rudnicka, Juzek. *Beyond "AI Language": The case for the idiolectal nature of LLM output.* arXiv:2608.06589, 2026.
URL: https://arxiv.org/abs/2608.06589
Corpus: prompt-matched 2024 vs 2026 model corpora on one topic; no prompt-matched human corpus.
May support: per-family ranges (safety disclaimers 46% vs 0.2%), the apostrophe-glyph observation, wordlist vintage. No human baseline — never a human/AI rate.
Caveats: single topic; model-vs-model.
Verified: 2026-09-14 (author list and title confirmed via the arXiv abstract page).

## `padmakumar-2024`
Padmakumar, He. *Does Writing with Language Models Reduce Content Diversity?* ICLR 2024 (arXiv:2309.05196).
URL: https://arxiv.org/abs/2309.05196
Corpus: randomized co-writing study, 38 writers × 3 conditions, ~370-word essays.
May support: direction on repeated n-grams and the localization of homogenization to model spans.
Caveats: GPT-3.5-era co-writing; argumentative essays; corpus-level diversity figures.
Verified: 2026-09-14 (author list and title confirmed via the arXiv abstract page).

## `chakrabarty-2025`
Chakrabarty, Laban, Wu. *Can AI writing be salvaged? Mitigating Idiosyncrasies and Improving Human-AI Alignment in the Writing Process through Edits.* CHI 2025.
URL: https://dl.acm.org/doi/full/10.1145/3706598.3713559
Corpus: LAMP — 1,057 paragraphs, 18 MFA-trained editors, 8,035 edit spans.
May support: the 13 container-noun heads of Table 8; line-level edit-span shares.
Caveats: 80% literary fiction; "rare in the human seed paragraphs" is not a corpus baseline.
Verified: 2026-09-14 (author list and title confirmed via the Semantic Scholar record for this DOI; ACM DL page returned a bot challenge).

## `sun-2025`
Sun, Yin, Xu, Kolter, Liu. *Idiosyncrasies in Large Language Models.* ICML 2025 (arXiv:2502.12150).
URL: https://arxiv.org/abs/2502.12150
Corpus: five-way model-of-origin attribution on chat outputs.
May support: model-vs-model attribution facts only. No human baseline — never a human/AI rate; its transformation experiments are detector attacks and are not adopted.
Caveats: attribution accuracy, not prevalence.
Verified: 2026-09-14 (author list and title confirmed via the arXiv abstract page).

## `milicka-2025`
Milička, Marklová, Cvrček. *Benchmark of stylistic variation in LLM-generated texts.* arXiv:2509.10179, 2025.
URL: https://arxiv.org/abs/2509.10179
Corpus: Biber multidimensional analysis over 32 model settings on 500-word continuations, English and Czech.
May support: direction on the passive-bearing dimension (29 of 32 settings away from it) and register non-adaptation.
Caveats: pre-review draft; figure-read values.
Verified: 2026-09-14 (author list and title confirmed via the arXiv abstract page).

## `kobak-2025`
Kobak, González-Márquez, Horvát, Lause. *Delving into LLM-assisted writing in biomedical publications through excess vocabulary.* Science Advances 11, 2025 (arXiv:2406.07016).
URL: https://arxiv.org/abs/2406.07016
Corpus: 15.1M PubMed abstracts, 2010–2024.
May support: the "wordlists decay" vintage note only. Its rate is document presence, not per-1k; never compared to the plugin's rule of thumb.
Caveats: cannot separate direct LLM use from humans absorbing LLM-preferred words.
Verified: 2026-09-14 (author list and title confirmed via the arXiv abstract page).

## `liang-2024`
Liang, Izzo, Zhang, Lepp, Cao, Zhao, Chen, Ye, Liu, Huang, McFarland, Zou. *Monitoring AI-Modified Content at Scale: A Case Study on the Impact of ChatGPT on AI Conference Peer Reviews.* ICML 2024 (arXiv:2403.07183).
URL: https://arxiv.org/abs/2403.07183
Corpus: AI-conference peer reviews; distributional GPT quantification.
May support: the non-native-speaker confound named in its discussion. Its ranked vocabulary tables are excluded as detector material.
Caveats: corpus-level estimator with no single-document form.
Verified: 2026-09-14 (full author list — Weixin Liang, Zachary Izzo, Yaohui Zhang, Haley Lepp, Hancheng Cao, Xuandong Zhao, Lingjiao Chen, Haotian Ye, Sheng Liu, Zhi Huang, Daniel A. McFarland, James Y. Zou — confirmed via the arXiv abstract page).

## `survey-2025`
Terčon, Dobrovoljc. *Linguistic Characteristics of AI-Generated Text: A Survey.* arXiv:2510.05136, 2025 (v1 preprint, no venue).
URL: https://arxiv.org/abs/2510.05136
Corpus: synthesis of 44 studies (lexicon, grammar, other).
May support: direction and replication counts only; no rates.
Caveats: 25 of 44 studies GPT-3.5-era; English in 40 of 44.
Verified: 2026-09-14 (authors — Luka Terčon, Kaja Dobrovoljc — confirmed via the arXiv abstract page).
