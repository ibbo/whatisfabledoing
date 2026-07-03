# whatisfabledoing

Public field-report project for `whatisfabledoing.com`.

## Purpose

Track substantive public reports from people actually using Anthropic Claude Fable / Claude Fable 5, with enough detail to show what serious users are achieving and how credible each report is.

## Data

- `data/fable-field-reports.md` - the report log, published verbatim on the site.
- `data/fable-field-reports.json` - lightweight seen-state for the collector.

Report format (one section per UTC day, entries written for the site's readers in a natural editorial voice — no analyst labels like "evidence quality" or "takeaway"):

```markdown
## YYYY-MM-DD

### [Short specific headline](https://source-url) — Author name/handle
One paragraph (2–5 sentences) describing what the person did with Fable and
what came of it. Credibility is conveyed through concrete facts (numbers,
reproduced bugs, merged PRs, quotes), not ratings.
```

The collector is the Hermes cron job `Claude Fable field reports` on the Mac mini (`hermes cron list`). It replaced the old OpenClaw job `0eea3d42-8913-4548-afc5-039b15f34934`, which is paused. After updating the data files the job must `git commit` and `git push` — GitHub Pages serves this repo, so the site only updates on push.

## Website

`index.html` at the repo root is the whole site — a static page that fetches and parses `data/fable-field-reports.md` (and reads `last_run` from the JSON) in the browser, so there is no build step. Served by GitHub Pages at `whatisfabledoing.com`. Preview locally with `python3 -m http.server` from the repo root.

## Votes

Each report card has an upvote button backed by a tiny API at `api.whatisfabledoing.com` (A record → VPS at 51.89.164.138, nginx → `fable-votes.service` → `server/votes_server.py` on 127.0.0.1:8127, SQLite at `/opt/fable-votes/votes.db`). One vote per report per voter key (sha256 of salt + IP + user agent), per-IP rate limiting, CORS locked to this site, and report ids are validated against the live report log. The frontend hides the vote UI if the API is unreachable. Deployment copies of the service/nginx configs live in `server/`; deploy by scp-ing `votes_server.py` to `/opt/fable-votes/` on the VPS (`ssh vps` from the Mac mini) and `sudo systemctl restart fable-votes`.

## Editorial Filter

Include high-signal, public, quotable sources with concrete usage, methodology, artifacts, or reasoned evaluation. Negative findings are welcome when they are evidence-based (e.g. benchmarked refusals), not access/rollout complaints.

Skip quota/rate-limit complaints, rollout drama, shallow hype, memes, duplicate amplification, and guardrail complaints unless they are part of a broader evidence-based capability evaluation.
