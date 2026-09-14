# Claude Code

## Tool calls
{
  "skill": "humanize:humanize",
  "args": "tests/fixtures/ai_report.txt --audit-only"
}
{
  "command": "cd /Users/ccf/git/humanize/skills/humanize && cat references/principles.md && echo ===== && cat /Users/ccf/git/humanize/tests/fixtures/ai_report.txt && echo ===== && wc -w /Users/ccf/git/humanize/tests/fixtures/ai_report.txt",
  "description": "Read principles reference and the fixture text"
}
{
  "command": "cd /Users/ccf/git/humanize/skills/humanize && cat /Users/ccf/git/humanize/tests/fixtures/ai_report.txt && printf '\\n----- words: ' && wc -w < /Users/ccf/git/humanize/tests/fixtures/ai_report.txt",
  "description": "Read the fixture text and count words"
}
{
  "command": "cat references/surface-tells.md",
  "description": "Read surface-tells reference"
}
{
  "command": "cat references/style-tells.md",
  "description": "Read style-tells reference"
}
{
  "command": "python3 scripts/surface_scan.py --text /Users/ccf/git/humanize/tests/fixtures/ai_report.txt",
  "description": "Run surface scanner on the fixture"
}
{
  "command": "python3 scripts/surface_scan.py /Users/ccf/git/humanize/tests/fixtures/ai_report.txt | python3 -c \"\nimport json,sys; d=json.load(sys.stdin)\nprint(json.dumps({k:d[k] for k in ('discourse','grammar','repetition','structures')}, indent=1)[:4000])\"",
  "description": "Pull discourse, grammar, repetition and structure hits from full scan JSON"
}

## Scanner output
Launching skill: humanize:humanize
Exit code 1
# Principles

Read this before every audit or rewrite.

1. **Disperse, don't converge.** StoryScope's central result: AI writing clusters in
   a shared region of stylistic and narrative space; human writing spreads out.
   A tell is a *default* the author didn't choose. The fix is a choice, not a
   different default. If every rewrite you produce would look alike, you have
   built a new cluster.

2. **Preserve voice and meaning.** Every fact, name, number, claim, and position
   survives. Register survives: a terse engineer stays terse, a warm note stays
   warm. You are removing tells, not imposing taste.

3. **Fix only what fired.** The audit names specific tells with quoted evidence.
   Rewrite those. Leave everything else exactly as it was, including things you
   would have written differently.

4. **Removals are safer than additions.** Cutting an unearned epilogue, a stacked
   metaphor, or a summary paragraph rarely misrepresents the author. Adding a
   joke, a brand name, or a flashback can. Reference entries tag each fix as
   `removal`, `addition`, or `rebalance`; make additions only when the inferred
   voice would plausibly do that, and say so in the report.

5. **Numbers are evidence, not verdicts.** Base rates come from a fiction corpus.
   Scan metrics are counts. A text can be entirely human and still show three
   tells; a text can show none and be generated. Report what fired and why a
   reader would notice. Never state or imply that the result is undetectable,
   passes a detector, or is "certified human."
   Check the direction before you flag it. Findings expire — lexical diversity
   reversed between GPT-3.5 and GPT-4 (Herbold et al. 2023 [herbold-2023]).
   Some never held — GPT-4o used agentless passives at about half the human
   rate (Reinhart et al. 2025 [reinhart-2025], 2024-era models), and 29 of 32
   model settings moved away from the dimension that carries passives (Milička
   et al. 2025 [milicka-2025]: a factor loading, not a passive count). Reader
   heuristics point backwards (Jakesch et al. 2023 [jakesch-2023], GPT-3-era
   self-presentation bios): contractions read as human but lean AI; grammar
   errors and long or rare words read as AI but lean human. Prefer recency for
   capability-dependent features, replication for stable ones — and never
   optimize for what a reader guesses is human.

6. **Ask rarely.** Infer register, audience, and intent from the text and the
   conversation. Ask one question only when a rewrite decision genuinely hinges
   on it and you cannot tell from context.

