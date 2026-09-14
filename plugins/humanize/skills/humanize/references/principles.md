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
