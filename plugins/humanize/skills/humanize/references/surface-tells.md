# Surface tells

The layer StoryScope does not measure: vocabulary, punctuation, sentence and
paragraph shape, and discourse moves. Applies to every text class. Each entry
names the `surface_scan.py` metric that measures it where one exists. Ranges
marked *rule of thumb* are working heuristics from practice, not measured in the
StoryScope corpus.

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

### Uniform sentence length
Looks like: every sentence 14–20 words; no fragments; no 40-word sentence.
Scan: `sentence_len.cv` (stdev/mean). Rule of thumb: published human prose
commonly 0.5–0.9; AI drafts often below 0.4.
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

### Headings and bullets in short pieces
Looks like: a 200-word email with three bold headers and two bulleted lists.
Scan: none; judge by reading.
Why it reads as AI: structure imposed regardless of length or medium.
Fix: removal — prose for anything under ~300 words unless the medium expects
lists.
