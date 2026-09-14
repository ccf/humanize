# Model fingerprints

Per-model idiosyncrasies from StoryScope's six-way attribution analysis
(narrative features, 68.4% macro-F1 overall). Load this only when the user
names the model that produced the text, or asks which model likely did. These
are tendencies measured on fiction, not detection rules.

## Claude (Sonnet 4.6 in the corpus)
The most distinctive AI profile (89.3% F1), through restraint: event intensity
escalates less than in any other source; narrative voice is the most uniform;
genre stance is reverent/continuist (62% vs 39–56% for others); favors
epilogues and quiet endings over climactic "avalanche" endings; avoids dream
sequences. Audit focus: flat escalation, epilogue after the natural end,
uniform voice.

## GPT (GPT-5.4)
Socially oriented plotting (82.1% F1): gossip and rumor as plot mechanism (64%
vs 44–55%); stories framed as reflection on past events; ensemble social
networks at human-like size; subverts expectations more than other models (41%
vs 27–36%). Audit focus: retrospective frame, rumor-driven turns.

## Gemini (3 Flash)
Tidiest endings and extended denouements; the bleakest settings (88% tagged
bleak/oppressive). Audit focus: over-resolved endings, uniformly dark
atmosphere.

## DeepSeek (V3.2)
Front-loads crucial context that other sources delay. Audit focus: everything
explained in the first quarter; no withholding.

## Kimi (K2.5)
Fewest fingerprints, lowest attribution F1; sits at the generic center of the
AI distribution. Audit focus: the shared AI defaults in `narrative-tells.md`
with no model-specific additions.

## Shared AI defaults (all five)
Emotion via bodily sensation and environmental mirroring; narrator states the
theme; no subplots; protagonist's own choice resolves the plot; extended
conceit; earnest tone without humor; no real-world names or brands. See
`style-tells.md` and `narrative-tells.md`.
