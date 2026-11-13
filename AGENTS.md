# Codex Instructions

## Purpose
Build a reliable, low-cost AI-agent workflow for operating a China-mainland social-media account.

## Rules
- Keep modules small, testable, and typed where practical.
- Isolate platform code under `app/collectors/` and `app/publishers/`.
- Use official APIs and authorized integrations only. Never bypass CAPTCHA, login controls, or platform restrictions.
- Publishing must be blocked unless an explicit approval state is recorded.
- Keep API keys in environment variables; never commit `.env` or log secrets.
- Record provenance for topics and generated content: source URL, capture time, model/prompt version, fact-check status.
- Do not invent trend metrics. Represent missing data as missing.
- Add tests for scoring, approval gates, retries, and idempotency.
- Set model-call budgets and rate limits.
- Ask before adding paid services, connecting real accounts, or enabling irreversible publishing actions.

## Development loop
1. Inspect existing code and tests.
2. State the planned change briefly.
3. Implement the smallest complete increment.
4. Add/update tests and docs.
5. Run tests and report exact results; never claim unrun tests passed.

## MVP order
1. Data models and migrations.
2. One lawful, traceable trend source.
3. Configurable topic scoring.
4. LLM adapter and draft generation.
5. Human review queue.
6. One platform adapter after permission verification.
7. Metrics ingestion and feedback loop.
