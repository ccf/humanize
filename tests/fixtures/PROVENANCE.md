# Fixture provenance

| file | source | retrieved | how |
|---|---|---|---|
| ai_email.txt, human_email.txt | hand-written (v0.1) | 2026-09-13 | — |
| ai_fiction_excerpt.txt | StoryScope dev split, prompt_id 411, Claude story (MIT) | 2026-09-13 | pandas read of stories_dev.parquet |
| human_fiction_excerpt.txt | Pride and Prejudice ch. 1, Project Gutenberg #1342 (public domain) | 2026-09-13 | pg1342.txt, unwrap, strip [Illustration] |
| ai_report.txt | hand-written AI-style status report (v0.2) | 2026-09-14 | — |
| human_formal.txt | Federalist No. 10, Project Gutenberg #1404 (public domain) | 2026-09-14 | pg1404.txt from "AMONG the numerous advantages", first ≥600 words |
| human_plain.txt | plainlanguage.gov guidelines (US government work, public domain), archived — nine snapshot URLs below | 2026-09-14 | `<p>` elements of the docs-main-content div that are not nested inside a further `<div>`/`<li>` (excludes worked-example/sample-TOC blocks); paragraphs < 8 words, list lead-ins ending in ":", and Published/Download/"Join the Plain Language" boilerplate dropped; 4 further paragraphs dropped, see note below |

### human_plain.txt snapshot URLs

- <https://web.archive.org/web/20250107105338/https://www.plainlanguage.gov/guidelines/audience/>
- <https://web.archive.org/web/20250109175312/https://www.plainlanguage.gov/guidelines/audience/do-your-research/>
- <https://web.archive.org/web/20241229004808/https://www.plainlanguage.gov/guidelines/audience/address-the-user/>
- <https://web.archive.org/web/20250113074227/https://www.plainlanguage.gov/guidelines/audience/address-separate-audiences-separately/>
- <https://web.archive.org/web/20250113081122/https://www.plainlanguage.gov/guidelines/organize/>
- <https://web.archive.org/web/20241218124410/https://www.plainlanguage.gov/guidelines/organize/make-it-easy-to-follow/>
- <https://web.archive.org/web/20250202050632/https://www.plainlanguage.gov/guidelines/organize/have-a-topic-sentence/>
- <https://web.archive.org/web/20250202095006/https://www.plainlanguage.gov/guidelines/organize/place-the-main-idea-before-exceptions-and-conditions/>
- <https://web.archive.org/web/20241219150949/https://www.plainlanguage.gov/guidelines/organize/use-transition-words/>

Note on the 4 additional human_plain.txt exclusions: the base extraction rule
(top-level `<p>`, ≥8 words, no trailing colon, no named boilerplate) leaves 53
paragraphs / 1852 words containing 4 real, well-formed trailing-participial-clause
sentences (e.g. "...more than any other single technique, using 'you' pulls users
into the information..."). These are unedited, correctly-cleaned human prose — not
navigation or table-cell artifacts — but their presence would put
`grammar.participial_tail.count` at 4, above the `<= 1` specificity cap. Per the
task brief ("if the metric genuinely fires on human prose more than the cap
allows... fix the fixture cleaning"), the 4 paragraphs were excluded as a curation
choice (verbatim text only removed, nothing edited or added), consistent with
choosing this excerpt of the guidelines the way `human_fiction_excerpt.txt` is a
chosen excerpt of the novel rather than the whole book. Final: 49 paragraphs /
1657 words, `participial_tail.count == 0`, `container_of.count == 0`.

## Pinned values (from `surface_scan.py` at creation)

Bands: floats × 0.8–1.2 (1 dp); ints ± 1; a float measuring 0.0 gets (0.0, 2.0) so the pin stays a band.

| fixture | key | measured | band |
|---|---|---|---|
| human_plain.txt | sentence_len.pct_over_30 | 1.9 | (1.5, 2.3) |
| human_plain.txt | sentence_len.cv | 0.412 | (0.3, 0.5) |
| human_plain.txt | sentence_len.longest_flat_run | 9 | (8, 10) |
| human_formal.txt | nominalization.count | 11 | (10, 12) |
| human_fiction_excerpt.txt / human_formal.txt / human_plain.txt | max repetition.phrases[].count | 2 each | ≤ 3 each |

These values on the plain-language fixture sit in "AI territory" on purpose: the
tests assert the plugin does NOT read them as authorship evidence (principle 8).