7. **Variance is the tool.** Vary sentence length. Let a plain sentence stay
   plain. Name an emotion once instead of embodying it again. Stop at the climax.
   Let one paragraph be a single line. Let a reference be specific. Each of these
   is a departure from the AI default; none is a new rule.

8. **Register and proficiency are not tells.** The measured AI profile — formal,
   impersonal, nominalized, flat sentence lengths, narrow lexis, few
   contractions — also describes competent second-language English, translated
   text, legal, technical, academic, and plain-language prose. That overlap is
   this repo's inference from the corpora below, not a finding any of them
   tests. Measure the profile; never infer authorship or proficiency from it,
   and never rewrite a text into looking less like one of those populations.
   Each human baseline here comes from one narrow population — StoryScope:
   amateur fiction; Muñoz-Ortiz: NYT lead paragraphs; Herbold: non-native
   student essays; Jakesch: short bios — whose own limitations decline to
   generalize. All of it is English; quote no number on translated or
   non-English text.
(eval):1: ==== not found
It's important to approach this update carefully, since several workstreams changed scope during the quarter. I'm not able to share vendor pricing here, but the overall picture is encouraging and the risks are manageable.

The implementation of the new ingestion pipeline finished two weeks behind the original estimate, reflecting the late discovery of schema drift in the partner feed. The team resolved the drift by introducing a validation layer, ensuring alignment across teams before any record reaches the warehouse. Throughput now sits at roughly nine thousand events per minute, exceeding the target we set in March.

Adoption of the shared design system continued across all workstreams and teams, creating a sense of momentum that was missing last quarter. Four product surfaces migrated to the new components, allowing designers to retire eleven legacy patterns. The migration of the billing screens remains in progress, pending the completion of an accessibility review.

On the reliability side, the optimization of our alerting rules reduced paging volume by about a third. Engineers consolidated forty-two overlapping alerts into nine, giving on-call staff a clearer signal during incidents. Mean time to acknowledge fell from eleven minutes to four, matching the level the platform group had proposed.

Customer support handled a spike in tickets after the pricing change, resolving most of them within the first business day. The knowledge base articles were rewritten in plainer language, and the deflection rate climbed from thirty to forty-one percent. A small group of enterprise accounts asked for a dedicated onboarding call, and account managers have scheduled those for the second week of the month.

Hiring closed on three of the five open roles, leaving two senior positions unfilled going into the next cycle. The weight of the decision to pause backfills fell mostly on the data platform group. We expect the remaining offers to close by mid-month, assuming the compensation adjustments are approved.

Coordination across all workstreams and teams improved once the weekly sync moved to a written format. Fewer meetings meant more focused work, and the written record made the escalation of blockers faster to trace. Product managers reported that the transformation of the roadmap into quarterly themes made prioritization discussions shorter.

Security completed the remediation of the findings from the spring audit, closing every high-severity item ahead of schedule. Two medium items remain open, awaiting a library upgrade that the vendor has scheduled for next month. The compliance team confirmed that the evidence collection process now runs automatically each week.

Documentation for the public API moved to the new site, giving external developers a searchable reference for the first time. Traffic to the reference pages doubled in the first month, and the volume of questions in the developer forum dropped noticeably. The technical writers also produced a migration guide for teams still on the deprecated endpoints.

Looking ahead, the integration of the analytics events into the new pipeline is the main dependency for the reporting launch. The team plans to finish the mapping by the end of the month, leaving three weeks for validation with finance. Budget remains within the approved envelope, and no additional headcount is requested at this time.

Finance reviewed the quarterly forecast with each product area and found no material variance against the plan. The revised allocation model landed in the reporting tool last week, and cost centre owners can now see their own numbers without filing a ticket. Two departments asked for a shorter reporting cycle, and that request is under review.

In summary, delivery across all workstreams and teams stayed on plan despite the schema issue, and the quarter closes with fewer open risks than it opened with. Please raise any concerns before Friday so they can be folded into the planning session.

