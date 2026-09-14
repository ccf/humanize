# Narrative tells (fiction)

StoryScope's nine non-style dimensions, filtered to the 57 features with a
human-vs-AI gap of at least 15 points (categorical) or 0.30 (1–5 scale). Load
only when the text is a story. Base rates are measured on 61,575 stories; see
`data/README.md`. Removals are safe; additions change what the story is — flag
them in the report so the author can reverse the choice.

## Agents

### Dominant mode of emotional expression
Looks like: feeling rendered as body — "her chest tightened", "something cold
settled in his stomach", "the words sat like stones" — scene after scene, with
the emotion itself never named.
Base rate: embodied sensations and metaphors — AI 81% / human 39%  (StoryScope AGENT_EMO_009)
Why it reads as AI: "show don't tell" applied as an absolute; human writers
name an emotion outright about a third of the time and vary the mode.
Fix: rebalance — keep the strongest one or two embodied moments; elsewhere,
name the feeling plainly ("she was angry") or cut the reaction entirely and let
the dialogue carry it.

### Preferred cues for conveying emotional state
Looks like: the weather agreeing with whoever is on the page — she reads the
letter and the rain starts; he decides to stay and the cloud breaks over the
field.
Base rate: metaphorical or environmental mirroring — AI 87% / human 47%  (StoryScope AGENT_EMO_012)
Why it reads as AI: pathetic fallacy signals feeling without naming it, so the
model reaches for it whenever a scene needs emotional weight it has not earned.
Fix: removal — let the weather be indifferent. Replace the mirroring detail
with something the character would actually have noticed at that moment,
whether or not it suits the mood.

### Modes of conveying the central character's emotions
Looks like: the protagonist's state carried by a nearby object every time — the
cold coffee she does not drink, the one dead fly on the sill, the coat still on
its hook.
Base rate: metaphorical or environmental imagery reflecting mood — AI 89% / human 50%  (StoryScope AGENT_EMO_002)
Why it reads as AI: the model treats objects as a reliable channel for
interiority, so the central character is almost never allowed to simply feel
something.
Fix: removal — keep one such object and cut the rest; let her say what she
wants, do something, or feel it in plain words instead.

### Dominant mode of introducing the central character
Looks like: the first paragraph is a dossier — "Maya Oyelaran was forty-two, a
hydrologist, and had not spoken to her brother in nine years" — before she does
or says anything.
Base rate: external description (appearance or background summary) — AI 52% / human 30%  (StoryScope AGENT_ATTR_001)
Why it reads as AI: a summary front-loads everything the rest of the story will
need, which is how a model manages consistency, not how a scene starts.
Fix: removal — cut the summary and open on the action or the first line of
dialogue; let the biography arrive in pieces later, or not at all.

### Scope of named human agents
Looks like: a cast of three — the protagonist, one antagonist, one confidant —
with everyone else left as "the nurse", "the neighbour", "a man from the
council".
Base rate: seven or more named human characters — AI 16% / human 35%  (StoryScope AGENT_ID_001)
Why it reads as AI: the direction is counter-intuitive — human stories are more
crowded; the model keeps the cast small because every name is a thread it has
to keep consistent.
Fix: addition — only when in character: give names to two or three of the
walk-ons who already appear, and let one of them come back once. Do not invent
characters to hit a count.

### Frequency of explicit emotion naming
Looks like: one "she was furious" every few pages, in a story otherwise built
entirely of gestures and weather.
Base rate: occasional explicit emotion naming — AI 91% / human 71%  (StoryScope AGENT_EMO_001)
Why it reads as AI: the middle band is the safe compromise between "show don't
tell" and clarity; human stories spread out to both ends.
Fix: removal — take the frequency off the middle: either name feelings plainly
and often, in the voice of a narrator who does that, or name none at all.

### Proportion of named vs. unnamed characters
Looks like: everyone with a speaking part has a name, including the barista and
the security guard, and none of them is ever "the woman at the desk" again.
Base rate: a mix of proper names and role-descriptors across major and minor characters — AI 27% / human 45%  (StoryScope AGENT_ID_003)
Why it reads as AI: naming is how the model keeps referents unambiguous, so it
names people a human writer would leave as their function.
Fix: addition — only when in character: add the mixture. Take the name back off
two or three minor figures and refer to them by role, and let a named character
be "her brother" in a scene where that is what he is.

