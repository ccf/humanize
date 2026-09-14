# Surface tells

The layer StoryScope does not measure: vocabulary, grammar, punctuation,
sentence and paragraph shape, and discourse moves. Applies to every text
class. Each entry names the `surface_scan.py` metric that measures it where
one exists. Ranges marked *rule of thumb* are working heuristics from
practice, not measured in the StoryScope corpus. Numbers that are not
StoryScope base rates sit on `Scan:` or `Rule of thumb:` lines with a `[key]`
that resolves in `SOURCES.md`.

## Vocabulary

### AI-associated wordlist
Looks like: "delve", "tapestry", "a testament to", "navigate the complexities",
"it's worth noting", "leverage", "robust", "seamless", "crucial", "pivotal",
"foster", "underscore", "multifaceted", "landscape", "vibrant", "nuanced",
"meticulous", "harness", "synergy", "holistic", "streamline", "elevate",
"empower", "unlock", "resonate", "realm", "beacon", "unwavering".
Scan: `wordlist.rate` per 1k words and `wordlist.hits` with sentence positions.
Rule of thumb: human drafts usually < 3/1k; AI drafts commonly 10–30/1k in
long-form prose and can exceed 60/1k in short business emails, where
boilerplate dominates.
Vintage: calibrated on 2023–2024 model output. A wordlist decays — Kobak et
al. 2025 [kobak-2025] tracked one marker's excess falling roughly fivefold
within a year (share of biomedical abstracts containing the word, not a per-1k
rate; not comparable to the rule of thumb above). Re-check against current
models before firing hard.
Why it reads as AI: these words are over-represented in RLHF-era model output
and under-represented in ordinary human prose of the same register; readers
have learned the list.
Fix: removal — replace with the plain word the author would use ("use" for
"leverage", "strong" for "robust", "important" for "crucial") or cut the word
entirely; most are decorative.

### Latinate lean
Looks like: "utilize", "facilitate", "demonstrate", "commence", "implement",
"ascertain" where "use", "help", "show", "start", "do", "find out" would do.
Base rate: AI 2.83 / human 2.51 on a 1–5 Anglo-Saxon→Latinate scale
(StoryScope STY_ALL_016).
Why it reads as AI: models default to the formal register of their training
mass; humans pick the short word unless the register demands otherwise.
Fix: rebalance — swap to the short Germanic word where the voice is not formal.

### Nominalized verbs
Looks like: "the implementation of the policy led to an improvement in
retention" where "implementing the policy improved retention" would do; "the
X of" frames stacked through a paragraph.
Scan: `nominalization.hits` and `nominalization.of_frames` — hits only, no
rate, no threshold; singular and plural forms are separate hits (Herbold et
al. 2023 [herbold-2023]; Reinhart et al. 2025 [reinhart-2025]).
Why it reads as AI: buried verbs rise monotonically across model generations,
but formal, legal, academic, and second-language prose nominalize legitimately
— in `expository` text these hits are a prompt to look, never a table row.
Fix: rebalance — unbury the verb where the register does not earn the noun.

### Abstract container-noun phrase
Looks like: "a sense of unease", "a mix of pride and fear", "the weight of the
decision" — an abstract container standing in for the concrete thing.
Scan: `grammar.container_of` count and hits; the 13 heads are those attested
in LAMP Table 8 (Chakrabarty et al. 2025 [chakrabarty-2025]), rare in the
human seed paragraphs.
Why it reads as AI: a reflex reach for an abstraction where a human names the
object or the feeling; fiction uses these legitimately, so judge density.
Fix: removal — name the concrete thing, or cut the frame and keep the noun.

### Hedge stacks
Looks like: "It could perhaps be argued that this might, to some extent,
generally be the case."
Scan: `hedges.rate` per 1k. Rule of thumb: > 10/1k in expository prose is
a stack.
Why it reads as AI: models hedge to avoid being wrong; a person with a view
states it and hedges once, if at all.
Fix: removal — keep at most one hedge per claim; delete the rest.