----- words:      620
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
al. 2025 [kobak-2025] show marker words rising and falling with model
generations (share of biomedical abstracts containing the word, not a per-1k
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
# Style tells

StoryScope's Style dimension (figurative language, sound, syntax, register,
tone, allusion), filtered to the 20 features with a human-vs-AI gap of at least
15 points (categorical) or 0.30 (1–5 scale). Base rates are measured on 61,575
stories; see `data/README.md`. These apply to every text class; each entry says
how it shows up outside fiction.

Entries are ordered by the size of the human-vs-AI gap, largest first.

### Presence of extended conceit
Looks like: a metaphor that is introduced and then developed across several
sentences or the whole piece — the company as a ship, grief as a house with
rooms, the codebase as a garden — with each paragraph extending it.
Base rate: AI 83% / human 40%  (StoryScope STY_FIG_004)
Why it reads as AI: models sustain a governing metaphor because it is a
coherence strategy; most human writers drop a figure after one use.
Fix: removal — keep the first instance if it earns its place; cut every later
callback to the conceit and say the literal thing instead.
Outside fiction: the "journey" or "building blocks" frame that runs through an
entire blog post or team update.

### Lexical register and consistency
Looks like: a piece that stays in one register throughout — uniformly elevated,
or uniformly neutral-standard — with no slang, no shift to plain talk, no
sudden formal aside.
Base rate: mixed register with code-switching — AI 19% / human 56%  (StoryScope STY_ALL_015)
Why it reads as AI: humans slip between registers as mood and audience shift
mid-text; models hold a single register as a consistency default.
Fix: addition — only when in character: let one sentence go colloquial, or let
a plain paragraph be interrupted by a precise technical term. Do not sprinkle
slang mechanically.
Outside fiction: an email that never once says "yeah", "honestly", or "ugh"
from a writer who would.

### Sound Patterning Prominence
Looks like: alliteration and assonance you notice while reading — "the slow
slide of silt", "a hollow, swallowing hush" — recurring through the piece rather
than once at a deliberate moment.
Base rate: noticeable sound patterning — AI 91% / human 55%  (StoryScope STY_TON_006)
Why it reads as AI: models reach for euphony by default, so the ear-pleasing
version of each phrase is the one that survives, while most human prose is
sonically flat.
Fix: removal — keep the one sound effect that is placed for a reason and de-tune
the rest by swapping in the word you would have chosen without the ear in mind.
Outside fiction: a product page where every feature name alliterates, or a
headline picked for sound over accuracy.

### Conventional vs fresh figurative language
Looks like: every image is a new one — "the grief sat in her like a stone
swallowed sideways" — and no stock phrase appears anywhere in the piece.
Base rate: predominantly fresh and inventive images — AI 65% / human 30%  (StoryScope STY_FIG_003)
Why it reads as AI: the direction is counter-intuitive — models are more
inventive than humans, not more clichéd, and the tell is relentless invention
with no ordinary sentence between the images.
Fix: removal — cut most of the fresh images and let plain statement carry the
passage; a stock phrase in the right place is a human signal, not a failure.
Outside fiction: an essay where every paragraph opens with a new and unusual
comparison instead of stating the point.

### Predominant tonal quality
Looks like: earnestness throughout — nothing is undercut, no line is wry, and
the piece means everything it says at face value.
Base rate: earnest or lyrical tone — AI 71% / human 40%  (StoryScope STY_TON_021)
Why it reads as AI: sincerity is the safe default for a model that cannot
predict whether a joke will land.
Fix: removal — take the earnestness off at least one high point: undercut a
grand line, let a character be unimpressed, or state the thing flatly.
Outside fiction: a launch post that is visibly moved by its own product, with no
dry aside anywhere in it.

### Sentence-structure repertoire
Looks like: balanced series as the default sentence shape — "It changed how we
build, how we ship, how we think" — paragraph after paragraph.
Base rate: frequent parallel or list-like structures — AI 99% / human 70%  (StoryScope STY_CPX_012)
Why it reads as AI: this is near-universal in AI text, because parallelism is
the cheapest way to sound composed and models apply it by reflex.
Fix: removal — break the series: cut one limb, make one limb a sentence of its
own, or replace the list with a single specific. See the tricolon habit in
`surface-tells.md` for the surface-level check.
Outside fiction: bullet-shaped sentences in an email — "faster, cheaper, and
easier to maintain" — where one accurate clause would do.

