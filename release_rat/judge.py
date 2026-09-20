import json
import os
import re
import urllib.error
import urllib.request
from .models import Assessment, Release

def _text(release: Release) -> str:
    return f"{release.name}\n{release.tag_name}\n{release.body}".lower()

def heuristic_assessment(release: Release, cfg: dict) -> Assessment:
    text = _text(release)
    sig = cfg["significance"]
    high = [k.lower() for k in sig["keywords"]["high"]]
    medium = [k.lower() for k in sig["keywords"]["medium"]]
    score = 0
    reasons = []
    for word in high:
        if word in text:
            score += 3
            reasons.append(word)
    for word in medium:
        if word in text:
            score += 1
            reasons.append(word)
    if re.match(r"^v?\d+\.0+\.0(?:$|[-+])", release.tag_name):
        score += 3
        reasons.append("major-version pattern")
    minimum = int(sig["minimum_score"])
    significant = score >= minimum
    reason = ", ".join(dict.fromkeys(reasons)) or "no significance signals found"
    summary = local_summary(release)
    return Assessment(significant, score, reason, summary)

def local_summary(release: Release) -> str:
    body = " ".join(line.strip() for line in release.body.splitlines() if line.strip())
    body = re.sub(r"\s+", " ", body).strip()
    if not body:
        return f"{release.name} ({release.tag_name}) was released, but the project did not provide release notes."
    if len(body) > 420:
        body = body[:417].rsplit(" ", 1)[0] + "..."
    return body

def llm_assessment(release: Release, cfg: dict, fallback: Assessment) -> Assessment:
    if not cfg["llm"].get("enabled", True) or not os.getenv("OPENAI_API_KEY"):
        return fallback

    prompt = f"""You are Release Rat, a software release triage assistant.
Decide whether this GitHub release is significant enough to notify a developer.
Significant means it materially changes behavior, APIs, security, compatibility,
performance, supported platforms, migrations, or important capabilities.
Ignore routine dependency bumps, typo fixes, tiny docs changes, and housekeeping.

Return JSON only with:
significant (boolean), score (integer 0-5), reason (string), summary (string).
The summary must be plain English, <= 500 characters, and must not invent facts.

Repository: {release.repository}
Release: {release.name}
Tag: {release.tag_name}
Published: {release.published_at}
Release notes:
{release.body[:12000]}
"""
    payload = {
        "model": cfg["llm"]["model"],
        "input": prompt,
        "text": {"format": {"type": "json_object"}},
    }
    req = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
            "Content-Type": "application/json",
            "User-Agent": "release-rat/0.1",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=int(cfg["llm"]["timeout_seconds"])) as response:
            data = json.loads(response.read().decode("utf-8"))
        text = data.get("output_text", "")
        if not text:
            for item in data.get("output", []):
                for content in item.get("content", []):
                    if content.get("type") in {"output_text", "text"}:
                        text += content.get("text", "")
        parsed = json.loads(text)
        return Assessment(
            significant=bool(parsed["significant"]),
            score=max(0, min(5, int(parsed["score"]))),
            reason=str(parsed["reason"])[:500],
            summary=str(parsed["summary"])[:500],
        )
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        return Assessment(
            significant=fallback.significant,
            score=fallback.score,
            reason=f"{fallback.reason}; LLM unavailable ({type(exc).__name__})",
            summary=fallback.summary,
        )
