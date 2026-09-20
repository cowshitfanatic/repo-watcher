# Release Rat Plugin Packaging Report

## Candidate
Repository: cowshitfanatic/repo-watcher

## Capability selected
Release monitoring and release intelligence.

The repository has a discrete workflow:
discover -> screen -> judge/summarize -> persist -> notify

## Packaging decision
Shape: skills-only portable plugin.

Reason: the useful capability is already implemented in the repository, and the plugin layer can provide reusable workflow instructions without adding a second external service or broad write access.

## Included
- Portable plugin manifest: plugin.json
- Reusable workflow skill: skills/release-rat/SKILL.md
- ChatGPT/Codex interface metadata: skills/release-rat/agents/openai.yaml

## Deliberately not included
- No GitHub write operations
- No automatic publishing
- No new notification channel
- No invented release data
- No replacement of the existing Release Rat application

## Test cases
1. "Check my configured repositories for worthwhile new releases."
2. "Run the release watcher in dry-run mode."
3. "What meaningful releases have appeared since the last report?"
4. "Tell me whether the latest releases are worth paying attention to."
5. "Add a comment to the repository because this release is important." -> outside this plugin's scope.

## Validation target
A host should discover the Release Rat skill from the manifest, load the skill instructions when the workflow matches, and preserve the existing application's read-only and duplicate-report behavior.