### Recurrent metaphorical motif
Looks like: one image family threaded through the whole piece — weight, tide,
machinery — so that unrelated paragraphs reach for the same register of
comparison.
Base rate: motif present — AI 96% / human 69%  (StoryScope STY_FIG_005)
Why it reads as AI: a recurring motif is a coherence device the model applies
across the whole text, while human writers rarely track their images that far.
Fix: removal — keep the motif's single strongest appearance and rewrite the
others from whatever the local scene or paragraph actually offers.
Outside fiction: a strategy memo where everything is weather, momentum, or
plumbing from the first line to the last.

### Allusion domain diversity
Looks like: references that stay in the safe canon — myth, history, literature —
and never a named band, film, product, or team.
Base rate: pop-culture or brand-name allusions — AI 13% / human 40%  (StoryScope STY_ALL_018)
Why it reads as AI: models avoid naming real commercial and cultural artifacts,
so their references land in a timeless, unplaceable nowhere.
Fix: addition — only when in character: name the actual thing the writer would
name, the specific show or product, instead of "a popular streaming series".
Outside fiction: a post about consumer software that never names a competitor.

### Use of irony and humor
Looks like: nothing in the piece is meant other than literally — no joke, no
sarcasm, no dry undercut anywhere in it.
Base rate: any discernible humor or irony (inverting the straight-faced value) —
AI 62% / human 88%  (StoryScope STY_TON_023)
Why it reads as AI: humor is the highest-risk register for a model, so playing
everything straight is the safe move.
Fix: addition — only when in character: one dry line where the writer would
actually be dry. Do not insert jokes into prose whose author has none.
Outside fiction: an incident report or team update with not one wry remark, from
someone whose speech is full of them.

### Dominant Tonal Register
Looks like: a narrative voice that lingers, reflects, and finds significance,
rather than one that is reportorial, hardboiled, or analytic.
Base rate: lyrical or meditative register — AI 77% / human 52%  (StoryScope STY_TON_001)
Why it reads as AI: the reflective register is the model's comfortable default
and gets applied whatever the material is.
Fix: removal — cut the reflective sentences and let the reported facts stand,
then pick the register the material actually demands and hold it.
Outside fiction: a postmortem that keeps pausing to consider what the outage
meant for the team.

### Dominant Figurative Device Type
Looks like: comparisons asserted rather than proposed — "the deadline was a
wall" rather than "the deadline felt like a wall" — with metaphor crowding out
simile and plain description.
Base rate: metaphor-dominant — AI 73% / human 50%  (StoryScope STY_FIG_002)
Why it reads as AI: metaphor is the more literary of the two moves, and models
take the more literary move.
Fix: removal — convert some metaphors back to similes or to literal statement;
the mix, not the metaphor itself, is what reads human.
Outside fiction: business writing where processes are engines, funnels, and
flywheels instead of being described.

### Parataxis vs Hypotaxis Preference
Looks like: syntax that never commits — some coordination, some subordination,
evenly mixed, with no run of blunt short clauses and no long embedded sentence.
Base rate: balanced parataxis and hypotaxis — AI 85% / human 64%  (StoryScope STY_CPX_004)
Why it reads as AI: the balanced middle is the average of all training prose,
and averaging is what the model does.
Fix: removal — take out the balance: write one passage as a chain of short
coordinated clauses and another as a single long subordinated sentence.
Outside fiction: documentation where every sentence has the same clause count
regardless of how simple or complicated the step is.

### Primary Function of Allusion
Looks like: a reference used to point at the moral — "like Icarus, we flew too
close" — rather than to color a setting or characterize whoever made it.
Base rate: allusion as theme-signposting or moral commentary — AI 46% / human 26%  (StoryScope STY_ALL_004)
Why it reads as AI: models use references to make the point legible, where human
writers more often use them for texture, humor, or offhand analogy.
Fix: removal — delete the signposting reference, or repurpose it so it says
something about the person making it rather than about the theme.
Outside fiction: an essay that closes on a myth or a quotation restating the
argument.