### Typical motivation domains for major characters
Looks like: the major characters all acting on principle — the archivist who
will not destroy the records because it would be wrong, the officer who follows
orders because order matters.
Base rate: ideological or moral commitments — AI 52% / human 35%  (StoryScope AGENT_MOT_012)
Why it reads as AI: principled motives are legible and defensible, and the
model prefers characters whose reasons it can state.
Fix: removal — replace one character's principle with an interest: he wants the
job, he is owed money, he does not want to be humiliated in front of his
daughter.

### Complexity of modeled social network
Looks like: three people who each know the protagonist and nobody else — the
mother, the colleague, the ex — who are never in a room together.
Base rate: very simple network, few relationships — AI 35% / human 19%  (StoryScope AGENT_ROLE_018)
Why it reads as AI: a sparse graph is cheap to keep coherent, so the model
builds social worlds with no edges it does not need.
Fix: removal — remove the isolation: give two of them a history with each other
and let one line of dialogue show it. See the shape of the network in `Network
Density of Side-to-Side Ties` below.

### Dominant trajectories of main character change
Looks like: the arc is a lesson — he begins dismissive of his tenant and ends
by understanding her, and the story is the distance between those two states.
Base rate: moral learning or increased empathy — AI 45% / human 30%  (StoryScope AGENT_ATTR_021)
Why it reads as AI: moral improvement is the arc the model has seen most and
the one least likely to be read as a mistake.
Fix: removal — cut the learning: let him end roughly where he started, or let
what he learns arrive too late to be any use to him.

### Social network richness around the protagonist
Looks like: the protagonist has a sister and a boss, and that is the whole of
her life on the page — no neighbour, no old friend who calls at the wrong time.
Base rate: minimal, one or two recurring close relationships — AI 33% / human 18%  (StoryScope AGENT_ROLE_021)
Why it reads as AI: the model gives the protagonist exactly the relationships
the plot consumes, so nothing surrounds her that the story does not use.
Fix: removal — remove the vacuum: add one recurring third party who appears
twice and wants something unrelated to the main problem.

### Secondary character density
Looks like: exactly three supporting characters, each with one job — the
confidant, the obstacle, the witness — and nobody who is merely around.
Base rate: few (2–3) secondary characters — AI 61% / human 46%  (StoryScope AGENT_ID_002)
Why it reads as AI: a functional cast with no spare parts is a planning
artifact; human stories carry passengers.
Fix: removal — remove the economy: let one or two people be present who serve
no narrative purpose, and do not give them anything to do later.

### Dominant sources of motivation
Looks like: the central character's reason for everything is a value she holds
— "she could not let them do it to someone else."
Base rate: ethical or ideological principles — AI 49% / human 34%  (StoryScope AGENT_MOT_003)
Why it reads as AI: the model gives its protagonist the motive that is easiest
to justify, which is also the one a reader has met most often.
Fix: removal — give her a reason that does not flatter her: she is bored, she
is owed money, she wants to be the one who turned out to be right.

### Density of figurative language in character depiction
Looks like: people described in images rather than facts — "his patience was a
thin rope", "she wore her competence like borrowed armour" — often in the same
paragraph.
Base rate: AI 3.78 / human 3.06 on a 1–5 scale  (StoryScope AGENT_ATTR_024)
Why it reads as AI: character description is where the model decorates hardest,
because a figure feels like insight even when it carries none.
Fix: rebalance — cut about a third of the figures attached to people, starting
with those that restate something the scene already showed; keep the one that
says what no plain sentence could.

## Events

### Mode of resolution of the main event chain
Looks like: nothing changes in the world; the conflict ends when the
protagonist accepts it — she stands in the doorway and understands that her
father did what he could.
Base rate: resolved through internal understanding or acceptance — AI 47% / human 27%  (StoryScope EVT_SCH_004)
Why it reads as AI: an internal resolution is always available and never
requires the plot to produce a consequence, so it is the model's safest ending.
Fix: removal — make something happen: let the resolution be an act with a cost,
or let the understanding arrive and change nothing.

