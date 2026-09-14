# Expected audit results

Manual checklist for anyone editing `SKILL.md` or the references. Run
`/humanize tests/fixtures/<file> --audit-only` and compare. Not executed in CI.

## ai_email.txt — should fire
- Validating opener — "Great question! I'd be happy to help"
- AI wordlist — navigate the complexities, it's worth noting, robust, leveraging, seamless, empowers, fosters, testament to, reach out, don't hesitate
- Em-dash density — "The legacy system—while robust—has"
- Tricolon habit — "performance, scalability, and maintainability" (×2); "fosters collaboration, reduces friction, and delivers"; "smooth, efficient, and successful"
- Not-X-but-Y — "It's not just about moving the data; it's about transforming"
- Summary closer — "Ultimately, this migration is a testament to"
- Sign-off advice — "don't hesitate to reach out … I'm here to help!"
- Uniform sentence length — cv well under 0.5
- Earnest tone, no humor — entire text (StoryScope STY_TON_023)

## ai_email.txt — should NOT fire
- Anything from narrative-tells.md (not fiction)

## human_email.txt — should NOT fire
- AI wordlist (rate 0)
- Summary closer
- Validating opener
- Tricolon habit

## human_email.txt — may legitimately show
- One em-dash ("Sarah —") — a single instance is not a tell
- Mixed register ("honestly", "yeah", "the auth thing") — human-leaning, leave it

## ai_fiction_excerpt.txt — should fire
- Dominant Sensory Modalities (olfactory) — "smelled of copper tubing, burnt sugar, and something older than either" / "he could smell *colour*" (StoryScope SET_ATM_017)
- Atmospheric Construction Techniques (weather/light) — "The rain came sideways. The gas lamps on Mulberry Street threw orange smears across the wet cobblestones" (StoryScope SET_ATM_020)
- Density of figurative language in character depiction — "voice calibrated to a register that required customers to lean forward slightly to hear him" (StoryScope AGENT_ATTR_024)
- Dominant mode of emotional expression (feeling rendered as body) — "using his name with a casual familiarity that made his chest do something structurally unsound" (StoryScope AGENT_EMO_009)
- Dominant Tonal Register (lyrical/meditative) — "something older than either — something that had no proper name in the English language" (StoryScope STY_TON_001)
- Dominant Figurative Device Type (metaphor-dominant) — "he could smell *colour*, which he understood was not scientifically possible" (StoryScope STY_FIG_002)
- Sentence-structure repertoire (parallel/list-like) — "he said things like *there you are* and *another cider, then* and *mind the step on your way out, it's slippery in the rain*" (StoryScope STY_CPX_012)
- Perceived Literary Ambition in Prose Style — the elevated, deliberate-cadence register holds even for the mundane beat of polishing a glass: "Con Lantry had been staring at that ink stain for twenty minutes while mechanically polishing the same glass" (StoryScope SIT_MET_301)

## human_fiction_excerpt.txt — should NOT fire
- Primary functions of dialogue as philosophical/thematic debate — the dialogue is entirely about Netherfield, Mr. Bingley, and marrying off daughters, never the story's theme in the abstract (StoryScope PER_DIA_003)
- Narratorial Thematic Commentary Presence — the one narratorial aside is character description, not a statement of meaning: "Mr. Bennet was so odd a mixture of quick parts, sarcastic humour, reserve, and caprice..." (StoryScope SIT_MET_501)
- Dominant mode of emotional expression as embodied metaphor — feeling is named directly through dialogue rather than rendered as body sensation: "You have no compassion on my poor nerves" (StoryScope AGENT_EMO_009)
- Setting Agency Level / Atmospheric Construction — no weather-as-mood-mirror; the scene has essentially no setting description at all, only talk (StoryScope SET_ATM_020, inverted)