### Sound patterning devices
Looks like: alliteration specifically, as the salient device whenever the prose
pushes — "a steady, stubborn strain", "policy, practice, and posture".
Base rate: alliteration prominent — AI 98% / human 79%  (StoryScope STY_TON_025)
Why it reads as AI: alliteration is the sound effect producible by word choice
alone, so it is the one models overuse.
Fix: removal — replace the alliterating word with the accurate one; if the
phrase survives only because it sounds good, cut the phrase.
Outside fiction: alliterative section headings and slogans in a deck or a
README.

### Use of Sentence Fragments
Looks like: fragments for emphasis, several to a page. Short. Punchy. Like this.
Base rate: fragments present and stylistically significant — AI 85% / human 67%  (StoryScope STY_CPX_003)
Why it reads as AI: the direction is counter-intuitive — AI fragments more than
humans do, because the one-beat emphatic fragment is a learned dramatic device,
not a sign of a loose human hand.
Fix: removal — rejoin most fragments into the sentences they broke off from, and
keep at most one where the break carries real emphasis.
Outside fiction: a social post where every third line is a one-word paragraph.

### Voice Markedness
Looks like: a voice with flavor but no risk — a little rhythm, a few distinctive
turns, no dialect, no verbal tic, nothing a reader could imitate.
Base rate: moderately marked voice, distinct but not extreme — AI 98% / human 83%  (StoryScope STY_TON_005)
Why it reads as AI: almost every AI passage lands in this middle band, while
human writing spreads out into plain report and into genuine idiosyncrasy.
Fix: removal — take the voice off the middle: either strip it back to plain
report, or commit to one real mannerism and carry it consistently.
Outside fiction: internal writing that sounds like a company rather than like a
person.

### Figurative Device Density
Looks like: a metaphor or simile in most paragraphs, including in sentences that
had a job to do and did not need one.
Base rate: AI 3.66 / human 3.00 on a 1–5 scale  (StoryScope STY_FIG_001)
Why it reads as AI: models decorate by default, and figurative density is the
most visible form that decoration takes.
Fix: rebalance — cut roughly a third of the figures, starting with those that
explain something already clear, and keep the ones doing work no literal
sentence could do.
Outside fiction: an explainer where every concept arrives with an analogy
attached to it.

### Rhythmic markedness of prose
Looks like: cadence you can hear — balanced clauses, repeated openings,
sentences resolving on a stressed beat — sustained across the whole piece.
Base rate: AI 3.61 / human 3.17 on a 1–5 scale  (StoryScope STY_TON_024)
Why it reads as AI: the model optimizes each sentence for fluency, and sustained
fluency turns into a metronome.
Fix: rebalance — break the meter: let one sentence end awkwardly, run another
past its natural stop, or drop a clause that exists only for balance.
Outside fiction: a speech-shaped post that reads as though written to be read
aloud when nobody will read it aloud.

### Allusion density
Looks like: prose that refers to almost nothing outside itself — no cited text,
no dated event, no artifact a reader would recognize.
Base rate: AI 2.26 / human 2.59 on a 1–5 scale  (StoryScope STY_ALL_017)
Why it reads as AI: models avoid specific external references because those are
the most checkable thing in a text, while humans reach for them constantly.
Fix: rebalance — add the reference the writer would actually have made, and
confirm it is real before keeping it.
Outside fiction: a memo that cites no paper, no prior project, and no names.