### Event Novelty Orientation
Looks like: every beat follows from the last exactly as expected — the warning,
the ignored warning, the accident, the reckoning.
Base rate: AI 3.02 / human 3.37 on a 1–5 scale, where 5 is highly surprising  (StoryScope EVT_CAU_017)
Why it reads as AI: the next event the model writes is the likeliest one, and a
chain of likeliest events is a story you can predict from its first page.
Fix: rebalance — let one event break the schema: someone declines the obvious
move, or the thing the story has been building toward simply does not happen.

## Perspective

### Primary functions of dialogue
Looks like: two characters arguing the theme aloud — "Maybe forgiveness isn't
something you give. Maybe it's something you stop withholding."
Base rate: philosophical or thematic debate — AI 59% / human 34%  (StoryScope PER_DIA_003)
Why it reads as AI: dialogue is where the model can state its point in a voice
that is not the narrator's, so the characters end up discussing the story.
Fix: removal — cut the debate and let them argue about the thing in front of
them: the bill, the key, who is driving back.

### Frequency of direct address to the reader
Looks like: not one "you" aimed outward in the whole story — no "you would have
liked her", no "I know how this sounds".
Base rate: reader never addressed — AI 94% / human 77%  (StoryScope PER_POV_009)
Why it reads as AI: the model narrates as though the text has no audience, so
even a confiding first-person teller never turns outward.
Fix: addition — only when in character: if the narrator is a teller — first
person, retrospective, speaking to someone — give them one sentence that admits
the reader is there. A close-third camera should stay closed.

## Plot

### Post-Climax Denouement Length
Looks like: the story ends twice — the confrontation, then a two-scene
epilogue: the funeral, then spring in the garden a year later.
Base rate: extended denouement, multiple scenes or time jumps — AI 51% / human 15%  (StoryScope PLT_MOR_007)
Why it reads as AI: the model keeps writing until every thread is visibly at
rest, and this is the largest single gap in the narrative dimensions.
Fix: removal — cut the epilogue. End on the last scene in which something is
still at stake. See `Ending temporal scope` for the same habit measured in
story time.

### Protagonist Transformational Trajectory
Looks like: the closed woman of page one is, by the last page, able to say the
thing out loud.
Base rate: positive growth or enlightenment — AI 68% / human 44%  (StoryScope PLT_MOR_004)
Why it reads as AI: growth is the default shape of a satisfying arc, and the
model has no reason to risk any other.
Fix: removal — take the growth out: make the change partial or sideways, or let
her win the argument and lose something for it.

### Agency in Resolution
Looks like: the ending turns on a decision — he chooses to hand over the tape —
and nothing outside him decides anything.
Base rate: resolution driven primarily by protagonist choice — AI 69% / human 46%  (StoryScope PLT_CON_007)
Why it reads as AI: protagonist agency is the craft rule the model applies
hardest, so chance and other people are written out of the ending.
Fix: removal — let something outside him take the decision away: the tape is
already gone, or someone else hands it over first.

### Moral Polarity Toward Protagonist
Looks like: the narrative is on her side throughout — her compromises are
understandable, her cruelty is provoked, and the last page vindicates her.
Base rate: affirmative or heroic stance — AI 52% / human 30%  (StoryScope PLT_MOR_002)
Why it reads as AI: the model aligns the narration's sympathy with its
viewpoint character by default and rarely lets that alignment break.
Fix: removal — remove the endorsement: let one of her choices go uncorrected
and un-excused, and do not have another character forgive her for it.

### Integration of Subplots with Theme
Looks like: a single line of causation from first page to last; there is no
side quarrel and no unrelated errand, so there is nothing for the theme to be
echoed by.
Base rate: no subplots at all — AI 79% / human 58%  (StoryScope PLT_THM_009)
Why it reads as AI: with one thread there is nothing to integrate; a single
spine is the easiest structure to keep coherent over a whole story.
Fix: addition — only when in character: one secondary thread that is not a
parallel of the theme — something the story is not about, which resolves on its
own terms.

### Density of Subplots
Looks like: every scene advances the same arc; the sister who appears in scene
two has no story of her own and is not heard from again.
Base rate: no significant subplots — AI 81% / human 60%  (StoryScope PLT_STR_003)
Why it reads as AI: secondary arcs cost tracking effort and pay off only at
length, so the model writes stories that are all main plot.
Fix: addition — only when in character: give one secondary character an arc of
two or three beats that resolves on its own schedule, not on the protagonist's.