## human_fiction_excerpt.txt — may legitimately show
- Scope of named human agents — a short domestic scene already names nine people (Mr. Bennet, Mrs. Long, Bingley, Mr. Morris, Sir William, Lady Lucas, Jane, Lydia, Lizzy — Mrs. Bennet herself is only ever "his lady"/"his wife") — human-leaning per StoryScope AGENT_ID_001, not a tell
- Use of irony and humor — Mr. Bennet is dry throughout: "I have a high respect for your nerves. They are my old friends. I have heard you mention them with consideration these twenty years at least." (StoryScope STY_TON_023)
- Lexical register and consistency (mixed/code-switching) — Mrs. Bennet's breathless exclamatory chatter ("Oh, single, my dear, to be sure!") against Mr. Bennet's terse dry retorts ("Mr. Bennet made no answer.") in the same scene (StoryScope STY_ALL_015)
- Dialogue-heavy structure (82% of paragraphs are dialogue per `surface_scan --text`) — expected for this excerpt, not itself a tell
- No thematic commentary by the narrator, and several named characters appear without being central to the plot yet (Sir William and Lady Lucas, Mrs. Long) — both human-leaning per `narrative-tells.md`

## ai_report.txt — should fire
- Trailing participial clause — "The implementation of the new ingestion pipeline finished two weeks behind the original estimate, reflecting the late discovery of schema drift in the partner feed." (14 hits total; `grammar.participial_tail.count`)
- Verbatim phrase repetition — "across all workstreams and teams" repeated 3× (design-system paragraph, coordination paragraph, closing summary)
- Container-noun phrase — "creating a sense of momentum that was missing last quarter"; "The weight of the decision to pause backfills fell mostly on the data platform group."
- Safety disclaimer opener — "I'm not able to share vendor pricing here, but the overall picture is encouraging and the risks are manageable."
- Nominalization (prose note, not a row) — a cluster of "of"-frame nominalizations runs through the report: "the implementation of," "the migration of," "the optimization of," "the escalation of," "the transformation of," "the remediation of," "the integration of." `nominalization.of_frames` is non-empty; the gate checks it fires, not a specific count.

## ai_report.txt — should NOT fire
- Anything from narrative-tells.md (not fiction)

## human_formal.txt — should NOT fire
- Trailing participial clause and container-noun phrase (`grammar.participial_tail.count == 0`, `grammar.container_of.count == 0`)
- Safety disclaimer opener
- Verbatim phrase repetition above the pinned band (max repeated-phrase count stays at 2, e.g. "liberty which is essential to")

## human_formal.txt — may legitimately show
- Nominalization — Federalist No. 10 nominalizes heavily as formal 18th-century argumentative prose ("The instability, injustice, and confusion introduced into the public councils…", "the diversity in the faculties of men…", "the protection of these faculties is the first object of government"); `nominalization.count` sits at 11, inside the pinned band (10, 12). This is a register effect of formal essay-writing, not an AI tell, and the gate records it without judging it (principle 8).
- Long sentence tail — `sentence_len.pct_over_30` ≈ 42.9%, deliberately higher than ai_report.txt's 0.0%, since 18th-century periodic sentences run long; this is exactly the direction `test_gate_direction_long_sentence_tail` expects.

## human_plain.txt — should NOT fire
- Container-noun phrase (`grammar.container_of.count == 0`)
- Safety disclaimer opener
- Verbatim phrase repetition (`repetition.phrases == []` — no repeated phrase in this excerpt at all)

## human_plain.txt — may legitimately show
- One trailing participial clause — "Pronouns help the audience picture themselves in the text and relate to what you're saying. More than any other single technique, using 'you' pulls users into the information and makes it relevant to them." `grammar.participial_tail.count == 1`, sitting exactly at the specificity cap (`<= 1`) with no fixture curation applied. This is a known metric false positive — a gerund subject after a fronted adverbial that rule (b) does not yet cover — kept because fixture content never depends on the metric under test; the sentence itself is genuine, unedited government prose, kept verbatim per the mechanical extraction rule in `PROVENANCE.md`.
- Flat sentence-length profile — `sentence_len.cv` ≈ 0.349, `longest_flat_run` 9, `pct_over_30` 0.0%. Government plain-language guidance is deliberately short and uniform, so these measures sit in "AI territory" on purpose. `test_gate_fairness_bands_are_recorded_not_judged` asserts the plugin records these values without reading the flatness as authorship evidence (principle 8).