### Latinate vs Anglo-Saxon lexical flavor
Looks like: "utilize", "facilitate", "commence", "demonstrate" where "use",
"help", "start", and "show" would carry the same sense.
Base rate: AI 2.83 / human 2.51 on a 1–5 scale  (StoryScope STY_ALL_016)
Why it reads as AI: the formal register dominates the training mass, so the
learned word wins unless the context pushes hard the other way.
Fix: rebalance — swap in the short Germanic word wherever the register does not
require the long one; `surface-tells.md` carries the paired surface check.
Outside fiction: a chat message written in the register of a policy document.
words 620 · sentences 34 · paragraphs 12
sentence length: mean 18.24, stdev 3.46, cv 0.19 (min 14, max 27)
paragraph length: mean 2.83 sentences, stdev 0.39, cv 0.137
per 1k words: em-dash 0.0 (0) · en-dash 0.0 (0) · semicolon 0.0 (0) · colon 0.0 (0) · ellipsis 0.0 (0) · exclamation 0.0 (0)
structures: tricolon 1 · not-but 1 · rhetorical-q 0 · parallel-opener runs 0 · distinct openers 0.735
wordlist: 0.0/1k — none
hedges 0.0/1k · intensifiers 0.0/1k
summary closer: yes · dialogue paragraphs: 0%
repetition: 3.2/1k · longest repeat 5 · "across all workstreams and teams"×3
grammar: participial tails 14 (22.6/1k) ", reflecting the late discovery of schema drift in the" · container-of 2 "a sense of"
sentence tail: over-30 0.0% · p90 25 · longest flat run 8
nominalization hits: 24 (validation×2, migration×2, implementation×1) · frames: "the implementation of", "the migration of"
{
 "discourse": {
  "summary_closer": true,
  "disclaimer_opener": {
   "fired": true,
   "hits": [
    {
     "text": "it's important to approach",
     "sentence": 0
    },
    {
     "text": "i'm not able to",
     "sentence": 1
    }
   ]
  }
 },
 "grammar": {
  "participial_tail": {
   "count": 14,
   "rate": 22.6,
   "hits": [
    {
     "text": ", reflecting the late discovery of schema drift in the",
     "sentence": 2
    },
    {
     "text": ", ensuring alignment across teams before any record reaches",
     "sentence": 3
    },
    {
     "text": ", exceeding the target we set in March",
     "sentence": 4
    },
    {
     "text": ", creating a sense of momentum that was missing last quarter",
     "sentence": 5
    },
    {
     "text": ", allowing designers to retire eleven legacy patterns",
     "sentence": 6
    },
    {
     "text": ", giving on-call staff a clearer signal during incidents",
     "sentence": 9
    },
    {
     "text": ", matching the level the platform group had proposed",
     "sentence": 10
    },
    {
     "text": ", resolving most of them within the first business day",
     "sentence": 11
    },
    {
     "text": ", leaving two senior positions unfilled going into the next",
     "sentence": 14
    },
    {
     "text": ", assuming the compensation adjustments are approved",
     "sentence": 16
    }
   ]
  },
  "container_of": {
   "count": 2,
   "hits": [
    {
     "text": "a sense of",
     "sentence": 5
    },
    {
     "text": "The weight of",
     "sentence": 15
    }
   ]
  }
 },
 "repetition": {
  "too_short": false,
  "repeated_phrase_rate": 3.2,
  "longest_repeat": 5,
  "phrases": [
   {
    "text": "across all workstreams and teams",
    "count": 3,
    "sentences": [
     5,
     17,
     32
    ]
   }
  ]
 },
 "structures": {
  "tricolon": 1,
  "not_but": 1,
  "rhetorical_q": 0,
  "parallel_openers": 0
 }
}

## Output
Using the humanize skill to audit the fixture without rewriting.
Audit only, so I stop after the table. The text is 620 words, classified `expository` (a quarterly status report).