### Stakes Types Present
Looks like: what is at risk is who the character is — "if he signed it, he
would not be able to look at himself" — rather than his job, his rent, or his
ribs.
Base rate: moral or spiritual integrity among the stakes — AI 86% / human 71%  (StoryScope PLT_STR_011)
Why it reads as AI: a moral stake is always available and needs no worldbuilding
to make real, so the model attaches one to almost every conflict.
Fix: removal — swap one moral stake for a material one and let the scene run on
that instead: the money, the visa, the tooth.

### Ending Closure Type
Looks like: the last page answers everything — we learn whether she forgives
him, whether the money came through, and what the whole thing meant.
Base rate: ambiguous or interpretive ending — AI 19% / human 35%  (StoryScope PLT_MOR_003)
Why it reads as AI: the direction is counter-intuitive — humans leave endings
open nearly twice as often; the model resolves because resolution is what a
satisfying ending looks like on average.
Fix: addition — only when in character: withhold one answer the story has been
driving at, and stop the scene before the reaction that would settle it.

### Thematic Unity
Looks like: every element points the same way — the broken clock, the estranged
son, the closing line about time — and nothing in the story is about anything
else.
Base rate: AI 4.74 / human 4.41 on a 1–5 scale  (StoryScope PLT_THM_008)
Why it reads as AI: unity is a coherence strategy the model applies across the
whole text; human stories carry material that does not serve the theme.
Fix: rebalance — let one element off the theme: a scene, an image, or a
character detail that is simply what it is.

### Degree of Closure
Looks like: every thread is tied on the last page — the letter is read aloud,
the diagnosis is named, the brother finally calls.
Base rate: AI 4.20 / human 3.90 on a 1–5 scale  (StoryScope PLT_MOR_006)
Why it reads as AI: the model finishes what it starts, so no question it raised
is left standing at the end.
Fix: rebalance — leave one raised question unanswered: cut the scene that
delivers the answer, or end before the phone is picked up.

## Revelation

### Reader Expectation Strategy
Looks like: the gun on the mantel goes off exactly as promised — the estranged
father is met, the illness is fatal, the letter says what it was always going
to say.
Base rate: sets up and fulfills expectations — AI 73% / human 53%  (StoryScope REV_SUS_005)
Why it reads as AI: the model plants and pays off because an unpaid setup looks
like an error, so nothing it promises goes unhonoured.
Fix: removal — break one promise: the meeting the story has been arranging
never happens, or happens and is uneventful.

### Overall Revelation Pacing Pattern
Looks like: the important facts arrive early — we learn in the second scene
that the brother drowned, and the rest of the story is consequence.
Base rate: back-loaded, key revelations near the end — AI 48% / human 66%  (StoryScope REV_DIS_001)
Why it reads as AI: the direction is counter-intuitive — humans hold back more
often; the model discloses early so every later scene can be written against a
settled context.
Fix: addition — only when in character: move one early disclosure into the last
quarter, and check that the earlier scenes still read without it.

### Use of Red Herrings
Looks like: every lead the story offers turns out to be true — no suspect who
is innocent, no explanation the reader is allowed to believe and then lose.
Base rate: red herrings deliberately deployed (inverting the "none" value) —
AI 16% / human 33%  (StoryScope REV_SUR_010)
Why it reads as AI: a false lead costs coherence and risks reading as a
mistake, so the model plants only clues it intends to honour.
Fix: addition — only when in character: let one plausible explanation stand for
several pages before the story takes it away. Do not add a false lead to a
story that is concealing nothing.

### Predominant Reader–Character Knowledge Alignment
Looks like: the reader learns everything at the moment the focal character does
— there is no scene in which we can see the car coming and she cannot.
Base rate: reader and character roughly aligned — AI 80% / human 64%  (StoryScope REV_SUR_004)
Why it reads as AI: strict alignment falls out of writing scene-by-scene from
one viewpoint, which is the model's default construction.
Fix: removal — remove the lockstep in one place: give the reader something the
character has not been told, or let the character know something the narration
withholds.

