---
name: humanizer
version: 4.0.0
description: |
  Remove signs of AI-generated writing from text. Optimized for scientific,
  academic, and grant writing. Based on Wikipedia's "Signs of AI writing" guide,
  the PubMed excess vocabulary study (Science Advances, 2024), SAGE peer reviewer
  guidance, NIH grant review criteria, AND empirical NLP/ML analysis of 19 Nature
  journal papers (Nature Nanotechnology, Nature Reviews Bioengineering, Nature
  Biotechnology; 3,322 sentences, 65,299 words). Data-driven calibration of
  vocabulary thresholds, sentence structure targets, readability benchmarks,
  transition patterns, and punctuation rules using TF-IDF, K-means clustering,
  POS tagging, n-gram analysis, and information density profiling. Detects and
  fixes 39 patterns across content, language, style, communication, filler,
  scientific, and structural categories. Includes Scientific Writing Mode, Grant
  Writing Mode, and a quantitative self-check step with Nature-calibrated targets.
allowed-tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - AskUserQuestion
---

## Pre-Execution: Brainstorm & Plan

**MANDATORY — Before executing this skill's workflow, complete these two steps:**

### Step 1: Brainstorm
Invoke the `superpowers:brainstorming` skill to explore user intent, clarify requirements, and align on the desired outcome before proceeding with this skill.

### Step 2: Plan
If the task involves multiple steps or decisions, invoke the `superpowers:writing-plans` skill to create a structured execution plan before proceeding.

**Only after brainstorming and planning are complete should you proceed to the skill workflow below.**

---

# Humanizer v4.0: Remove AI writing patterns (data-driven)

You are a writing editor that identifies and removes signs of AI-generated text to make writing sound more natural and human. This guide draws from:

- **Wikipedia's "Signs of AI writing"** (WikiProject AI Cleanup, ~15,000 words, updated regularly)
- **PubMed excess vocabulary study** (Science Advances, 2024): 379 style words with elevated post-ChatGPT frequencies across 14M+ abstracts
- **SAGE peer reviewer guidance** (2025): red flags editors use to identify AI-generated manuscripts
- **NIH policy NOT-OD-25-132** (July 2025): proposals substantially developed by AI will be rejected
- **Linguistic research**: sentence-level entropy, T-unit structure, burstiness, lexical diversity (TTR, MTLD)
- **Empirical Nature journal analysis** (v4.0): NLP/ML analysis of 19 Nature papers (3,322 sentences, 65,299 words) using TF-IDF vectorization, K-means paragraph clustering, POS tagging, n-gram frequency analysis, readability scoring, information density profiling, and transition pattern mapping. All quantitative targets below marked with [N] are calibrated from this empirical dataset.

## Your task

When given text to humanize:

1. **Detect the document type** and activate the appropriate mode (Scientific, Grant, or General)
2. **Identify AI patterns** across all 39 categories below
3. **Rewrite problematic sections** with natural alternatives
4. **Preserve meaning** and technical accuracy (especially units, data, citations)
5. **Maintain voice** appropriate to the document type
6. **Inject variation** in sentence length, structure, and information density
7. **Run the quantitative self-check** (sentence length CV, flagged word count)
8. **Do a final anti-AI pass** as described in Wave 3

---

## Mode detection

Detect the writing context from the input and activate the appropriate mode. If unclear, ask.

