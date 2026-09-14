# Fixture provenance

| file | source | retrieved | how |
|---|---|---|---|
| ai_email.txt, human_email.txt | hand-written (v0.1) | 2026-09-13 | — |
| ai_fiction_excerpt.txt | StoryScope dev split, prompt_id 411, Claude story (MIT) | 2026-09-13 | pandas read of stories_dev.parquet |
| human_fiction_excerpt.txt | Pride and Prejudice ch. 1, Project Gutenberg #1342 (public domain) | 2026-09-13 | pg1342.txt, unwrap, strip [Illustration] |
| ai_report.txt | hand-written AI-style status report (v0.2) | 2026-09-14 | — |
| human_formal.txt | Federalist No. 10, Project Gutenberg #1404 (public domain) | 2026-09-14 | pg1404.txt from "AMONG the numerous advantages", first ≥600 words |
| human_plain.txt | plainlanguage.gov guidelines (US government work, public domain), archived — nine snapshot URLs below | 2026-09-14 | mechanical rule only: `<p>` elements anywhere inside the docs-main-content div, in document order, with paragraphs under 8 words dropped, list lead-ins ending in ":" dropped, and Published/Download/"Join the Plain Language" boilerplate dropped; whole paragraphs kept verbatim in page order (audience pages, then organize pages) and the walk stops at the first paragraph that brings the running total to ≥ 600 words — no sentence was removed or reordered inside a kept paragraph |

### human_plain.txt snapshot URLs

All nine pages listed in the task brief were fetched (HTTP 200, no "no captures
found" pages) so the extraction script could walk them in order; the 600-word
stop was reached partway through the third page, so only `audience/`,
`audience/do-your-research/`, and `audience/address-the-user/` contributed text
to the final fixture. The remaining six are recorded here for reproducibility.

- <https://web.archive.org/web/20250107105338/https://www.plainlanguage.gov/guidelines/audience/> (used)
- <https://web.archive.org/web/20250109175312/https://www.plainlanguage.gov/guidelines/audience/do-your-research/> (used)
- <https://web.archive.org/web/20241229004808/https://www.plainlanguage.gov/guidelines/audience/address-the-user/> (used, truncated mid-page at 600 words)
- <https://web.archive.org/web/20250113074227/https://www.plainlanguage.gov/guidelines/audience/address-separate-audiences-separately/> (fetched, unused)
- <https://web.archive.org/web/20250113081122/https://www.plainlanguage.gov/guidelines/organize/> (fetched, unused)
- <https://web.archive.org/web/20241218124410/https://www.plainlanguage.gov/guidelines/organize/make-it-easy-to-follow/> (fetched, unused)
- <https://web.archive.org/web/20250202050632/https://www.plainlanguage.gov/guidelines/organize/have-a-topic-sentence/> (fetched, unused)
- <https://web.archive.org/web/20250202095006/https://www.plainlanguage.gov/guidelines/organize/place-the-main-idea-before-exceptions-and-conditions/> (fetched, unused)
- <https://web.archive.org/web/20241219150949/https://www.plainlanguage.gov/guidelines/organize/use-transition-words/> (fetched, unused)

Result: 19 paragraphs / 606 words, taken verbatim with no sentence-level
exclusions. `grammar.participial_tail.count == 1` (one hit: "...more than any
other single technique, using 'you' pulls users into the information and makes
it relevant to them."), at the `<= 1` specificity cap; `container_of.count == 0`;
`discourse.disclaimer_opener.fired == False`; `repetition.phrases == []`. The
one participial-tail hit is a known metric false positive — a gerund subject
after a fronted adverbial that rule (b) does not yet cover — kept because
fixture content never depends on the metric under test.

## Pinned values (from `surface_scan.py` at creation)

Bands: floats × 0.8–1.2, rounded outward to 2 dp; ints ± 1; a float measuring
0.0 gets (0.0, 2.0) so the pin stays a band; the formal nominalization gate is
a floor (≥ 5), not a band.

| fixture | key | measured | band |
|---|---|---|---|
| human_plain.txt | sentence_len.pct_over_30 | 0.0 | (0.0, 2.0) |
| human_plain.txt | sentence_len.cv | 0.349 | (0.28, 0.42) |
| human_plain.txt | sentence_len.longest_flat_run | 9 | (8, 10) |
| human_formal.txt | nominalization.count | 11 | floor (≥ 5) |
| human_fiction_excerpt.txt / human_formal.txt | max repetition.phrases[].count | 2 each | ≤ 3 each |
| human_plain.txt | max repetition.phrases[].count | 0 (no repeated phrases) | ≤ 1 |

These values on the plain-language fixture sit in "AI territory" on purpose: the
tests assert the plugin does NOT read them as authorship evidence (principle 8).
