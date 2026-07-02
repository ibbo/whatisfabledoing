# whatisfabledoing

Public field-report project for `whatisfabledoing.com`.

## Purpose

Track substantive public reports from people actually using Anthropic Claude Fable / Claude Fable 5, with enough detail to show what serious users are achieving and how credible each report is.

## Data

- `data/fable-field-reports.md` - curated chronological report log.
- `data/fable-field-reports.json` - lightweight seen-state for the collector.

The active OpenClaw cron job is `Claude Fable field reports` (`0eea3d42-8913-4548-afc5-039b15f34934`). It should read/write the exact files above, not the old `~/clawd/memory/fable-field-reports.*` paths.

## Website

`index.html` at the repo root is the whole site — a static page that fetches and parses `data/fable-field-reports.md` (and reads `last_run` from the JSON) in the browser, so there is no build step: the cron job updating the data files updates the site. Deploy by serving the repo root on any static host (the domain is `whatisfabledoing.com`). Preview locally with `python3 -m http.server` from the repo root.

The parser expects the existing entry format (`- Source: <url> — <author>. Task/domain: … Achieved: … Evaluation: … Evidence quality: … Takeaway: …` under `## YYYY-MM-DD` headings); entries that don't match still render as raw text.

## Editorial Filter

Include high-signal, public, quotable sources with concrete usage, methodology, artifacts, or reasoned evaluation.

Skip quota/rate-limit complaints, rollout drama, shallow hype, memes, duplicate amplification, and guardrail complaints unless they are part of a broader evidence-based capability evaluation.
