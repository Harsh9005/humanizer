# Humanizer v4.0 — Data-Driven AI Writing Pattern Removal

A Claude Code skill that removes signs of AI-generated writing from text, optimized for scientific, academic, and grant writing. **v4.0 is empirically calibrated against 19 Nature journal papers using NLP/ML techniques.**

## What's new in v4.0

### Empirical Nature journal calibration

v4.0 is built on NLP/ML analysis of **19 Nature papers** (Nature Nanotechnology, Nature Reviews Bioengineering, Nature Biotechnology) — 3,322 sentences and 65,299 words. Every target marked with **[N]** is derived from this dataset.

**Techniques used:**
- TF-IDF vectorization for vocabulary profiling
- K-means clustering for paragraph structure identification (data-dense vs. interpretive)
- POS tagging for voice and person analysis
- N-gram frequency analysis (2/3/4-grams)
- Readability scoring (Flesch-Kincaid, Gunning Fog, Flesch Reading Ease)
- Information density profiling with coefficient of variation
- Transition pattern mapping and sentence opening classification

### Key changes from v3.0

| Area | v3.0 | v4.0 (Nature-calibrated) |
|---|---|---|
| **Patterns** | 35 | **39** (+transition overuse, passive voice absence, readability mismatch, colon overuse) |
| **Sentence length CV** | >0.40 | **0.45-0.65** (Scientific), >0.40 (General) |
| **Mean sentence length** | Not specified | **20-28 words** (Scientific), 15-22 (General) |
| **AI vocabulary** | Zero tolerance all tiers | **Context-aware**: Tier 1A (always flag), Tier 1B (Nature frequency baselines), Tier 2 (cluster detection) |
| **Em dash policy** | Zero all modes | **Mode-dependent**: zero (General/Grant), <=2/1000w (Scientific) |
| **Copula ratio** | <15% | **<5%** (Scientific), <10% (General) |
| **Passive voice** | Not tracked | **10-25%** target (Nature: 17.1% — zero passive is itself an AI tell) |
| **Transition word openers** | Not tracked | **<8%** of sentences (Nature: 4.0%) |
| **Contrast:Additive ratio** | Not tracked | **>1.5:1** (Nature: ~2:1) |
| **Info density CV** | Not tracked | **>0.45** (Nature: 0.555) |
| **Colon overuse** | Not tracked | **<=0.05/sentence** rhetorical colons; banned label-colon patterns |
| **Readability (FK grade)** | Not tracked | **14-18** (Scientific; Nature: 16.1) |

### New patterns in v4.0

| # | Pattern | Key finding |
|---|---|---|
| 36 | **Transition word overuse** | Only 4% of Nature sentences open with transition words. AI hits 10-20%. Contrast transitions should outnumber additive ones 2:1. |
| 37 | **Passive voice absence** | Nature uses 17.1% passive voice. Eliminating all passive is itself an AI tell. Methods and established procedures naturally use passive. |
| 38 | **Readability mismatch** | Nature's Flesch-Kincaid grade is 16.1. If humanized scientific text drops below grade 14, it has been oversimplified. |
| 39 | **Colon overuse** | AI uses rhetorical colons 4-5x more than Nature. Zero Nature papers used "Key finding:", "Notably:", "Importantly:" before a colon. Banned. |

### Nature-calibrated vocabulary baselines

Words that previous versions flagged unconditionally are now context-aware in Scientific mode:

| Word | Nature frequency (/10K words) | New policy |
|---|---|---|
| key (adj.) | 7.04 | Legitimate. Flag only in clusters of 3+. |
| furthermore | 3.06 | Legitimate. Flag only if >5/10K or clustered. |
| additionally | 2.76 | Legitimate. Flag only if >4/10K or clustered. |
| moreover | 2.76 | Same as additionally. |
| robust | 1.99 | Legitimate technical descriptor. Flag when filler. |
| comprehensive | 1.68 | Legitimate when describing actual scope. |
| crucial | 1.53 | Flag when >2/10K or vague importance. |
| multifaceted | 0.15 | Very rare even in Nature. Almost always AI. |

**Cluster rule:** If any paragraph contains 3+ words from Tier 1B + Tier 2, flag the entire paragraph regardless of individual frequencies.

## Installation

### Recommended (clone directly into Claude Code skills directory)

```bash
mkdir -p ~/.claude/skills
git clone https://github.com/Harsh9005/humanizer.git ~/.claude/skills/humanizer-4.0.0
```

### Manual install/update (only the skill file)

