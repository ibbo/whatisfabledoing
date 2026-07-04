# Backlog

Ideas noted for later — not commitments.

## Time-decayed vote score for "Most upvoted"

**Problem it would solve:** with a growing report count, the "Most upvoted"
view will tend to be dominated by old reports that have simply had more time
to collect votes, making the ranking feel stale.

**Trigger to act:** revisit when the top of the "Most upvoted" list stops
changing even though newer reports are getting votes.

**Sketch:** rank by `votes / (age_in_days + 2)^g` (Hacker News-style gravity,
g ≈ 1.2–1.8) instead of raw count. Age can come from the report's date
section in `data/fable-field-reports.md` or `seen_at` in the JSON seen-state,
so it's computable client-side in `index.html` with no API changes — the API
keeps returning raw counts either way. Could be a third sort option
("Trending") rather than replacing "Most upvoted".