### Twist Placement Pattern
Looks like: whatever the story was hiding comes out in the middle, and the last
third is the working-through.
Base rate: climactic end twist — AI 45% / human 61%  (StoryScope REV_SUR_007)
Why it reads as AI: the direction is counter-intuitive — humans put the turn at
the end more often; the model reveals earlier so it can resolve the fallout.
Fix: addition — only when in character: move the revelation into the last scene
and cut the processing that used to follow it.

### Depth of Recontextualization After Surprise
Looks like: the reveal changes what happens next but nothing that came before —
learning the aunt lied does not make a single earlier scene read differently.
Base rate: AI 2.95 / human 3.29 on a 1–5 scale  (StoryScope REV_SUR_003)
Why it reads as AI: the model writes forward, so its surprises are new
information rather than a second reading of what is already on the page.
Fix: rebalance — plant two earlier moments the revelation will reinterpret: a
line that was heard one way, a refusal that had a different reason.

## Setting

### Dominant Sensory Modalities
Looks like: smell in nearly every setting — "the room smelled of wet wool and
old coffee", "diesel and cut grass off the verge".
Base rate: olfactory imagery among the dominant modalities — AI 82% / human 57%  (StoryScope SET_ATM_017)
Why it reads as AI: the direction is counter-intuitive — AI reaches for smell
more than humans do, because "engage the other senses" is craft advice applied
as a checklist and smell is the cheapest non-visual detail to invent.
Fix: removal — cut most of the smells, keeping one that a character would
actually have registered, and let the other rooms be described by what is in
them.

### Spatial Granularity Level
Looks like: the geography fully specified — the street the flat is on, which
way the window faces, how many steps to the kitchen, and where the town sits
relative to the coast.
Base rate: high spatial granularity — AI 54% / human 30%  (StoryScope SET_LOC_002)
Why it reads as AI: the direction is counter-intuitive — models are more
precise about space than human writers, because a fully specified layout is how
they keep the scene consistent with itself.
Fix: removal — cut the floor plan. Keep the two or three physical facts a
character has reason to notice and let the rest of the space stay unmapped.

### Setting Agency Level
Looks like: the place never interferes — the snow is described at length but
never blocks the road, and the flat is called small but nobody has to step over
anyone.
Base rate: setting that provides constraints or opportunities — AI 37% / human 55%  (StoryScope SET_ATM_003)
Why it reads as AI: the model uses setting for atmosphere rather than as a
mechanism, so its places are decorated but inert.
Fix: addition — only when in character: let the place cost something — the last
bus, the door that only opens from the inside, the heat that ends the
conversation early.

### Atmospheric Construction Techniques
Looks like: mood built from sky — "the light had gone grey and flat", "rain
against the window all afternoon" — in scene after scene.
Base rate: weather and light as atmosphere-builders — AI 90% / human 73%  (StoryScope SET_ATM_020)
Why it reads as AI: weather is the atmospheric tool that needs no specific
knowledge of the place, so it is the one the model always has available.
Fix: removal — build the atmosphere from something else in at least half the
scenes: the objects in the room, the noise through the wall, the state of the
floor.

### Opening Spatial Grounding
Looks like: the first page places you twice — the kitchen of a farmhouse, and
the farmhouse forty kilometres east of the river.
Base rate: clear local and global spatial context at the opening — AI 33% / human 18%  (StoryScope SET_LOC_004)
Why it reads as AI: the model establishes coordinates before it starts, the way
an outline does; human openings more often begin inside the situation.
Fix: removal — cut the wide shot. Open in the room and let the reader find out
where the room is when it matters, or never.

### Setting as Psychological Mirror
Looks like: the house failing at the rate the marriage does — a leak in the
first chapter, a collapsed ceiling by the end.
Base rate: AI 4.07 / human 3.58 on a 1–5 scale  (StoryScope SET_ATM_022)
Why it reads as AI: correspondence between inside and outside is a coherence
device, and the model maintains it across a whole story where a human writer
would forget.
Fix: rebalance — break the correspondence at least once: let the environment be
indifferent or actively wrong-footed at the worst moment. The scene-level
version of this habit is `Preferred cues for conveying emotional state`.

