# Release Rat

Release Rat watches a configured list of GitHub repositories, checks for new releases, filters out routine releases, summarizes worthwhile ones in plain English, remembers what it has already reported, and notifies Discord when a webhook is configured.

It deliberately uses a tiered workflow:

1. GitHub release metadata is fetched deterministically.
2. A cheap significance screen catches obvious routine releases.
3. If an OpenAI API key is configured, only borderline/interesting releases are sent to the model for a structured significance decision and plain-English summary.
4. Reported release IDs are persisted locally so the same release is not reported twice.
5. Discord is optional; without it, reports are appended to `data/reports.log`.

No GitHub write permissions are needed.

## Quick start

Requires Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp config.example.yaml config.yaml
python -m release_rat --once
```

Edit `config.yaml` and put repositories under `repositories`, for example:

```yaml
repositories:
  - openai/openai-python
  - langchain-ai/langgraph

interval_minutes: 60
max_releases_per_repo: 5

significance:
  minimum_score: 3
  always_signals:
    - security
    - breaking
    - deprecation
    - major
    - migration

notifications:
  discord_webhook: ""

llm:
  enabled: true
  model: gpt-5-mini
```

Set `OPENAI_API_KEY` only if you want model-assisted judgment and summaries. If it is absent, Release Rat still works using deterministic significance rules and a local plain-text summary.

Run continuously:

```bash
python -m release_rat
```

Run once:

```bash
python -m release_rat --once
```

Dry run without recording or notifying:

```bash
python -m release_rat --once --dry-run
```

## GitHub Actions

The included workflow runs every hour and is the easiest way to make the rat periodic without keeping a machine running.

Add repository secrets:

- `OPENAI_API_KEY` (optional)
- `DISCORD_WEBHOOK_URL` (optional)

Edit `config.yaml` to add repositories. The workflow commits `data/state.json` back to the repository so release memory survives between runs.

## Architecture

This is intentionally not a giant autonomous framework. Release detection is deterministic and cheap; the model is only used where judgment actually helps. State is a small JSON document. Notifications are a narrow adapter.

The main workflow is:

`discover -> screen -> judge/summarize -> persist -> notify`

Failures are isolated per repository/release. A transient failure in one repository does not prevent the others from being checked.

## Safety / failure behavior

Release Rat only reads public GitHub release data. It never publishes, comments, opens issues, or changes repositories.

It treats release IDs as the stable memory key, not titles or tags. Draft and prerelease releases are ignored by default. Deleted or missing releases are never fabricated.

Discord failures are logged and do not erase state. State is written atomically to reduce corruption risk.

## Tests

```bash
python -m unittest discover -s tests -v
```