| # | Tell | Evidence | Base rate / metric |
|---|------|----------|--------------------|
| 1 | Safety disclaimer opener | "It's important to approach this update carefully", "I'm not able to share vendor pricing here, but" (×2, sentences 1–2) | 46% vs 0.2% of responses, per-family range [rudnicka-2026] |
| 2 | Trailing participial clause | ", ensuring alignment across teams before any record reaches" (×14 in 34 sentences) | scan: 22.6/1k; ratio 5.3×, d = 1.38 [reinhart-2025] |
| 3 | Verbatim repetition | "across all workstreams and teams" (×3, sentences 6, 18, 33) | scan: longest repeat 5 words; OR 1.47 [jakesch-2023] |
| 4 | Uniform sentence length | every sentence 14–27 words; longest flat run 8; no sentence over 30 | scan: cv 0.19, over-30 0.0%; rule of thumb human 0.5–0.9; human over-30 31.2% vs AI 17.5–21.0% [munoz-ortiz-2024] |
| 5 | Uniform paragraph length | 12 paragraphs, all 2–3 sentences | scan: paragraph cv 0.137; rule of thumb below 0.3 is uniform |
| 6 | Summary closer | "In summary, delivery across all workstreams and teams stayed on plan despite the schema issue" | scan: summary_closer = yes |
| 7 | Abstract container-noun phrase | "creating a sense of momentum", "The weight of the decision to pause backfills" (×2) | scan: container_of 2; heads from LAMP Table 8 [chakrabarty-2025] |

Notes on what did not become a row:

- **Nominalizations** fired 24 hits with stacked frames such as "the implementation of", "the migration of", "the optimization of", "the remediation of", "the transformation of". In expository prose these are a prompt to look, not a row. Here they are dense enough that a rewrite would unbury several verbs.
- **Wordlist, hedges, intensifiers, em-dashes, semicolons** all scanned at zero. The one tricolon and the one not-but structure are within normal range for this length.
- **Style tells** mostly did not fire in a way a status report would not earn. The uniformly earnest, neutral register is native to the genre, so I did not count it as evidence.

Strongest signals are the assistant-style disclaimer opening, the participial tails in nearly half the sentences, and the flat sentence and paragraph rhythm. No rewrite was made.
Audit only, so I stop after the table. The text is 620 words, classified `expository` (a quarterly status report).

| # | Tell | Evidence | Base rate / metric |
|---|------|----------|--------------------|
| 1 | Safety disclaimer opener | "It's important to approach this update carefully", "I'm not able to share vendor pricing here, but" (×2, sentences 1–2) | 46% vs 0.2% of responses, per-family range [rudnicka-2026] |
| 2 | Trailing participial clause | ", ensuring alignment across teams before any record reaches" (×14 in 34 sentences) | scan: 22.6/1k; ratio 5.3×, d = 1.38 [reinhart-2025] |
| 3 | Verbatim repetition | "across all workstreams and teams" (×3, sentences 6, 18, 33) | scan: longest repeat 5 words; OR 1.47 [jakesch-2023] |
| 4 | Uniform sentence length | every sentence 14–27 words; longest flat run 8; no sentence over 30 | scan: cv 0.19, over-30 0.0%; rule of thumb human 0.5–0.9; human over-30 31.2% vs AI 17.5–21.0% [munoz-ortiz-2024] |
| 5 | Uniform paragraph length | 12 paragraphs, all 2–3 sentences | scan: paragraph cv 0.137; rule of thumb below 0.3 is uniform |
| 6 | Summary closer | "In summary, delivery across all workstreams and teams stayed on plan despite the schema issue" | scan: summary_closer = yes |
| 7 | Abstract container-noun phrase | "creating a sense of momentum", "The weight of the decision to pause backfills" (×2) | scan: container_of 2; heads from LAMP Table 8 [chakrabarty-2025] |

Notes on what did not become a row:

- **Nominalizations** fired 24 hits with stacked frames such as "the implementation of", "the migration of", "the optimization of", "the remediation of", "the transformation of". In expository prose these are a prompt to look, not a row. Here they are dense enough that a rewrite would unbury several verbs.
- **Wordlist, hedges, intensifiers, em-dashes, semicolons** all scanned at zero. The one tricolon and the one not-but structure are within normal range for this length.
- **Style tells** mostly did not fire in a way a status report would not earn. The uniformly earnest, neutral register is native to the genre, so I did not count it as evidence.

Strongest signals are the assistant-style disclaimer opening, the participial tails in nearly half the sentences, and the flat sentence and paragraph rhythm. No rewrite was made.
