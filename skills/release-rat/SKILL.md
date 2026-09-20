---
name: release-rat
description: Monitor configured GitHub repositories for new releases, identify releases that are worth attention, summarize why they matter in plain English, and avoid duplicate reporting. Use this skill when the user asks to run Release Rat, check watched repositories for meaningful releases, review recent release activity, or prepare a release report.
---

# Release Rat

Use this skill to operate the repository's Release Rat workflow rather than inventing release information.

## Workflow

1. Treat GitHub release metadata as the source of truth. Release identity is the numeric GitHub release ID.
2. Load the user's configured repositories from `config.yaml`. Do not silently invent repositories when the configuration is missing or invalid.
3. Run one polling cycle for an explicit check:
   `python -m release_rat --once`
4. For a preview that must not change state or send notifications, use:
   `python -m release_rat --once --dry-run`
5. Let the deterministic significance rules screen releases first. Use model-assisted judgment only when the project's LLM configuration enables it.
6. Report the repository, tag, significance decision, and plain-English summary returned by Release Rat.
7. Preserve the project's duplicate-report protection. Do not manually re-report a release that the state store says has already been reported unless the user explicitly asks for a fresh review.
8. Treat Discord as optional. A missing webhook is not a failure of release detection.
9. Never fabricate a release, tag, changelog entry, security issue, migration requirement, or other detail that is not present in GitHub release data or the model's structured assessment.
10. Release Rat is read-only with respect to GitHub repositories. Do not add comments, issues, labels, releases, or other GitHub writes as part of this workflow.

## Output

Prefer a compact report with:

- Repository and release tag
- Whether the release was considered worthwhile
- Why it matters, in plain English
- Release URL when available

When nothing worthwhile is found, say so plainly and distinguish that result from a failed GitHub request.

## Failure handling

A failure affecting one repository or release should not be represented as a successful report. Preserve the distinction between:

- no noteworthy releases found
- repository/release lookup failed
- model-assisted assessment unavailable
- notification delivery failed

When the LLM is unavailable, use the deterministic/local behavior provided by the application rather than inventing a model judgment.

## Scope

This skill packages the existing Release Rat application. It does not replace or modify the application's configuration, state, GitHub client, significance rules, notification adapter, or scheduling mechanism.