### Intensifier stacks
Looks like: "truly remarkable", "deeply meaningful", "incredibly important",
"genuinely transformative", several per paragraph.
Scan: `intensifiers.rate` per 1k. Rule of thumb: > 8/1k reads as padding.
Why it reads as AI: intensifiers substitute for specifics; humans intensify
rarely and usually for effect.
Fix: removal — delete the intensifier or replace the phrase with a concrete
detail that earns the emphasis.

## Punctuation

### Em-dash density
Looks like: "The plan—while ambitious—was sound—and it worked."
Scan: `punct.em_dash` per 1k. Rule of thumb: human nonfiction 0–4/1k; AI
drafts often 8–20/1k. Per-1k rates need roughly 300+ words to mean anything;
below that, cite the raw count (`punct.counts.em_dash`) and treat one or two
marks as noise. CLI flags like `--audit-only` are not counted; only `word--word`
or spaced ` -- ` forms count as an em-dash.
Why it reads as AI: models use the em-dash as a universal joiner where a human
would use a comma, a period, or parentheses, and they use it in every paragraph.
Fix: rebalance — keep one em-dash where it does real work; convert the rest to
periods (usually) or commas.

### Semicolon and colon habits
Looks like: semicolons joining independent clauses in casual prose; colons
introducing a clause that restates the previous one.
Scan: `punct.semicolon`, `punct.colon` per 1k.
Why it reads as AI: semicolons in a text message or casual email are rare for
humans; colon-led restatement is a summarizing tic.
Fix: rebalance — in casual registers, split into two sentences.

## Structures

### Tricolon habit (rule of three)
Looks like: "fast, reliable, and secure"; "we build, we ship, we learn"; every
list has exactly three items.
Scan: `structures.tricolon` count. Rule of thumb: more than one per 150 words
is a habit, not a choice. Counts any `A, B, and C` sequence, including clause
joins; treat the number as a prompt to look, not a verdict.
Why it reads as AI: the three-item list is rhythmically satisfying and the model
reaches for it reflexively; humans produce two- and four-item lists as often.
Fix: rebalance — cut one item, add a fourth, or make one item a sentence of its
own. Keep a tricolon only where the rhythm is the point.

### Not-X-but-Y framing
Looks like: "It's not about the code, it's about the culture." "This isn't a
setback—it's an opportunity." "Not only did we ship, but we learned."
Scan: `structures.not_but` count.
Why it reads as AI: a contrast frame that manufactures insight by negating a
strawman; models use it to sound reflective.
Fix: removal — state Y directly. Delete the negated X unless someone actually
claimed it.

### Rhetorical question then answer
Looks like: "So what does this mean for teams? It means…" "Why does this matter?
Because…"
Scan: `structures.rhetorical_q` count (outside dialogue).
Why it reads as AI: a transition device that simulates dialogue with the reader;
humans use it sparingly and usually with an edge.
Fix: removal — delete the question; keep the answer as a statement.

### Parallel sentence openers
Looks like: three or more consecutive sentences beginning with the same word
("We… We… We…", "It… It… It…").
Scan: `structures.parallel_openers` (runs of ≥3) and `openers.distinct_ratio`.
Rule of thumb: distinct-opener ratio below 0.6 in prose longer than 15 sentences
is monotonous.
Why it reads as AI: anaphora is a deliberate rhetorical figure; unintentional
anaphora is a generation artifact.
Fix: rebalance — vary the openers; combine two of the sentences.

### Verbatim repetition
Looks like: a phrase of four or more words reappearing intact across the piece
— "across all workstreams and teams" three times in a status report — or a
string lifted from the prompt or title.
Scan: `repetition.phrases` (silent under 150 words); repeated phrases are the
strongest true-source predictor readers miss, OR 1.47 (Jakesch et al. 2023
[jakesch-2023]); `repetition.repeated_phrase_rate` is reported-only.
Why it reads as AI: recurrence with no rhetorical intent; terminology, names,
and identifiers must repeat — exempt technical and legal prose — and a refrain
in fiction is deliberate.
Fix: removal — keep one instance and vary or cut the rest.

