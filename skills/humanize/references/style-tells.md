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