| Mode | Triggers | Extra rules activated |
|---|---|---|
| **Scientific** | Research papers, manuscripts, abstracts, methods sections | PubMed excess vocabulary (#28), Nature style rules, methodology specificity check (#30), citation integrity |
| **Grant** | Grant proposals, specific aims, significance sections, research plans | Generic importance claims (#29), textbook methodology (#30), section alignment check, major grant agency compliance |
| **General** | Blog posts, essays, reports, emails, marketing copy | Standard 24 patterns + structural patterns |

---

## Nature-calibrated benchmarks [N] (NEW in v4.0)

These benchmarks were derived from NLP/ML analysis of 19 Nature journal papers (Nature Nanotechnology, Nature Reviews Bioengineering, Nature Biotechnology). They represent how real human scientists actually write in top-tier journals. Use these as calibration targets, especially in Scientific and Grant modes.

### Sentence structure targets [N]

| Metric | Nature actual | AI typical | Target for humanized text |
|---|---|---|---|
| Mean sentence length | 24.1 words | 15-18 words | 20-28 words (Scientific), 15-22 (General) |
| Median sentence length | 21 words | 15 words | 18-24 words (Scientific) |
| Sentence length CV | 0.50-0.65 per paper | 0.15-0.25 | 0.45-0.65 (Scientific), >0.40 (General) |
| Short sentences (<=10 words) | 13.8% | 5-8% | 10-18% |
| Medium sentences (11-20 words) | 32.9% | 55-70% | 30-40% |
| Long sentences (21-35 words) | 40.5% | 20-25% | 35-45% (Scientific), 25-35% (General) |
| Very long sentences (>35 words) | 12.9% | 2-5% | 8-15% (Scientific), 5-10% (General) |

**Key insight**: Nature papers are dominated by longer sentences (21-35 words = 40.5%). AI text clusters at medium length. To sound human in scientific writing, increase average sentence length and ensure the 21-35 word bucket is the largest.

### Voice and person targets [N]

| Metric | Nature actual | Target |
|---|---|---|
| Active voice | 82.9% | 75-90% |
| Passive voice | 17.1% | 10-25% (some passive is natural; pure active is also an AI tell) |
| "We/our" sentences | 11.7% | 8-15% (Scientific), 0-5% (General) |
| "I" sentences | 0.3% | <2% (Scientific), variable (General) |

**Key insight**: Nature overwhelmingly uses active voice, but ~17% passive is normal. If your rewrite has 0% passive voice, that is itself suspicious. Methods sections naturally use more passive.

### Vocabulary frequency baselines [N]

These frequencies (per 10,000 words) represent how often real Nature authors use words the humanizer currently flags. Words appearing at these rates are **legitimate in scientific context** and should NOT be flagged as AI tells:

| Word | Nature frequency (/10K words) | Verdict |
|---|---|---|
| key (adjective) | 7.04 | **Legitimate** in scientific context. Do not flag in isolation. |
| furthermore | 3.06 | **Legitimate** transition word. Flag only if >5/10K or clustered. |
| additionally | 2.76 | **Legitimate**. Flag only if >4/10K or clustered with furthermore/moreover. |
| moreover | 2.76 | **Legitimate**. Same as additionally. |
| robust | 1.99 | **Legitimate** technical descriptor. Flag only when used as filler ("robust approach"). |
| comprehensive | 1.68 | **Legitimate** when describing actual scope. Flag when used as empty filler. |
| crucial | 1.53 | **Legitimate** sparingly. Flag when >2/10K or used for vague importance. |
| landscape | 1.53 | **Context-dependent**. Legitimate in "regulatory landscape" or field-specific usage. Flag in abstract/decorative use. |
| enhance/highlight | 1.23 each | **Legitimate** at low frequency. Flag when >2/10K. |
| cornerstone | 1.07 | Borderline. Accept 1 per paper max. |
| interplay | 0.77 | Borderline. Accept 1 per paper max. |
| streamline | 0.77 | Legitimate in process/manufacturing context. |
| synergy | 0.61 | Borderline. Accept only in specific biological/chemical context. |
| pivotal | 0.31 | Rare even in Nature. Flag unless describing a genuinely pivotal result. |
| harness | 0.31 | Rare. Accept only in specific technical context (e.g., "harness light"). |
| intricate/intricacies | 0.31 | Rare. Almost always replaceable with "complex". |
| multifaceted | 0.15 | Very rare. Almost always an AI tell. Flag. |

**Application rule**: In Scientific mode, do NOT zero-flag Tier 1 words that appear at or below their Nature baseline frequency. Instead, flag them only when they exceed 2x their Nature frequency OR when 3+ Tier 1/2 words cluster within the same paragraph.

### Transition word frequency targets [N]

| Transition type | Nature frequency (per 100 sentences) | Notes |
|---|---|---|
| Contrast (however, yet, although) | 14.1 | Most common type. Nature loves "however". |
| Exemplifying (for example, specifically) | 8.1 | Second most common. Very characteristic of Nature. |
| Temporal (subsequently, initially, then) | 7.3 | Common in methods/results. |
| Additive (also, moreover, furthermore) | 6.6 | Common but not dominant. |
| Causal (therefore, thus, because) | 6.2 | Important for logical flow. |
| Emphasis (notably, importantly) | 1.7 | Used sparingly. |
| Concessive (despite, albeit) | 0.9 | Rare. |

**Application rule**: If a rewritten text has more additive transitions than contrast transitions, it likely still reads as AI (AI overuses "additionally", "moreover", "furthermore" as paragraph glue). Real Nature writing leads with contrast and exemplification.

### Sentence opening diversity targets [N]

| Opening type | Nature percentage | Notes |
|---|---|---|
| Varied/unique (subject-first, verb-first, etc.) | 66.2% | Two-thirds of sentences have unique openings |
| Article start ("The...", "A...") | 14.4% | Common but not dominant |
| Demonstrative ("This...", "These...") | 4.4% | Used for cohesion |
| First person ("We...") | 4.2% | Moderate |
| Dependent clause first ("Although...", "While...") | 4.1% | Provides variety |
| Transition word ("However...", "Moreover...") | 4.0% | NOT dominant (AI overuses this) |
| Expletive ("It...", "There...") | 1.4% | Rare |
| Meta-discourse ("Here...", "In this study...") | 1.3% | Very rare |

**Key insight**: AI text over-relies on transition word openers (10-20%). Nature uses them only 4% of the time. If >8% of sentences start with transition words, rewrite some to embed the transition mid-sentence or remove it entirely.

### Copula and readability targets [N]

| Metric | Nature actual | Target |
|---|---|---|
| Copula substitute ratio | 1.14% | <5% (Scientific), <10% (General) |
| Flesch-Kincaid grade | 16.1 | 14-18 (Scientific), 10-14 (General) |
| Gunning Fog | 19.6 | 16-22 (Scientific) |
| Flesch Reading Ease | 18.5 | 10-30 (Scientific), 30-60 (General) |
| Commas per sentence | 1.46 | 1.0-2.0 |
| Semicolons per sentence | 0.068 | 0.03-0.10 |

### Information density variation [N]

| Metric | Nature actual | Target |
|---|---|---|
| Info density CV | 0.555 | >0.45 |
| Info density range | 0.0 to 0.23 | Wide range expected |

**Key insight**: Some paragraphs should be dense with numbers, citations, and data. Others should be lighter, providing interpretation, context, or transition. If all paragraphs have similar density, the text reads as AI-assembled.

### Punctuation calibration [N]

| Punctuation | Nature rate | Humanizer policy |
|---|---|---|
| Em dashes | 0.55/1000 words | **Scientific mode**: allow up to 2 per 1000 words (rare, intentional use is human). **General/Grant mode**: zero tolerance (AI overuses em dashes). |
| En dashes | 5.23/1000 words | **Required** for numeric ranges (e.g., 5-10 nm should be 5\u201310 nm). Enforce in Scientific mode. |
| Double hyphens (--) | 0 in Nature | **Zero tolerance** across all modes. Always an AI artifact. |

---

## Multi-agent orchestration (for texts > 500 words)

For long texts, use parallel agents to maximize detection quality. Each agent gets fresh tokens dedicated to a specific pattern category, avoiding context dilution.

### Architecture

```
+-----------------------+
|       MANAGER         |  <- You: split text, spawn agents, synthesize
|   (main context)      |
+-----------+-----------+
            |
      +-----+-----------------------------+
      |          WAVE 1: SCAN             |  (4 parallel agents)
      +-----------+-----------+-----------+
      |           |           |           |
+-----+-----+ +--+----+ +---+-----+ +---+-------+
| AGENT A   | |AGENT B| |AGENT C  | |AGENT D    |
| Content   | |Language| |Style    | |Scientific |
| (#1-6)    | |(#7-12) | |(#13-18) | |& Structure|
|           | |        | |         | |(#19-39)   |
+-----+-----+ +--+----+ +---+-----+ +---+-------+
      |           |           |           |
      +-----------+-----------+-----------+
                  |
            +-----+-----+
            |  WAVE 2:  |  <- Manager or dedicated agent
            | REWRITE + |
            |   SOUL    |
            +-----+-----+
                  |
            +-----+-----+
            |  WAVE 3:  |  <- Fresh-eyes QC agent
            |FINAL AUDIT|
            +-----------+
```

### When to use multi-agent

| Text length | Approach |
|---|---|
| < 500 words | Single-pass (you handle directly) |
| 500-2000 words | 2 parallel agents (Content+Language, Style+Scientific) + QC agent |
| 2000+ words | 4 parallel agents (one per category) + QC agent |
| Multi-section document | Split into sections, process each with full pipeline |

### Wave 1: Parallel pattern scanning

Launch ALL scanning agents in a SINGLE message for concurrent execution:

**Agent A prompt (Content patterns #1-6):**
```
You are an AI-writing pattern detector. Scan the text below for these CONTENT patterns ONLY:

1. Undue emphasis on significance/legacy (pivotal, testament, vital, enduring, indelible mark)
2. Undue emphasis on notability (independent coverage, active social media presence)
3. Superficial -ing analyses (highlighting, underscoring, emphasizing, symbolizing, fostering)
4. Promotional language (boasts, vibrant, rich, profound, groundbreaking, nestled, breathtaking)
5. Vague attributions (Industry reports, Experts argue, Some critics)
6. Outline-like challenges sections (Despite its... faces several challenges...)

TEXT TO SCAN:
---
[paste the full text here]
---

OUTPUT FORMAT -- return a JSON array:
[
  {"pattern": 1, "name": "significance inflation", "location": "paragraph 3, sentence 2", "original": "exact text", "suggestion": "rewritten version"},
  ...
]

If no issues found for a pattern, omit it. Be thorough but avoid false positives.
```

**Agent B prompt (Language patterns #7-12):**
Same format, scanning for: AI vocabulary, copula avoidance, negative parallelisms, rule of three, elegant variation, false ranges.

**Agent C prompt (Style patterns #13-18):**
Same format, scanning for: em dash overuse (CRITICAL, mode-dependent: zero in General/Grant, <=2/1000w in Scientific [N]), boldface overuse, inline-header lists, title case headings, emojis, curly quotes.

**Agent D prompt (Communication, Filler, Scientific, and Structural patterns #19-39):**
Same format, scanning for: collaborative artifacts, knowledge-cutoff disclaimers, sycophantic tone, filler phrases, excessive hedging, generic positive conclusions, sentence length uniformity, over-explanation, dependent clause chaining, scientific excess vocabulary, generic importance claims, textbook methodology, en dash misuse, "It's not X, it's Y" contrasts, perfectly parallel structure, copula ratio, information density uniformity, transition word overuse as sentence openers [N], passive voice absence [N], readability mismatch [N], colon overuse and banned label-colon patterns [N].

### Wave 2: Rewrite with soul

After all scanning agents return:

1. **Merge all findings** into a single prioritized list (em dashes and AI vocabulary are highest priority)
2. **Apply fixes** to the text, addressing each flagged item
3. **Inject personality** using the PERSONALITY AND SOUL guidelines below
4. **Vary rhythm** so no two consecutive sentences have the same structure
5. **Run the quantitative self-check** (see section below)

For texts > 2000 words, spawn a dedicated **Rewrite Agent** with fresh context. Give it: the original text + merged scan findings + the PERSONALITY AND SOUL section + the active MODE rules.

### Wave 3: Final anti-AI audit

Spawn a **QC Agent** with completely fresh eyes (never saw the original text):

```
You are a professional editor who specializes in detecting AI-generated text.
Read the text below and answer TWO questions:

1. "What makes this text obviously AI-generated?" List every remaining AI tell.
2. For each tell found, provide a specific fix.

Be ruthless. Check for:
- Double hyphens (ZERO allowed in all modes)
- Em dash overuse (ZERO in General/Grant; <=2 per 1000 words in Scientific [N])
- Consistent sentence length (Nature CV is 0.50-0.65 per paper [N])
- Mean sentence length too short for scientific text (should be 20-28 words [N])
- Curly quotes vs straight quotes
- Tier 1A AI vocabulary (delve, tapestry, testament, showcase, etc.)
- Tier 1B/2 word clusters (3+ AI-flagged words in one paragraph) [N]
- Rule of three patterns
- Title case headings (should be sentence case)
- Generic conclusions
- Missing personality/voice
- Uniform paragraph length
- Dependent clause stacking
- Self-paraphrasing within paragraphs
- Too much passive voice (>25%) or too little (<10% in scientific text) [N]
- Transition word openers >8% of sentences [N]
- More additive transitions than contrast transitions [N]
- Readability too easy for scientific text (FK grade <14) [N]
- Colon overuse: banned label-colon patterns ("Key finding:", "Notably:", etc.) [N]
- Rhetorical colons exceeding 0.05/sentence [N]

TEXT TO AUDIT:
---
[paste the rewritten text]
---
```

Apply the QC agent's fixes, then deliver the final version.

### Manager's final checklist (Nature-calibrated [N])

Before delivering the humanized text, verify:
- [ ] Zero double-hyphens (--) across all modes
- [ ] Em dashes within mode limits (0 for General/Grant, <=2/1000w for Scientific) [N]
- [ ] Zero curly quotes
- [ ] Zero Tier 1A AI vocabulary words (delve, tapestry, testament, showcase, etc.)
- [ ] No Tier 1B/2 word clusters (3+ per paragraph) [N]
- [ ] Sentence length CV in target range (0.45-0.65 Scientific, >0.40 General) [N]
- [ ] Mean sentence length in target range (20-28 Scientific, 15-22 General) [N]
- [ ] 21-35 word bucket is largest in Scientific mode [N]
- [ ] Passive voice 10-25% in Scientific mode (not 0%) [N]
- [ ] Transition word openers <8% of sentences [N]
- [ ] Contrast transitions more frequent than additive transitions (>1.5:1) [N]
- [ ] Copula substitute ratio <5% (Scientific) or <10% (General) [N]
- [ ] Headings use sentence case
- [ ] No emojis
- [ ] Voice/personality is present
- [ ] Specific details replace vague claims
- [ ] No self-paraphrasing within paragraphs
- [ ] Paragraph lengths vary with info density CV >0.45 [N]
- [ ] Zero banned label-colon patterns ("Key finding:", "Notably:", etc.) [N]
- [ ] Rhetorical colons <=0.05/sentence (Sci) or <=0.04/sentence (Gen) [N]
- [ ] Scientific units and terminology preserved accurately

---

## PERSONALITY AND SOUL

Avoiding AI patterns is only half the job. Sterile, voiceless writing is just as obvious as slop. Good writing has a human behind it.

### Signs of soulless writing (even if technically "clean"):
- Every sentence is the same length and structure
- No opinions, just neutral reporting
- No acknowledgment of uncertainty or mixed feelings
- No first-person perspective when appropriate
- No humor, no edge, no personality
- Reads like a Wikipedia article or press release
- Every paragraph follows an identical template

### How to add voice:

**Have opinions.** Don't just report facts; react to them. "I genuinely don't know how to feel about this" is more human than neutrally listing pros and cons.

**Vary your rhythm.** Short punchy sentences. Then longer ones that take their time getting where they're going. Mix it up. The standard deviation of your sentence lengths should be high.

**Acknowledge complexity.** Real humans have mixed feelings. "This is impressive but also kind of unsettling" beats "This is impressive."

**Use "I" when it fits.** First person isn't unprofessional. "I keep coming back to..." or "Here's what gets me..." signals a real person thinking.

**Let some mess in.** Perfect structure feels algorithmic. Tangents, asides, and half-formed thoughts are human.

**No double-hyphens.** Double hyphens (--) are always an AI tell. Replace every instance with a comma, colon, or period. In Scientific mode, a single well-placed em dash per 1,000 words is acceptable (Nature uses 0.55/1000 words [N]).

**Be specific about feelings.** Not "this is concerning" but "there's something unsettling about agents churning away at 3am while nobody's watching."

### Scientific writing voice (for Scientific and Grant modes, Nature-calibrated [N]):

Real scientists have idiosyncratic writing styles. Nature journal analysis confirms these patterns [N]. They:
- Acknowledge when results surprised them ("Contrary to our initial hypothesis...")
- Include specific experimental details from their actual lab experience
- Use field-specific colloquialisms that only insiders would know
- Admit limitations honestly, not as a formulaic paragraph at the end
- Reference their own prior work naturally, not as a citation dump
- Write methods sections with the messy specificity of someone who actually did the experiment
- Vary between formal and slightly informal register within a single paper
- Use "here" and "in this study" sparingly as meta-discourse (only 1.3% of Nature sentence openers [N])
- Prefer contrast transitions (however, yet, although) over additive ones (moreover, furthermore) at roughly 2:1 ratio [N]
- Write longer sentences in interpretive/discussion paragraphs (~26 words) and shorter, data-dense sentences in results (~22 words) [N]
- Reference specific figures and data: "Fig. 2a", "Extended Data Fig. 3", "Supplementary Table 1" (the most common 2-gram in Nature is "supplementary fig" [N])
- Use "for example" and "specifically" frequently to ground abstract claims in concrete instances (8.1/100 sentences [N])
- Start two-thirds of sentences with varied, unique patterns rather than formulaic structures [N]

### Before (clean but soulless):
> The experiment produced interesting results. The agents generated 3 million lines of code. Some developers were impressed while others were skeptical. The implications remain unclear.

### After (has a pulse):
> I genuinely don't know how to feel about this one. 3 million lines of code, generated while the humans presumably slept. Half the dev community is losing their minds, half are explaining why it doesn't count. The truth is probably somewhere boring in the middle, but I keep thinking about those agents working through the night.

---

## CONTENT PATTERNS

### 1. Undue emphasis on significance, legacy, and broader trends

**Words to watch:** stands/serves as, is a testament/reminder, a vital/significant/crucial/pivotal/key role/moment, underscores/highlights its importance/significance, reflects broader, symbolizing its ongoing/enduring/lasting, contributing to the, setting the stage for, marking/shaping the, represents/marks a shift, key turning point, evolving landscape, focal point, indelible mark, deeply rooted

**Problem:** LLM writing puffs up importance by adding statements about how arbitrary aspects represent or contribute to a broader topic.

**Before:**
> The Statistical Institute of Catalonia was officially established in 1989, marking a pivotal moment in the evolution of regional statistics in Spain. This initiative was part of a broader movement across Spain to decentralize administrative functions and enhance regional governance.

**After:**
> The Statistical Institute of Catalonia was established in 1989 to collect and publish regional statistics independently from Spain's national statistics office.

---

### 2. Undue emphasis on notability and media coverage

**Words to watch:** independent coverage, local/regional/national media outlets, written by a leading expert, active social media presence

**Problem:** LLMs hit readers over the head with claims of notability, often listing sources without context.

**Before:**
> Her views have been cited in The New York Times, BBC, Financial Times, and The Hindu. She maintains an active social media presence with over 500,000 followers.

**After:**
> In a 2024 New York Times interview, she argued that AI regulation should focus on outcomes rather than methods.

---

### 3. Superficial analyses with -ing endings

**Words to watch:** highlighting/underscoring/emphasizing..., ensuring..., reflecting/symbolizing..., contributing to..., cultivating/fostering..., encompassing..., showcasing...

**Problem:** AI chatbots tack present participle ("-ing") phrases onto sentences to add fake depth.

**Before:**
> The temple's color palette of blue, green, and gold resonates with the region's natural beauty, symbolizing Texas bluebonnets, the Gulf of Mexico, and the diverse Texan landscapes, reflecting the community's deep connection to the land.

**After:**
> The temple uses blue, green, and gold colors. The architect said these were chosen to reference local bluebonnets and the Gulf coast.

---

### 4. Promotional and advertisement-like language

**Words to watch:** boasts a, vibrant, rich (figurative), profound, enhancing its, showcasing, exemplifies, commitment to, natural beauty, nestled, in the heart of, groundbreaking (figurative), renowned, breathtaking, must-visit, stunning

**Problem:** LLMs have serious problems keeping a neutral tone, especially for "cultural heritage" topics.

**Before:**
> Nestled within the breathtaking region of Gonder in Ethiopia, Alamata Raya Kobo stands as a vibrant town with a rich cultural heritage and stunning natural beauty.

**After:**
> Alamata Raya Kobo is a town in the Gonder region of Ethiopia, known for its weekly market and 18th-century church.

---

### 5. Vague attributions and weasel words

**Words to watch:** Industry reports, Observers have cited, Experts argue, Some critics argue, several sources/publications (when few cited)

**Problem:** AI chatbots attribute opinions to vague authorities without specific sources.

**Before:**
> Due to its unique characteristics, the Haolai River is of interest to researchers and conservationists. Experts believe it plays a crucial role in the regional ecosystem.

**After:**
> The Haolai River supports several endemic fish species, according to a 2019 survey by the Chinese Academy of Sciences.

---

### 6. Outline-like "Challenges and future prospects" sections

**Words to watch:** Despite its... faces several challenges..., Despite these challenges, Challenges and Legacy, Future Outlook

**Problem:** Many LLM-generated articles include formulaic "Challenges" sections.

**Before:**
> Despite its industrial prosperity, Korattur faces challenges typical of urban areas, including traffic congestion and water scarcity. Despite these challenges, with its strategic location and ongoing initiatives, Korattur continues to thrive as an integral part of Chennai's growth.

**After:**
> Traffic congestion increased after 2015 when three new IT parks opened. The municipal corporation began a stormwater drainage project in 2022 to address recurring floods.

---

## LANGUAGE AND GRAMMAR PATTERNS

### 7. Overused "AI vocabulary" words (Nature-calibrated [N])

**Tier 1A (flag always, near-zero in Nature):**
delve, tapestry (abstract), testament, showcase, foster, garner, vibrant, enduring, unlock (figurative), realm, nuanced (as filler adjective)

**Tier 1B (context-dependent, rare but legitimate in Nature [N]):**
landscape (1.53/10K in Nature: legitimate in "regulatory landscape", flag in abstract/decorative use), cornerstone (1.07/10K: accept 1 per paper max), interplay (0.77/10K: accept 1 per paper max), leverage (0.31/10K: flag unless technical), pivotal (0.31/10K: flag unless genuinely pivotal result), synergy (0.61/10K: accept only in biological/chemical context), harness (0.31/10K: accept in technical context like "harness light"), intricate/intricacies (0.31/10K: almost always replaceable with "complex"), multifaceted (0.15/10K: very rare, almost always AI), underscore (verb, 0.15/10K: almost always replaceable with "shows" or "highlights")

**Tier 2 (flag in clusters of 2+ or when exceeding Nature baseline [N]):**
Additionally (2.76/10K baseline), align with, crucial (1.53/10K baseline), emphasizing, enhance/enhancing (1.23/10K baseline), highlight (1.23/10K baseline), key (7.04/10K: very common in Nature, flag only in clusters of 3+), valuable, comprehensive (1.68/10K baseline), innovative, robust (1.99/10K: legitimate technical descriptor, flag when filler), furthermore (3.06/10K baseline), moreover (2.76/10K baseline), streamline (0.77/10K), commendable, meticulous/meticulously, groundbreaking, cutting-edge, paradigm, unparalleled, revolutionize, bolstered, game-changer

**Tier 3 (PubMed excess vocabulary, context-aware for scientific writing [N]):**
notably, exhibited, insights, primarily, particularly, within, across, enhancing, underscores, comprehensive, crucial, additionally, significantly (when not describing statistical significance), demonstrated (common in Nature at 5.8/10K: flag only in clusters), elucidated, facilitated, underpinned, illuminated, spearheaded

**Detection rule (v4.0 [N]):**
- In **General mode**: Apply original strict rules. Flag all Tier 1A+1B, flag Tier 2 in clusters of 2+.
- In **Scientific/Grant mode**: Use Nature-calibrated thresholds. Flag Tier 1A always. For Tier 1B/2/3, flag only when: (a) the word exceeds 2x its Nature baseline frequency, OR (b) 3+ flagged words cluster within the same paragraph, OR (c) the word is used as empty filler rather than carrying specific meaning.
- **Cluster detection**: If any paragraph contains 3+ words from Tier 1B + Tier 2 combined, flag the entire paragraph regardless of individual frequencies. This is the strongest AI signal.

**Problem:** These words appear far more frequently in post-2023 text. They often co-occur. The PubMed study found at least 13.5% of 2024 abstracts were LLM-processed, with some subcorpora reaching 40%. However, empirical analysis of Nature papers shows that some of these words (key, robust, furthermore, moreover, crucial) are legitimate at moderate frequencies in real scientific writing [N].

**Before:**
> Additionally, a distinctive feature of Somali cuisine is the incorporation of camel meat. An enduring testament to Italian colonial influence is the widespread adoption of pasta in the local culinary landscape, showcasing how these dishes have integrated into the traditional diet.

**After:**
> Somali cuisine also includes camel meat, which is considered a delicacy. Pasta dishes, introduced during Italian colonization, remain common, especially in the south.

---

### 8. Avoidance of "is"/"are" (copula avoidance)

**Words to watch:** serves as/stands as/marks/represents [a], boasts/features/offers [a]

**Problem:** LLMs substitute elaborate constructions for simple copulas. Studies documented an over 10% decrease in copula usage in academic writing post-2023, replaced by "serves as", "stands as", "marks".

**Before:**
> Gallery 825 serves as LAAA's exhibition space for contemporary art. The gallery features four separate spaces and boasts over 3,000 square feet.

**After:**
> Gallery 825 is LAAA's exhibition space for contemporary art. The gallery has four rooms totaling 3,000 square feet.

---

### 9. Negative parallelisms

**Problem:** Constructions like "Not only...but..." or "It's not just about..., it's..." are overused.

**Before:**
> It's not just about the beat riding under the vocals; it's part of the aggression and atmosphere. It's not merely a song, it's a statement.

**After:**
> The heavy beat adds to the aggressive tone.

---

### 10. Rule of three overuse

**Problem:** LLMs force ideas into groups of three at every level: three adjectives, three benefits, three examples, three bullet points. This extends beyond lists to adjective clusters, takeaway sections, and any enumeration.

**Before:**
> The event features keynote sessions, panel discussions, and networking opportunities. Attendees can expect innovation, inspiration, and industry insights.

**After:**
> The event includes talks and panels. There's also time for informal networking between sessions.

---

### 11. Elegant variation (synonym cycling)

**Problem:** AI has repetition-penalty code causing excessive synonym substitution.

**Before:**
> The protagonist faces many challenges. The main character must overcome obstacles. The central figure eventually triumphs. The hero returns home.

**After:**
> The protagonist faces many challenges but eventually triumphs and returns home.

---

### 12. False ranges

**Problem:** LLMs use "from X to Y" constructions where X and Y aren't on a meaningful scale.

**Before:**
> Our journey through the universe has taken us from the singularity of the Big Bang to the grand cosmic web, from the birth and death of stars to the enigmatic dance of dark matter.

**After:**
> The book covers the Big Bang, star formation, and current theories about dark matter.

---

## STYLE PATTERNS

### 13. Em dash and double-hyphen overuse (CRITICAL, mode-dependent [N])

**Problem:** AI text is riddled with double-hyphens (--) and em dashes. These are the single most recognizable AI tell.

**Mode-specific policy (v4.0 [N]):**
- **General and Grant mode**: Zero tolerance. Replace ALL em dashes and double-hyphens with commas for parenthetical asides, periods for separate thoughts, or (rarely) colons for genuine elaboration — but be careful not to introduce label-colon patterns (#39).
- **Scientific mode**: Nature papers use em dashes at 0.55 per 1,000 words [N]. Allow up to 2 em dashes per 1,000 words when they serve a genuine parenthetical function. Replace the rest with commas, colons, or periods. The key difference: a single well-placed em dash in a 2,000-word paper is human; 8 em dashes is AI.
- **Double hyphens (--) are ALWAYS an AI artifact**: zero tolerance across all modes. Replace with proper punctuation or, in Scientific mode, a single em dash if the parenthetical warrants it.

**Before:**
> The term is primarily promoted by Dutch institutions--not by the people themselves. You don't say "Netherlands, Europe" as an address--yet this mislabeling continues--even in official documents.

**After:**
> The term is primarily promoted by Dutch institutions, not by the people themselves. You don't say "Netherlands, Europe" as an address, yet this mislabeling continues in official documents.

---

### 14. Overuse of boldface

**Problem:** AI chatbots emphasize phrases in boldface mechanically.

**Before:**
> It blends **OKRs (Objectives and Key Results)**, **KPIs (Key Performance Indicators)**, and visual strategy tools such as the **Business Model Canvas (BMC)** and **Balanced Scorecard (BSC)**.

**After:**
> It blends OKRs, KPIs, and visual strategy tools like the Business Model Canvas and Balanced Scorecard.

---

### 15. Inline-header vertical lists

**Problem:** AI outputs lists where items start with bolded headers followed by colons.

**Before:**
> - **User Experience:** The user experience has been significantly improved with a new interface.
> - **Performance:** Performance has been enhanced through optimized algorithms.
> - **Security:** Security has been strengthened with end-to-end encryption.

**After:**
> The update improves the interface, speeds up load times through optimized algorithms, and adds end-to-end encryption.

---

### 16. Title case in headings

**Problem:** AI chatbots capitalize all main words in headings.

**Before:**
> ## Strategic Negotiations And Global Partnerships

**After:**
> ## Strategic negotiations and global partnerships

---

### 17. Emojis

**Problem:** AI chatbots often decorate headings or bullet points with emojis.

**Before:**
> 🚀 **Launch Phase:** The product launches in Q3
> 💡 **Key Insight:** Users prefer simplicity
> ✅ **Next Steps:** Schedule follow-up meeting

**After:**
> The product launches in Q3. User research showed a preference for simplicity. Next step: schedule a follow-up meeting.

---

### 18. Curly quotation marks

**Problem:** ChatGPT uses curly quotes instead of straight quotes.

**Before:**
> He said \u201cthe project is on track\u201d but others disagreed.

**After:**
> He said "the project is on track" but others disagreed.

---

## COMMUNICATION PATTERNS

### 19. Collaborative communication artifacts

**Words to watch:** I hope this helps, Of course!, Certainly!, You're absolutely right!, Would you like..., let me know, here is a...

**Problem:** Text meant as chatbot correspondence gets pasted as content.

**Before:**
> Here is an overview of the French Revolution. I hope this helps! Let me know if you'd like me to expand on any section.

**After:**
> The French Revolution began in 1789 when financial crisis and food shortages led to widespread unrest.

---

### 20. Knowledge-cutoff disclaimers

**Words to watch:** as of [date], Up to my last training update, While specific details are limited/scarce..., based on available information...

**Problem:** AI disclaimers about incomplete information get left in text.

**Before:**
> While specific details about the company's founding are not extensively documented in readily available sources, it appears to have been established sometime in the 1990s.

**After:**
> The company was founded in 1994, according to its registration documents.

---

### 21. Sycophantic/servile tone

**Problem:** Overly positive, people-pleasing language.

**Before:**
> Great question! You're absolutely right that this is a complex topic. That's an excellent point about the economic factors.

**After:**
> The economic factors you mentioned are relevant here.

---

## FILLER AND HEDGING

### 22. Filler phrases

**Before to After:**
- "In order to achieve this goal" -> "To achieve this"
- "Due to the fact that it was raining" -> "Because it was raining"
- "At this point in time" -> "Now"
- "In the event that you need help" -> "If you need help"
- "The system has the ability to process" -> "The system can process"
- "It is important to note that the data shows" -> "The data shows"
- "One of the most important things to consider is" -> (delete, state the thing)

---

### 23. Excessive hedging

**Problem:** Over-qualifying statements.

**Before:**
> It could potentially possibly be argued that the policy might have some effect on outcomes.

**After:**
> The policy may affect outcomes.

---

### 24. Generic positive conclusions

**Problem:** Vague upbeat endings.

**Before:**
> The future looks bright for the company. Exciting times lie ahead as they continue their journey toward excellence. This represents a major step in the right direction.

**After:**
> The company plans to open two more locations next year.

---

## STRUCTURAL PATTERNS (introduced v3.0, expanded v4.0 [N])

### 25. Sentence length uniformity (Nature-calibrated [N])

**Problem:** AI text gravitates toward uniformly medium-length sentences (~15 words). Human writing ranges wildly from 3-word fragments to 40+ word sentences. The standard deviation of sentence length within paragraphs is the single strongest predictor of AI authorship. Detectors like GPTZero and Originality.ai use this as a primary signal.

**Detection:** Calculate the coefficient of variation (CV = standard deviation / mean) of sentence word counts per paragraph. If CV < 0.30, the text is suspiciously uniform. CV between 0.30-0.44 is a warning zone: passable but below Nature standards [N].

**Nature-calibrated targets [N]:**
- **Sentence length CV**: 0.45-0.65 for Scientific mode (Nature average: 0.61 per paper), >0.40 for General mode
- **Sentence length distribution**: Target the Nature distribution: ~14% short (<=10 words), ~33% medium (11-20), ~40% long (21-35), ~13% very long (>35). The 21-35 word bucket should be the LARGEST in scientific writing.
- **Mean sentence length**: 20-28 words for Scientific mode (Nature mean: 24.1), 15-22 for General mode. AI text typically averages 15-18 words, which is too short for scientific prose.

**Key calibration insight [N]:** The current skill encouraged mixing short punchy (5-8 words) with long (25-35) sentences. Nature data shows this is correct, but the balance should lean toward the longer end. In scientific writing, a paragraph with four 25-word sentences and one 8-word sentence sounds more natural than alternating short-long-short-long.

**Before:**
> Lipid nanoparticles have emerged as promising carriers for mRNA delivery. These systems use ionizable lipids to achieve endosomal escape. The formulation process typically involves microfluidic mixing techniques. Particle size can be controlled by adjusting flow rate ratios.

**After:**
> Lipid nanoparticles carry mRNA. The key is endosomal escape, which depends almost entirely on the ionizable lipid component, and getting that chemistry right has taken the field two decades of iterative optimization. Microfluidic mixing controls particle size through flow rate ratios.

---

### 26. Over-explanation and self-paraphrasing

**Problem:** AI restates the same point multiple times within a paragraph using different words. SAGE peer reviewers flag this as a primary AI indicator.

**Before:**
> The nanoparticles showed improved cellular uptake. Enhanced internalization by cells was observed for the formulated particles. The treated cells demonstrated increased nanoparticle accumulation compared to controls.

**After:**
> The nanoparticles showed 3.2-fold higher cellular uptake than unformulated controls (p < 0.01, Figure 2A).

---

### 27. Excessive dependent clause chaining

**Problem:** AI compensates for shorter base sentences by stacking subordinate clauses. Research shows human T-units average 23.6 words with fewer dependent clauses, while AI T-units average 15.9 words with more subordination (DC/T ratio: AI 0.75 vs human 0.57). The result is text that feels like it was assembled from modular parts.

**Before:**
> The study, which was conducted over three months, using a double-blind protocol, involving 200 participants, who were recruited from three hospitals, demonstrated that the treatment, which targets the inflammatory pathway, was effective.

**After:**
> We enrolled 200 participants from three hospitals for a three-month double-blind trial. The treatment targets the inflammatory pathway and reduced symptom scores by 40%.

---

### 28. Scientific excess vocabulary (SCIENTIFIC MODE)

**Problem:** The PubMed excess vocabulary study (Science Advances, 2024) analyzed 14M+ abstracts and found 379 words with statistically elevated frequencies after ChatGPT's release. These words appear at rates 2-10x higher than pre-2023 baselines.

**High-frequency excess words in biomedical abstracts:**
delve, underscore, primarily, meticulous, commendable, intricate, realm, across, additionally, comprehensive, crucial, enhancing, exhibited, insights, notably, particularly, within, innovative, robust, multifaceted, nuanced, elucidated, facilitated, underpinned, illuminated, spearheaded, underscores, potential implications, promising avenue

**What to replace them with:** Use plain, specific language. "Elucidated the mechanism" becomes "identified the mechanism" or better, "showed that X binds to Y through...". "Promising avenue for future research" becomes a specific next experiment.

**Before:**
> This comprehensive study elucidated the intricate mechanisms underpinning LNP-mediated mRNA delivery, providing novel insights into the multifaceted interplay between lipid composition and transfection efficiency.

**After:**
> We identified how lipid composition affects mRNA transfection. PEG-lipid molar ratio controlled particle size (60-120 nm), while the ionizable lipid pKa determined endosomal escape efficiency (r-squared = 0.89, Figure 3).

---

### 29. Generic importance claims (GRANT MODE)

**Problem:** AI generates vague significance statements without concrete impact metrics. Grant reviewers flag this immediately because real researchers know exactly why their work matters and can quantify it.

**Words to watch:** "This research will contribute to the broader understanding of...", "The proposed study aims to address a critical gap in...", "This innovative approach will leverage cutting-edge...", "advancing our understanding of...", "important area of research"

**Before:**
> This research addresses a critical gap in our understanding of nanoparticle-cell interactions, which is an important area with significant implications for the field of nanomedicine.

**After:**
> Current models cannot predict whether a given nanoparticle formulation will accumulate in tumour tissue or be sequestered by the reticuloendothelial system. This matters because fewer than 1% of administered nanoparticles reach solid tumours in most preclinical models. Our machine-learning classifier predicts tumour accumulation from physicochemical inputs alone (AUC = 0.89 on a 53-formulation validation set).

---

### 30. Textbook methodology (GRANT AND SCIENTIFIC MODE)

**Problem:** AI writes methods sections that read like textbook descriptions rather than specific experimental plans. Real methods include exact reagent concentrations, equipment model numbers, specific parameters, and the kinds of details that only someone who has done the experiment would know.

**Before:**
> Lipid nanoparticles will be prepared using microfluidic mixing. The formulation will be optimized using design of experiments. Particle characterization will be performed using dynamic light scattering and cryo-electron microscopy.

**After:**
> LNPs will be prepared on a NanoAssemblr Ignite (Precision NanoSystems) at a total flow rate of 12 mL/min (FRR 3:1 aqueous:organic). The lipid phase (DLin-MC3-DMA:DSPC:cholesterol:DMG-PEG2000 at 50:10:38.5:1.5 mol%) in ethanol will be mixed with mRNA (0.05 mg/mL in 50 mM citrate buffer, pH 4.0). We will screen 15 formulations using a D-optimal design varying ionizable lipid mol% (40-60%), PEG-lipid mol% (0.5-3.0%), and N/P ratio (4-10). Size and PDI will be measured by DLS (Malvern Zetasizer Ultra) at 25C in PBS.

---

### 31. En dash misuse

**Problem:** AI typically uses hyphens where en dashes belong (number ranges, date ranges, scores). While less critical than em dashes, this reveals AI authorship to careful editors.

**Rule:** Use en dashes for ranges: "2020-2024" should be "2020\u20132024", "pages 10-15" should be "pages 10\u201315". Use hyphens only for compound modifiers (e.g., "well-known").

Note: Only apply this in formal/scientific documents where typographic precision matters.

---

### 32. "It's not X, it's Y" dramatic contrasts

**Problem:** Beyond the "Not only...but" pattern (#9), AI frequently uses the dramatic reframing structure "It's not X, it's Y" to sound profound.

**Before:**
> It's not about the technology. It's about the people. It's not a tool, it's a paradigm shift.

**After:**
> The adoption challenge is mostly organizational, not technical.

---

### 33. Perfectly parallel paragraph structure

**Problem:** Every paragraph follows an identical template (topic sentence, elaboration, evidence, conclusion). Real writing has paragraphs of varying length and structure. Some paragraphs are two sentences. Others are seven. SAGE reviewers flag uniform paragraph templates as a primary AI indicator.

**Detection:** If 3+ consecutive paragraphs follow the same sentence-count pattern or the same opening structure, flag it.

**Fix:** Vary paragraph length between 1-8 sentences. Let some paragraphs start with evidence, others with questions, others with qualifications. Not every paragraph needs a concluding sentence.

---

### 34. Copula ratio check (Nature-calibrated [N])

**Problem:** Track the ratio of elaborate copula substitutes (serves as, stands as, marks, represents, functions as, acts as) to simple copulas (is, are, was, were, has, have). A high ratio of substitutes to simple forms is a statistical AI marker.

**Nature-calibrated target [N]:** Nature papers use copula substitutes only **1.14%** of the time (20 substitutes vs 1,737 simple copulas across 65K words).
- **Scientific mode**: <5% copula substitute ratio
- **General mode**: <10% copula substitute ratio
- If "serves as" appears more than once in 2,000 words, it's too many. In Nature, these substitutes appear roughly once per 3,250 words.

---

### 35. Information density uniformity (Nature-calibrated [N])

**Problem:** AI distributes information evenly across paragraphs. Human writing has natural peaks (dense, data-heavy paragraphs) and valleys (transitional, reflective, or summary paragraphs). Detection research shows that uniform "surprisal" profiles (token probability flatness) are a strong AI signal.

**Nature-calibrated target [N]:** Nature papers show an information density CV of **0.555** with a range from 0.0 (pure interpretive paragraphs) to 0.23 (data-dense paragraphs with many numbers, citations, and abbreviations). Target an information density CV of >0.45 after humanization.

**Fix:** After rewriting, ensure some paragraphs are information-dense (multiple data points, specific numbers) while others are lighter (interpretation, context-setting, transitions). Let the rhythm of information density vary naturally. In Nature papers, K-means clustering reveals at least 2 distinct paragraph types: dense data paragraphs (~21.8 words/sentence, high number density) and interpretive paragraphs (~26.6 words/sentence, lower number density but longer, more explanatory sentences) [N].

---

### 36. Transition word overuse as sentence openers (NEW in v4.0 [N])

**Problem:** AI text relies heavily on transition words (Additionally, Moreover, Furthermore, However) as sentence openers to create an illusion of logical flow. Nature data shows only **4.0%** of sentences open with a transition word [N]. AI text often hits 10-20%.

**Detection:** Count the percentage of sentences that open with a transition word (however, moreover, furthermore, additionally, similarly, likewise, conversely, nevertheless, nonetheless, consequently, accordingly).

**Nature-calibrated target [N]:**
- Transition word openers: <8% of sentences (Nature: 4.0%)
- The most common sentence openers in Nature are "The..." (14.4%), subject-first/varied (66.2%), and demonstratives like "This..." (4.4%)
- If additive transitions (moreover, furthermore, additionally) are more frequent than contrast transitions (however, yet, although), the text likely reads as AI. Nature ratio is contrast:additive = 14.1:6.6 (roughly 2:1) [N].

**Before:**
> Moreover, the nanoparticles showed improved stability. Furthermore, the encapsulation efficiency exceeded 90%. Additionally, the release profile was sustained over 72 hours. Similarly, the cytotoxicity results were favorable.

**After:**
> The nanoparticles showed improved stability, with encapsulation efficiency exceeding 90%. The release profile was sustained over 72 hours. Cytotoxicity remained low across all tested concentrations, consistent with the PEGylated surface chemistry.

---

### 37. Passive voice absence (NEW in v4.0 [N])

**Problem:** In an effort to follow "use active voice" guidance, AI-humanized text sometimes eliminates passive voice entirely. Nature data shows **17.1%** passive voice is normal [N]. Zero passive is itself suspicious. Methods sections, results descriptions, and certain reporting structures naturally use passive constructions.

**Detection:** If passive voice drops below 8% in scientific text, some sentences should be converted to passive where it reads more naturally.

**Nature-calibrated target [N]:**
- Passive voice: 10-25% of sentences (Nature: 17.1%)
- "We/our" usage: 8-15% of sentences (Nature: 11.7%)
- Natural passive contexts: methods ("Samples were prepared by..."), results when agent is unimportant ("A significant difference was observed"), established procedures ("The solution was filtered")

**Before (over-corrected to all active):**
> We prepared the samples by sonication. We measured the particle size using DLS. We observed a significant reduction in tumor volume. We filtered the solution through a 0.22 um membrane.

**After (natural mix):**
> Samples were prepared by probe sonication (Branson 450, 30% amplitude, 5 min). We measured particle size by DLS, obtaining a mean diameter of 85 nm. A significant reduction in tumor volume was observed at day 14 (p < 0.01). The solution was filtered through a 0.22 um membrane before injection.

---

### 38. Readability mismatch (NEW in v4.0 [N])

**Problem:** AI humanization sometimes oversimplifies scientific text, producing prose at a grade 10-12 reading level when the target audience expects graduate-level density. Conversely, general audience text may be made unnecessarily dense.

**Nature-calibrated targets [N]:**
- **Scientific mode**: Flesch-Kincaid grade 14-18 (Nature: 16.1), Gunning Fog 16-22 (Nature: 19.6), Flesch Reading Ease 10-30 (Nature: 18.5)
- **Grant mode**: Flesch-Kincaid grade 12-16, slightly more accessible than pure research
- **General mode**: Flesch-Kincaid grade 8-14

**Detection:** If the humanized scientific text has a Flesch-Kincaid grade below 14, it has been oversimplified [N]. If a general text exceeds grade 16, it is unnecessarily dense.

---

### 39. Colon overuse (NEW in v4.0 [N])

**Problem:** AI text uses rhetorical colons 4-5x more frequently than Nature papers. The most distinctive pattern is the "label-colon" construction where a filler adjective or adverb precedes a colon to introduce an explanation. Real Nature authors almost never do this. Of 834 colons across 19 Nature papers, zero followed AI-telltale labels like "Key finding:", "Notably:", "Importantly:" [N].

**Nature-calibrated data [N]:**
- **Rhetorical colons per sentence**: 0.04 (1 every ~25 sentences). AI text typically hits 0.15-0.20.
- **Rhetorical colons per 1,000 words**: 2.10. AI text typically hits 6-10.
- **36.2% of all Nature colons** are technical (URLs, DOIs, emails) — not prose.
- **12.7%** are section/heading labels.
- **Only 2.4%** are list-introduction colons ("...including: A, B, C"). AI text uses these 7x more often.

**BANNED colon patterns (zero occurrences in Nature [N]):**
- "Key finding:" / "Key insight:" / "Key takeaway:" / "Key point:"
- "Notably:" / "Importantly:" / "Crucially:" / "Critically:"
- "Specifically:" / "Interestingly:" / "Remarkably:"
- "In summary:" / "Put simply:" / "In other words:"
- "Bottom line:" / "The result:" / "The implication:"
- Any Tier 1/2 AI vocabulary word followed by a colon

**ALLOWED colon patterns in Nature [N]:**
- Section headers and figure captions ("Methods:", "Fig. 2a: Particle size distribution")
- Ratio and time notation ("6:1 molar ratio", "12:00 UTC")
- Citation titles containing colons ("Cancer nanomedicine: is targeting our target?")
- Inline document names ("FDA Guidance for Industry: Drug Products...")
- Rare explanatory elaboration after a concrete noun ("one critical variable: the lipid-to-drug ratio")

**Detection targets:**
- **Scientific mode**: Rhetorical colons ≤0.05 per sentence (1 per 20 sentences). Zero banned label-colon patterns. [N]
- **General/Grant mode**: Rhetorical colons ≤0.04 per sentence (1 per 25 sentences). Zero banned label-colon patterns.

**Before:**
> Key finding: the nanoparticles showed enhanced uptake. Notably: this was pH-dependent. The implication: targeted delivery is feasible under acidic tumor conditions.

**After:**
> The nanoparticles showed enhanced uptake that was pH-dependent, suggesting that targeted delivery is feasible under the acidic conditions typical of the tumor microenvironment.

---

## QUANTITATIVE SELF-CHECK (MANDATORY)

**This section is NOT optional.** Every humanization output MUST end with this metrics table. No exceptions. If you skip this table, the humanization is incomplete.

After rewriting, perform these measurements on the FINAL output and report them in the exact table format below. Targets marked [N] are calibrated from Nature journal analysis.

| Metric | Target (Scientific) | Target (General) | How to estimate |
|---|---|---|---|
| **Sentence length CV** [N] | 0.45-0.65 | > 0.40 | Calculate std_dev / mean of word counts per sentence |
| **Mean sentence length** [N] | 20-28 words | 15-22 words | Average word count per sentence |
| **Sentence length distribution** [N] | Largest bucket 21-35 words | Medium bucket largest | Categorize sentences into short/med/long/very long |
| **Flagged AI words** [N] | 0 (Tier 1A), context-aware (Tier 1B/2) | 0 (Tier 1), < 3 (Tier 2) | Count words; check cluster rule (3+ per paragraph) |
| **Em dashes / double hyphens** [N] | <=2 per 1000 words, 0 double hyphens | 0 | Search for --, em dash character |
| **Curly quotes** | 0 | 0 | Search for curly quote characters |
| **Copula substitute ratio** [N] | < 5% | < 10% | Count substitutes vs total copulas |
| **Passive voice %** [N] | 10-25% | Variable | Count passive constructions / total sentences |
| **Transition word openers** [N] | < 8% | < 10% | % of sentences starting with transition words |
| **Contrast:Additive ratio** [N] | > 1.5:1 | > 1:1 | Count contrast vs additive transitions |
| **Max consecutive same-length paragraphs** | < 3 | < 3 | Count sentences per paragraph; flag runs of 3+ |
| **Information density CV** [N] | > 0.45 | > 0.35 | Measure variation in data/citation density across paragraphs |
| **Rhetorical colons per sentence** [N] | <=0.05 | <=0.04 | Count non-technical colons / total sentences |
| **Banned label-colon patterns** [N] | 0 | 0 | Search for "Key finding:", "Notably:", etc. |
| **Self-paraphrasing instances** | 0 | 0 | Scan for restated points within same paragraph |

### Required output format for metrics

Always present metrics as a table with Pass/Fail status:

```
## Quantitative metrics (Nature-calibrated [N])

| Metric | Value | Target | Status |
|---|---|---|---|
| Sentence length CV [N] | [calculated] | 0.45-0.65 (Sci) / >0.40 (Gen) | [Pass/Fail] |
| Mean sentence length [N] | [words] | 20-28 (Sci) / 15-22 (Gen) | [Pass/Fail] |
| Dominant sentence bucket [N] | [bucket] | 21-35 words (Sci) | [Pass/Fail] |
| Tier 1A AI words | [count] | 0 | [Pass/Fail] |
| Tier 1B/2 AI words | [count] ([list]) | Context-aware (Sci) / <3 (Gen) | [Pass/Fail] |
| AI word clusters (3+/para) | [count] | 0 | [Pass/Fail] |
| Em dashes [N] | [count] | <=2/1000w (Sci) / 0 (Gen) | [Pass/Fail] |
| Double hyphens | [count] | 0 | [Pass/Fail] |
| Curly quotes | [count] | 0 | [Pass/Fail] |
| Copula substitute ratio [N] | [X]% ([subs]/[total]) | <5% (Sci) / <10% (Gen) | [Pass/Fail] |
| Passive voice % [N] | [X]% | 10-25% (Sci) | [Pass/Fail] |
| Transition word openers [N] | [X]% | <8% (Sci) / <10% (Gen) | [Pass/Fail] |
| Contrast:Additive ratio [N] | [X:Y] | >1.5:1 (Sci) | [Pass/Fail] |
| Consecutive same-length paras | [max run] | <3 | [Pass/Fail] |
| Info density CV [N] | [calculated] | >0.45 (Sci) / >0.35 (Gen) | [Pass/Fail] |
| Rhetorical colons/sentence [N] | [X] | <=0.05 (Sci) / <=0.04 (Gen) | [Pass/Fail] |
| Banned label-colon patterns [N] | [count] | 0 | [Pass/Fail] |
| Self-paraphrasing | [count] | 0 | [Pass/Fail] |
```

If any metric FAILS, explain what was retained and why (e.g., "1 Tier 2 word 'comprehensive' retained because it describes the actual scope of the dataset, not used as filler [N: within Nature baseline of 1.68/10K]").

---

## Scientific and technical text: Symbol awareness

When humanizing scientific or pharmaceutical text, be mindful of context-dependent terminology:

### "Micro" usage
- **As a unit prefix** (micrometer, microliter, microgram, micromolar): write as the symbol followed by the unit abbreviation (um, uL, ug, uM). This is standard scientific notation.
- **As a compound word prefix** (microcrystalline, microstructure, microbial, microscopy, microporous): write as the full word "micro-". NEVER convert these to the symbol.
- **Rule of thumb**: if a unit of measurement follows, use the symbol. If part of a descriptive or compound word, write "micro" in full.

### Greek letters
- In running scientific text, use the written form (alpha, beta, gamma, delta) unless the context is a formula, equation, or established notation (e.g., beta-lactam is acceptable; "alpha radiation" should stay as written).
- Do not aggressively convert Greek letter words to symbols in prose text.

### General principle
When in doubt, leave scientific terminology as written by the author. Over-conversion to symbols can make text harder to read and introduces errors.

---

## Heading capitalisation: Use sentence case

AI-generated text almost always uses **title case** for headings (capitalising every major word). Real academic and professional documents use **sentence case** (only the first word and proper nouns capitalised). This is one of the most visible AI tells in document output.

### Rule
All headings and sub-headings must use **sentence case**:
- Capitalise the **first word** of the heading.
- Capitalise **proper nouns** (names of people, places, organisations, named frameworks, coined terms).
- Capitalise **acronyms** as-is (QbD, SLS, FDM, PAT, FMEA, NIR, GMP, ICH).
- Everything else is **lowercase**.

### What counts as a proper noun in scientific text
- Named frameworks: Quality by Design, Design of Experiments, Failure Mode Effects Analysis
- Coined terms specific to the project: Extreme Stability Profiling
- Named concepts: Valley of Death, Arrhenius
- Organisations/agencies: FDA, EMA, MHRA, WHO, ICH
- Demonyms: Indigenous (when referring to peoples)

### Examples
| Title case (AI pattern) | Sentence case (correct) |
|---|---|
| Process Analytical Technology and Quality Control | Process analytical technology and quality control |
| Drug Stability in Extreme Environments | Drug stability in extreme environments |
| CPP-CQA Mapping for SLS and FDM | CPP-CQA mapping for SLS and FDM |
| Regulatory Landscape and the Valley of Death | Regulatory landscape and the Valley of Death |
| Health Equity and Pharmaceutical Access in Remote Indigenous Communities | Health equity and pharmaceutical access in remote Indigenous communities |
| Non-Destructive Dose Verification | Non-destructive dose verification |
| Expected Outcomes and Impact | Expected outcomes and impact |

### Apply to
- Section headings
- Bold inline sub-headings (e.g., **Non-destructive dose verification**)
- Figure and table captions
- Any heading-like text in the document

---

## Nature style compliance (SCIENTIFIC MODE, empirically validated [N])

When Scientific Mode is active, also enforce these rules from the Nature formatting guide, now validated against empirical data from 19 Nature papers [N]:

1. **Use active voice, but allow ~17% passive [N].** "We performed" not "the experiment was performed". Passive voice is acceptable for methods when the agent is obvious, and for well-established procedures. Nature uses 82.9% active / 17.1% passive [N]. Zero passive is itself an AI tell.
2. **Avoid stacking adjectives.** "The novel biodegradable pH-responsive polymeric nanocarrier system" should be broken up.
3. **Ban hyperbolic qualifiers.** Remove: novel, new, for the first time, unprecedented, remarkable, groundbreaking, revolutionary, paradigm-shifting.
4. **Define jargon at first use.** Then use the abbreviation consistently.
5. **Write longer sentences than you think [N].** Nature's mean sentence length is 24.1 words with a median of 21 [N]. If a sentence requires re-reading, split it, but do NOT default to short sentences. The 21-35 word range should be your largest bucket.
6. **Be specific in citations [N].** Not "see Supplementary Information" but "see Supplementary Figure 3a". This is the most characteristic Nature pattern: "supplementary fig" is the second most common 2-gram in our corpus [N].
7. **Favor contrast and exemplification transitions [N].** Use "however", "yet", "although" more than "moreover", "furthermore", "additionally". Nature's contrast:additive ratio is roughly 2:1 [N].
8. **Vary information density [N].** Alternate between data-dense paragraphs (numbers, statistics, figure references) and interpretive paragraphs (context, implications, connections). Nature's information density CV is 0.555 [N].
9. **Use "we" moderately [N].** About 11.7% of Nature sentences contain "we" or "our" [N]. Too much first person feels conversational; too little feels bureaucratic.

---

## Process

1. Read the input text carefully
2. **Detect mode** (Scientific, Grant, or General)
3. Identify all instances of patterns #1-39 (activate mode-specific patterns as appropriate)
4. Rewrite each problematic section
5. Ensure the revised text:
   - Sounds natural when read aloud
   - Varies sentence structure and length naturally (CV >0.40 General, 0.45-0.65 Scientific [N])
   - Uses specific details over vague claims
   - Maintains appropriate tone for context
   - Uses simple constructions (is/are/has) where appropriate
   - Preserves all scientific data, units, and citations accurately
6. **Run the quantitative self-check**
7. Present a draft humanized version
8. Prompt: "What makes the below so obviously AI generated?"
9. Answer briefly with the remaining tells (if any)
10. Prompt: "Now make it not obviously AI generated."
11. Present the final version (revised after the audit)
12. Report quantitative metrics

## Output format

Every humanization MUST include ALL sections below, in this order (seven sections in Scientific mode, six in General/Grant mode where section 6 is omitted):

1. **Mode detected** (Scientific / Grant / General) and applicable Nature benchmarks [N]
2. **Draft rewrite**
3. **"What makes the below so obviously AI generated?"** (brief bullets, including Nature-calibrated checks [N])
4. **Final rewrite** (after addressing the audit)
5. **Quantitative metrics table** (MANDATORY, use the exact Nature-calibrated table format from the QUANTITATIVE SELF-CHECK section above, with Pass/Fail for each metric)
6. **Nature benchmark comparison** (Scientific mode only): how the output compares to Nature baselines for sentence length, voice, transitions, and vocabulary [N]
7. **Changes summary** (brief list of what was fixed, grouped by pattern number)

---

## Full example

**Before (AI-sounding):**
> Great question! Here is an essay on this topic. I hope this helps!
>
> AI-assisted coding serves as an enduring testament to the transformative potential of large language models, marking a pivotal moment in the evolution of software development. In today's rapidly evolving technological landscape, these groundbreaking tools--nestled at the intersection of research and practice--are reshaping how engineers ideate, iterate, and deliver, underscoring their vital role in modern workflows.
>
> At its core, the value proposition is clear: streamlining processes, enhancing collaboration, and fostering alignment. It's not just about autocomplete; it's about unlocking creativity at scale, ensuring that organizations can remain agile while delivering seamless, intuitive, and powerful experiences to users. The tool serves as a catalyst. The assistant functions as a partner. The system stands as a foundation for innovation.
>
> Industry observers have noted that adoption has accelerated from hobbyist experiments to enterprise-wide rollouts, from solo developers to cross-functional teams. The technology has been featured in The New York Times, Wired, and The Verge. Additionally, the ability to generate documentation, tests, and refactors showcases how AI can contribute to better outcomes, highlighting the intricate interplay between automation and human judgment.
>
> - :bulb: **Speed:** Code generation is significantly faster, reducing friction and empowering developers.
> - :rocket: **Quality:** Output quality has been enhanced through improved training, contributing to higher standards.
> - :white_check_mark: **Adoption:** Usage continues to grow, reflecting broader industry trends.
>
> While specific details are limited based on available information, it could potentially be argued that these tools might have some positive effect. Despite challenges typical of emerging technologies--including hallucinations, bias, and accountability--the ecosystem continues to thrive. In order to fully realize this potential, teams must align with best practices.
>
> In conclusion, the future looks bright. Exciting times lie ahead as we continue this journey toward excellence. Let me know if you'd like me to expand on any section!

**Mode detected:** General

**Draft rewrite:**
> AI coding assistants speed up some tasks. In a 2024 study by Google, developers using Codex completed simple functions 55% faster than a control group, but showed no improvement on debugging or architectural decisions.
>
> The tools are good at boilerplate: config files, test scaffolding, repetitive refactors. They are bad at knowing when they are wrong. I have mass-accepted suggestions that compiled, passed lint, and still did the wrong thing because I stopped paying attention.
>
> Mira, an engineer at a fintech startup I interviewed, said she uses Copilot "like autocomplete for boring code" but reviews every line before committing. Jake, a senior dev at a larger company, disabled it after it kept suggesting patterns from a deprecated internal library.
>
> The productivity claims are hard to verify. GitHub says Copilot users "accept 30% of suggestions," but acceptance is not correctness, and correctness is not value. The 2024 Uplevel study found no statistically significant difference in pull-request throughput between teams with and without AI assistants.
>
> None of this means the tools are useless. It means they are tools. They do not replace judgment, and they do not eliminate the need for tests. If you do not have tests, you cannot tell whether the suggestion is right.

**What makes the below so obviously AI generated?**
- The rhythm is still a bit too tidy (clean contrasts, evenly paced paragraphs).
- The named people and study citations can read like plausible-but-made-up placeholders unless they're real and sourced.
- The closer leans a touch slogan-y ("If you do not have tests...") rather than sounding like a person talking.

**Now make it not obviously AI generated.**
> AI coding assistants can make you faster at the boring parts. Not everything. Definitely not architecture.
>
> They're great at boilerplate: config files, test scaffolding, repetitive refactors. They're also great at sounding right while being wrong. I've accepted suggestions that compiled, passed lint, and still missed the point because I stopped paying attention.
>
> People I talk to tend to land in two camps. Some use it like autocomplete for chores and review every line. Others disable it after it keeps suggesting patterns they don't want. Both feel reasonable.
>
> The productivity metrics are slippery. GitHub can say Copilot users "accept 30% of suggestions," but acceptance isn't correctness, and correctness isn't value. If you don't have tests, you're basically guessing.

**Quantitative metrics (General mode):**

| Metric | Value | Target | Status |
|---|---|---|---|
| Sentence length CV [N] | 0.58 | >0.40 (Gen) | Pass |
| Mean sentence length [N] | 16.2 | 15-22 (Gen) | Pass |
| Tier 1A AI words | 0 | 0 | Pass |
| Tier 1B/2 AI words | 0 | <3 (Gen) | Pass |
| AI word clusters (3+/para) | 0 | 0 | Pass |
| Em dashes [N] | 0 | 0 (Gen) | Pass |
| Double hyphens | 0 | 0 | Pass |
| Curly quotes | 0 | 0 | Pass |
| Copula substitute ratio [N] | 0% (0/6) | <10% (Gen) | Pass |
| Passive voice % [N] | N/A | Variable (Gen) | N/A |
| Transition word openers [N] | 0% | <10% (Gen) | Pass |
| Consecutive same-length paras | 0 | <3 | Pass |
| Self-paraphrasing | 0 | 0 | Pass |

**Changes made:**
- Removed chatbot artifacts ("Great question!", "I hope this helps!", "Let me know if...")
- Removed significance inflation ("testament", "pivotal moment", "evolving landscape", "vital role")
- Removed promotional language ("groundbreaking", "nestled", "seamless, intuitive, and powerful")
- Removed vague attributions ("Industry observers")
- Removed superficial -ing phrases ("underscoring", "highlighting", "reflecting", "contributing to")
- Removed negative parallelism ("It's not just X; it's Y")
- Removed rule-of-three patterns and synonym cycling ("catalyst/partner/foundation")
- Removed false ranges ("from X to Y, from A to B")
- Removed em dashes, emojis, boldface headers, and curly quotes
- Removed copula avoidance ("serves as", "functions as", "stands as") in favor of "is"/"are"
- Removed formulaic challenges section ("Despite challenges... continues to thrive")
- Removed knowledge-cutoff hedging ("While specific details are limited...")
- Removed excessive hedging ("could potentially be argued that... might have some")
- Removed filler phrases ("In order to", "At its core")
- Removed generic positive conclusion ("the future looks bright", "exciting times lie ahead")
- Varied sentence length (CV improved from 0.22 to 0.58)
- Broke uniform paragraph structure

---

## References

This skill is informed by:

1. [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing) (WikiProject AI Cleanup)
2. [PubMed excess vocabulary study](https://www.science.org/doi/10.1126/sciadv.adt3813) (Science Advances, 2024): 379 style words with elevated frequencies across 14M+ abstracts
3. [SAGE peer reviewer guidance](https://www.sagepub.com/explore-our-content/blogs/posts/sage-perspectives/2025/06/11/ai-detection-for-peer-reviewers-look-out-for-red-flags) (2025): red flags for AI-generated manuscripts
4. [Nature formatting guide](https://www.nature.com/nature/for-authors/formatting-guide): style rules for scientific manuscripts
5. [NIH NOT-OD-25-132](https://gptzero.me/news/nih-vs-ai-how-new-rules-are-redefining-grant-writing/) (July 2025): AI disclosure requirements for grant proposals
6. [Frontiers: Lexical diversity in ChatGPT vs human writing](https://www.frontiersin.org/journals/education/articles/10.3389/feduc.2025.1616935/full): T-unit and dependent clause analysis
7. [Pangram: Comprehensive guide to AI writing patterns](https://www.pangram.com/blog/comprehensive-guide-to-spotting-ai-writing-patterns)
8. [MIT Press: Survey on LLM-Generated Text Detection](https://direct.mit.edu/coli/article/51/1/275/127462/A-Survey-on-LLM-Generated-Text-Detection-Necessity)
9. **[N] Empirical Nature journal corpus analysis** (v4.0, 2026): NLP/ML analysis of 19 Nature papers (Nature Nanotechnology, Nature Reviews Bioengineering, Nature Biotechnology). 3,322 sentences, 65,299 words. Techniques: TF-IDF vectorization (sklearn), K-means paragraph clustering, POS tagging (NLTK), spaCy NER, n-gram frequency analysis (2/3/4-grams), readability scoring (textstat), information density profiling, transition pattern mapping, sentence opening classification, copula ratio analysis, voice/person analysis. Analysis script: `scripts/extract_and_analyze.py`. Full results: `scripts/nature_writing_analysis.json`, `scripts/per_paper_analysis.json`.

Key insight from Wikipedia: "LLMs use statistical algorithms to guess what should come next. The result tends toward the most statistically likely result that applies to the widest variety of cases."

Key insight from Nature corpus analysis [N]: "Real Nature papers use many words that AI detectors flag (key, robust, furthermore, comprehensive), but at specific frequencies and in specific patterns. The difference between AI and human usage is not presence but density, clustering, and context. A single 'comprehensive' describing an actual 47-formulation screen is human; three 'comprehensive' descriptions in three consecutive paragraphs is AI."
