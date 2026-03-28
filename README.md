## SaaS Signal

`applyr` currently contains one agent: `researcher`, a single-pass SaaS opportunity research pipeline.

Phase 1 workflow:

- collect Reddit pain signals and 3-star review signals
- normalize them into a common record shape
- score each opportunity across five dimensions
- print a ranked terminal report or JSON payload

CLI:

```bash
applyr run --fixture researcher/data/fixtures/saas_signals.json
applyr eval --fixture researcher/data/fixtures/saas_signals.json
applyr graph --fixture researcher/data/fixtures/saas_signals.json
```

Environment:

- `ANTHROPIC_API_KEY` for future live scoring
- `CACHE_DIR` to override local cache storage
- `REDDIT_USER_AGENT` for Reddit collector requests