### Trailing participial clause
Looks like: a finished sentence that keeps going after a comma with an -ing
verb: ", ensuring seamless integration", ", allowing teams to move faster",
", highlighting the importance of".
Scan: `grammar.participial_tail` count, rate, and hits; ratio 5.3×, d = 1.38,
2024-era models, news and academic registers (Reinhart et al. 2025
[reinhart-2025]).
Why it reads as AI: the tack-on lets a sentence add a consequence without a
new subject, and models reach for it several times a paragraph.
Fix: removal — split into a sentence with its own subject, or drop the clause.

### Uniform sentence length
Looks like: every sentence 14–20 words; no fragments; no 40-word sentence.
Scan: `sentence_len.cv` (stdev/mean); `sentence_len.pct_over_30` (humans
31.2% vs 17.5–21.0%, 2023 news corpus, direction not magnitude; Muñoz-Ortiz et
al. 2024 [munoz-ortiz-2024]); `sentence_len.longest_flat_run` (reported-only).
A flat profile is also the native shape of plain-language and technical prose
— `tests/fixtures/human_plain.txt` sits in AI territory on every sentence
metric — and is not authorship evidence.
Rule of thumb: published human prose commonly 0.5–0.9; AI drafts often below
0.4.
Why it reads as AI: models regress to the mean sentence; humans write in bursts.
Fix: rebalance — split one long sentence into a short one and a fragment; merge
two mid-length sentences into a long one. Aim for range, not a target.

### Uniform paragraph length
Looks like: every paragraph three to four sentences; every paragraph opens with
a topic sentence and closes with a mini-conclusion.
Scan: `paragraph_len.cv`. Rule of thumb: below 0.3 across five or more
paragraphs is uniform.
Why it reads as AI: the five-paragraph-essay template applied to everything.
Fix: rebalance — allow a one-sentence paragraph; let one paragraph run long.

## Discourse moves

### Validating opener
Looks like: "Great question!" "I'd be happy to help." "Absolutely!" "That's a
really insightful point."
Scan: `wordlist.hits` includes "great question", "i hope this helps".
Why it reads as AI: assistant-style acknowledgement before content; humans
answer.
Fix: removal — start with the content.

### Restating the prompt
Looks like: the first paragraph paraphrases the question or task before
addressing it.
Scan: none; judge by reading.
Why it reads as AI: models anchor by echoing input; humans assume the reader
remembers what they asked.
Fix: removal — delete the paraphrase.

### Summary closer
Looks like: a final paragraph opening "In conclusion", "Ultimately", "Overall",
"In short" that restates the opening.
Scan: `discourse.summary_closer` (boolean).
Why it reads as AI: essay-template closure on texts that do not need it; humans
end when they are done.
Fix: removal — cut the paragraph, or end on the last concrete point.

### Sign-off advice and offers
Looks like: "Remember to…", "Feel free to reach out", "Don't hesitate to…",
"I hope this helps!"
Scan: `wordlist.hits` includes "reach out", "don't hesitate", "i hope this helps".
Why it reads as AI: assistant boilerplate.
Fix: removal — end with the actual last thing you have to say, or a plain sign-off.

### Safety disclaimer opener and AI self-reference
Looks like: a first paragraph that qualifies before it answers — "It's
important to approach this carefully", "I'm not able to give specific advice,
but", "consult a professional" — or any "As an AI" self-reference.
Scan: `discourse.disclaimer_opener.fired` and `.hits`; per-family range 46%
vs 0.2% of responses (Rudnicka & Juzek 2026 [rudnicka-2026]).
Why it reads as AI: assistant safety framing on a text that asked for none;
the same phrases mid-document are an ordinary discourse observation.
Fix: removal — start with the answer.

### Headings and bullets in short pieces
Looks like: a 200-word email with three bold headers and two bulleted lists.
Scan: none; judge by reading.
Why it reads as AI: structure imposed regardless of length or medium.
Fix: removal — prose for anything under ~300 words unless the medium expects
lists.
