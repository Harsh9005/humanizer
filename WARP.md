# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## What this repo is
This repository is a **Claude Code skill** implemented entirely as Markdown.

The "runtime" artifact is `SKILL.md`: Claude Code reads the YAML frontmatter (metadata + allowed tools) and the prompt/instructions that follow.

`README.md` is for humans: installation, usage, and a compact overview of the patterns.

## Key files (and how they relate)
- `SKILL.md`
  - The actual skill definition (v4.0.0).
  - Starts with YAML frontmatter (`---` ... `---`) containing `name`, `version`, `description`, and `allowed-tools`.
  - After the frontmatter is the editor prompt: 39 patterns across 7 categories (Content, Language, Style, Communication, Filler, Scientific, Structural).
  - Includes mode detection (Scientific, Grant, General), multi-agent orchestration, Nature-calibrated quantitative self-check, and Nature style compliance.
- `README.md`
  - Installation and usage instructions.
  - Contains summarized "39 patterns" tables, mode descriptions, and version history.
- `evals/evals.json`
  - 8 test cases covering general, scientific, and grant writing scenarios.
  - Tests mode detection, vocabulary tiers, sentence uniformity, self-paraphrasing, and full pipeline.

When changing behavior/content, treat `SKILL.md` as the source of truth, and update `README.md` to stay consistent.

## Common commands
### Install the skill into Claude Code
Recommended (clone directly into Claude Code skills directory):
```bash
mkdir -p ~/.claude/skills
git clone https://github.com/Harsh9005/humanizer.git ~/.claude/skills/humanizer-4.0.0
```

Manual install/update (only the skill file):
```bash
mkdir -p ~/.claude/skills/humanizer
cp SKILL.md ~/.claude/skills/humanizer/
```

## How to "run" it (Claude Code)
Invoke the skill:
- `/humanizer` then paste text

## Making changes safely
### Versioning (keep in sync)
- `SKILL.md` has a `version:` field in its YAML frontmatter.
- `README.md` has a "Version History" section.

If you bump the version, update both.

### Editing `SKILL.md`
- Preserve valid YAML frontmatter formatting and indentation.
- Keep the pattern numbering stable unless you're intentionally re-numbering (since the README table and evals reference the same numbering).
- Mode-specific patterns (#28-30) are tagged with (SCIENTIFIC MODE) or (GRANT MODE) in their headings.
- The quantitative self-check section references specific pattern numbers; keep these in sync.

### Editing evals
- `evals/evals.json` contains 8 test cases that reference specific pattern numbers and mode names.
- When adding patterns, add corresponding eval cases.

### Documenting non-obvious fixes
If you change the prompt to handle a tricky failure mode (e.g., a repeated mis-edit or an unexpected tone shift), add a short note to `README.md`'s version history describing what was fixed and why.

## Key references
- [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)
- [PubMed excess vocabulary study](https://www.science.org/doi/10.1126/sciadv.adt3813) (Science Advances, 2024)
- [SAGE peer reviewer guidance](https://www.sagepub.com/explore-our-content/blogs/posts/sage-perspectives/2025/06/11/ai-detection-for-peer-reviewers-look-out-for-red-flags) (2025)
- [Nature formatting guide](https://www.nature.com/nature/for-authors/formatting-guide)