### Environmental and Ecological Emphasis
Looks like: landscape and climate given standing in the story — the drought
that frames the year, the river mentioned in every other scene, the season
tracked from page to page.
Base rate: AI 3.21 / human 2.84 on a 1–5 scale  (StoryScope SET_LOC_014)
Why it reads as AI: ecological framing is a currently prestigious move and the
model applies it whether or not the story is about a place.
Fix: rebalance — cut some of the landscape reporting and keep the parts that
change what a character can do.

## Situatedness

### Narratorial Thematic Commentary Presence
Looks like: the narration stepping out to explain — "It was the kind of
forgiveness that costs more than the wound did."
Base rate: narrator comments explicitly on theme or meaning — AI 76% / human 52%  (StoryScope SIT_MET_501)
Why it reads as AI: the model wants the point to land, so it states it in a
register no character has to take responsibility for.
Fix: removal — delete the sentence that explains. If the scene does not carry
the meaning without it, the scene is what needs fixing.

### Intertextual Strategy Types
Looks like: nothing is named — the book on the nightstand is "a paperback", the
hymn is "a hymn", the film they are half-watching is "an old film".
Base rate: explicit named reference to a specific text or author — AI 24% / human 46%  (StoryScope SIT_MET_202)
Why it reads as AI: named works are the most checkable thing in a story, so the
model gestures at culture instead of citing it.
Fix: addition — only when in character: name the actual book, song or writer
the character would have to hand, and confirm it exists and fits the period.

### Reference Explicitness
Looks like: references that gesture without naming — a flood, a betrayed
brother, a descent into a cellar — so the story reads as myth-shaped with no
myth invoked.
Base rate: primarily implicit echoes (genres, archetypes, unnamed myths) — AI 72% / human 50%  (StoryScope SIT_MET_008)
Why it reads as AI: archetype is free and attribution is risky, so allusion
collapses into resonance.
Fix: removal — remove the haze: either name the source the passage is echoing,
or cut the echo and let the event be only itself.

### Fourth-Wall Permeability
Looks like: the narrator never acknowledges a reader — no "you", no aside, no
"I should say here", no wink at the telling.
Base rate: reader never acknowledged — AI 63% / human 43%  (StoryScope SIT_MET_004)
Why it reads as AI: models write as though no one is watching; human narrators
break frame more than half the time, even lightly.
Fix: addition — only when in character: one aside or direct address at a point
where the voice already leans confiding. Never bolt it on to a close-third
literary voice.

### Tone Toward Genre Conventions
Looks like: the genre played entirely straight — the detective's world-weariness
and the cold spot on the landing delivered without one knowing beat.
Base rate: earnest and sincere stance toward genre — AI 84% / human 65%  (StoryScope SIT_GEN_004)
Why it reads as AI: irony about a convention risks reading as a failure to
execute it, so the model commits and never smiles.
Fix: removal — take the earnestness off one convention: let a character find it
ridiculous, or let the trope be executed badly by someone in the story.

### Structural Experimentation Level
Looks like: one timeline, one viewpoint, scenes in order, and section breaks
that do nothing but pass time.
Base rate: simple linear single strand — AI 62% / human 46%  (StoryScope SIT_MET_302)
Why it reads as AI: linear single-strand is the structure with the fewest ways
to go wrong, so it is where the model settles unless pushed.
Fix: removal — remove the straight line: frame the story from a later vantage,
or move one scene out of sequence and leave the join unexplained.

### Literary Ambition Signaling
Looks like: a ghost story that keeps reaching for significance — the haunting is
really about inherited grief, and the prose says so about once a page.
Base rate: crossover genre with literary aspirations — AI 79% / human 63%  (StoryScope SIT_MET_012)
Why it reads as AI: the model hedges between entertainment and literary
seriousness, which lands it in the crossover band far more often than a human
writer who has picked one.
Fix: removal — pick an end of the range: either let it be a ghost story and cut
the significance, or drop the genre engine and write the grief directly.

### Narrator Address Mode
Looks like: no "you" of any kind — not the generic "you never hear the one that
hits you", not a word to a listener inside the story, not the reader.
Base rate: no direct address of any kind — AI 94% / human 80%  (StoryScope SIT_MET_104)
Why it reads as AI: the model narrates to no addressee at all, so even the
impersonal "you" that ordinary speakers use constantly goes missing.
Fix: addition — only when in character: the generic "you" is the least intrusive
of the three modes and usually the right one; use a diegetic listener if the
story already has someone being told. See `Fourth-Wall Permeability` before
addressing the reader directly.