```bash
mkdir -p ~/.claude/skills/humanizer
cp SKILL.md ~/.claude/skills/humanizer/
```

## Usage

In Claude Code, invoke the skill:

```
/humanizer

[paste your text here]
```

Or ask Claude to humanize text directly:

```
Please humanize this text: [your text]
```

## Overview

Based on:
- [Wikipedia's "Signs of AI writing"](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing) guide (WikiProject AI Cleanup, ~15,000 words)
- [PubMed excess vocabulary study](https://www.science.org/doi/10.1126/sciadv.adt3813) (Science Advances, 2024)
- [SAGE peer reviewer guidance](https://www.sagepub.com/explore-our-content/blogs/posts/sage-perspectives/2025/06/11/ai-detection-for-peer-reviewers-look-out-for-red-flags) (2025)
- [NIH NOT-OD-25-132](https://gptzero.me/news/nih-vs-ai-how-new-rules-are-redefining-grant-writing/) (July 2025)
- **Empirical NLP/ML analysis of 19 Nature papers** (v4.0, 2026)

### Key insight

> "LLMs use statistical algorithms to guess what should come next. The result tends toward the most statistically likely result that applies to the widest variety of cases." — Wikipedia

> "Real Nature papers use many words that AI detectors flag (key, robust, furthermore, comprehensive), but at specific frequencies and in specific patterns. The difference between AI and human usage is not presence but density, clustering, and context." — v4.0 corpus analysis

## Modes

| Mode | Triggers | Extra rules |
|---|---|---|
| Scientific | Research papers, manuscripts, abstracts, methods | Nature-calibrated vocabulary, sentence length 20-28w, passive voice 10-25%, FK grade 14-18 |
| Grant | Proposals, specific aims, significance sections | Generic importance claims, textbook methodology, alignment checks |
| General | Blog posts, essays, reports, emails | Standard patterns with stricter thresholds |

## All 39 patterns

### Content patterns (#1-6)

| # | Pattern | Example fix |
|---|---------|-------------|
| 1 | Significance inflation | "marking a pivotal moment" → specific facts |
| 2 | Notability name-dropping | Citation dumps → one specific, contextualized reference |
| 3 | Superficial -ing analyses | "symbolizing... reflecting..." → remove or source |
| 4 | Promotional language | "nestled within the breathtaking" → neutral description |
| 5 | Vague attributions | "Experts believe" → specific source with date |
| 6 | Formulaic challenges | "Despite challenges... continues to thrive" → specific facts |

### Language patterns (#7-12)

| # | Pattern | Example fix |
|---|---------|-------------|
| 7 | AI vocabulary (context-aware) [N] | 3 tiers with Nature frequency baselines + cluster detection |
| 8 | Copula avoidance | "serves as... features... boasts" → "is... has" |
| 9 | Negative parallelisms | "It's not just X, it's Y" → state directly |
| 10 | Rule of three (all levels) | Triplet adjectives, benefits, examples → natural count |
| 11 | Synonym cycling | "protagonist... main character... hero" → consistent term |
| 12 | False ranges | "from X to Y, from A to B" → list directly |

### Style patterns (#13-18)

| # | Pattern | Example fix |
|---|---------|-------------|
| 13 | Em dash overuse (mode-dependent) [N] | Zero (General/Grant), <=2/1000w (Scientific) |
| 14 | Boldface overuse | Remove mechanical emphasis |
| 15 | Inline-header lists | Convert to prose |
| 16 | Title case headings | Use sentence case |
| 17 | Emojis | Remove entirely |
| 18 | Curly quotes | Replace with straight quotes |

### Communication and filler (#19-24)

| # | Pattern | Example fix |
|---|---------|-------------|
| 19 | Chatbot artifacts | Remove "I hope this helps" etc. |
| 20 | Cutoff disclaimers | Remove "While details are limited..." |
| 21 | Sycophantic tone | Remove "Great question!" etc. |
| 22 | Filler phrases | "In order to" → "To" |
| 23 | Excessive hedging | "could potentially possibly" → "may" |
| 24 | Generic conclusions | "The future looks bright" → specific plans |

### Structural patterns (#25-35)

| # | Pattern | Example fix |
|---|---------|-------------|
| 25 | Sentence length uniformity [N] | CV 0.45-0.65, mean 20-28w, 21-35w bucket largest |
| 26 | Over-explanation / self-paraphrasing | Remove restated points within paragraphs |
| 27 | Dependent clause chaining | Longer independent clauses, fewer subordinations |
| 28 | Scientific excess vocabulary | PubMed-specific: "elucidated", "facilitated", "underpinned" |
| 29 | Generic importance claims | "critical gap" → specific problem with quantified impact |
| 30 | Textbook methodology | Add reagent concentrations, equipment models, specific parameters |
| 31 | En dash misuse | Hyphens in ranges → proper en dashes |
| 32 | "It's not X, it's Y" contrasts | Dramatic reframing → direct statement |
| 33 | Parallel paragraph structure | Uniform templates → varied paragraph lengths and openings |
| 34 | Copula ratio [N] | <5% substitutes (Scientific), <10% (General) |
| 35 | Information density uniformity [N] | CV >0.45, vary between data-dense and interpretive paragraphs |

### New in v4.0 (#36-39) [N]

| # | Pattern | Example fix |
|---|---------|-------------|
| 36 | Transition word overuse [N] | <8% sentence openers; contrast:additive >1.5:1 |
| 37 | Passive voice absence [N] | 10-25% passive is natural; 0% passive is suspicious |
| 38 | Readability mismatch [N] | FK grade 14-18 (Scientific); don't oversimplify |
| 39 | Colon overuse [N] | <=0.05/sentence; zero "Key finding:" / "Notably:" patterns |

## Quantitative self-check

After humanization, the skill reports Nature-calibrated metrics:

| Metric | Target (Scientific) | Target (General) |
|---|---|---|
| Sentence length CV [N] | 0.45-0.65 | >0.40 |
| Mean sentence length [N] | 20-28 words | 15-22 words |
| Tier 1A AI words | 0 | 0 |
| AI word clusters (3+/para) | 0 | 0 |
| Em dashes [N] | <=2/1000w | 0 |
| Copula substitute ratio [N] | <5% | <10% |
| Passive voice % [N] | 10-25% | Variable |
| Transition word openers [N] | <8% | <10% |
| Contrast:Additive ratio [N] | >1.5:1 | >1:1 |
| Rhetorical colons/sentence [N] | <=0.05 | <=0.04 |
| Info density CV [N] | >0.45 | >0.35 |

## Analysis data

The `scripts/` directory contains the reusable analysis pipeline:

- `extract_and_analyze.py` — Full NLP/ML pipeline (PDF extraction, sentence analysis, TF-IDF, K-means, POS tagging, readability scoring)
- `nature_writing_analysis.json` — Aggregate results across all 19 papers
- `per_paper_analysis.json` — Per-paper breakdown for validation

## References

1. [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)
2. [PubMed excess vocabulary study](https://www.science.org/doi/10.1126/sciadv.adt3813) (Science Advances, 2024)
3. [SAGE peer reviewer guidance](https://www.sagepub.com/explore-our-content/blogs/posts/sage-perspectives/2025/06/11/ai-detection-for-peer-reviewers-look-out-for-red-flags) (2025)
4. [Nature formatting guide](https://www.nature.com/nature/for-authors/formatting-guide)
5. [NIH NOT-OD-25-132](https://gptzero.me/news/nih-vs-ai-how-new-rules-are-redefining-grant-writing/) (July 2025)
6. [Frontiers: Lexical diversity study](https://www.frontiersin.org/journals/education/articles/10.3389/feduc.2025.1616935/full)
7. [Pangram: AI writing patterns guide](https://www.pangram.com/blog/comprehensive-guide-to-spotting-ai-writing-patterns)
8. [MIT Press: LLM Text Detection Survey](https://direct.mit.edu/coli/article/51/1/275/127462/A-Survey-on-LLM-Generated-Text-Detection-Necessity)
9. Empirical NLP/ML corpus analysis of 19 Nature journal papers (v4.0, 2026)

## Version history

- **4.0.0** - Major data-driven upgrade: NLP/ML analysis of 19 Nature papers (3,322 sentences, 65K words). 4 new patterns (#36-39), Nature-calibrated benchmarks for sentence structure, vocabulary, transitions, voice, readability, punctuation. Context-aware AI vocabulary with frequency baselines. TF-IDF, K-means, POS tagging, n-gram analysis.
- **3.0.0** - Scientific/Grant writing modes, 11 new structural patterns (#25-35), PubMed excess vocabulary (3-tier system), quantitative self-check, Nature style compliance
- **2.2.0** - Added a final "obviously AI generated" audit + second-pass rewrite prompts
- **2.1.1** - Fixed pattern #18 example (curly quotes vs straight quotes)
- **2.1.0** - Added before/after examples for all 24 patterns
- **2.0.0** - Complete rewrite based on raw Wikipedia article content
- **1.0.0** - Initial release

## License

MIT