### Thematic Explicitness and Moralizing
Looks like: the point stated more than once — a character says it in dialogue
in the second act, and the final paragraph says it again in the narration.
Base rate: AI 3.94 / human 3.28 on a 1–5 scale  (StoryScope SIT_MET_303)
Why it reads as AI: the model cannot tell whether the theme has landed, so it
insures the reading by repeating it.
Fix: rebalance — delete the statements of the theme, keeping at most one, and
prefer the one spoken by a character who is partly wrong about it.

### Moral / Philosophical Weighting
Looks like: the story designed around a question — whether loyalty survives
being tested — with the plot arranged as the test and the characters as
positions.
Base rate: AI 3.68 / human 3.26 on a 1–5 scale  (StoryScope SIT_GEN_010)
Why it reads as AI: an argument gives the model a spine to build on, so the
story keeps being for something.
Fix: rebalance — let part of the story be for pleasure: a scene that is
interesting rather than instructive, and a detail that argues nothing.

### Perceived Literary Ambition in Prose Style
Looks like: sentences that keep signalling seriousness — a subordinate clause,
an image, a deliberate cadence — even in the passage where someone buys a train
ticket.
Base rate: AI 3.77 / human 3.48 on a 1–5 scale  (StoryScope SIT_MET_301)
Why it reads as AI: the model holds the literary register everywhere rather
than reserving it, so there is no plain writing to measure the good sentences
against.
Fix: rebalance — flatten the ordinary passages into plain report and keep the
marked style for the two or three moments that earn it. The sentence-level
checks are in `style-tells.md`.

## Social Networks

### Size of Social Network
Looks like: four people who matter and nobody else — the protagonist, two
intimates, one opponent — with the hospital, the firm and the village present
only as words.
Base rate: small network of 3–4 significant nodes — AI 60% / human 42%  (StoryScope SOC_STR_001)
Why it reads as AI: four nodes is the size at which every relationship can be
given a scene, and the model writes to what it can fully service.
Fix: removal — remove the tidiness: either cut to two people and let the story
be that small, or let a fifth and sixth figure matter without giving them
scenes of their own.

### Network Density of Side-to-Side Ties
Looks like: every relationship runs through the protagonist — her mother and
her colleague have never met and never will.
Base rate: hub-and-spoke network — AI 71% / human 54%  (StoryScope SOC_STR_002)
Why it reads as AI: a star graph keeps every relationship anchored to the
viewpoint character, which is how the model keeps the cast legible.
Fix: removal — remove the hub: give two side characters one scene together that
the protagonist is not in, or a shared history she learns about late.

### Range of Relationship Types Present
Looks like: a cast connected by family, work and friendship only — nobody in
the story wants anybody.
Base rate: a romantic or sexual relationship meaningfully present — AI 30% / human 48%  (StoryScope SOC_REL_007)
Why it reads as AI: the direction is counter-intuitive — humans write desire
into about half their stories; models route around it, leaving social worlds
that are unusually chaste.
Fix: addition — only when in character: let an existing relationship carry
attraction, wanted or not. Do not add a romance to a story with no place for
one.

## Temporal Structure

### Ending temporal scope
Looks like: the story does not stop when the argument ends — it jumps six
months on to show the two of them at a wedding, civil now.
Base rate: ends at or just after the main climax, no forward jump — AI 51% / human 70%  (StoryScope TMP_ORD_014)
Why it reads as AI: the direction is counter-intuitive — humans stop at the
climax far more often; the model adds a later vantage because distance reads as
completion.
Fix: addition — only when in character: cut the forward jump and end inside the
last scene of the main line of events. This is the story-time view of
`Post-Climax Denouement Length`.

### Global Chronological Structure
Looks like: straight time with one memory dropped in — a single half-page
flashback to the hospital corridor, then back to the present for good.
Base rate: mostly chronological with rare flashbacks — AI 72% / human 55%  (StoryScope TMP_ORD_001)
Why it reads as AI: one flashback is the smallest gesture toward temporal depth
a story can make, and the model makes exactly that gesture.
Fix: removal — take it off the default: either go strictly chronological and
fold the memory into dialogue, or let the past intrude often enough to become a
second strand.
