from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping, Sequence

PASS = "PASS"
NON_PASS = {"FAIL", "UNKNOWN", "BLOCKED", "SKIPPED", "WAIVED", "STALE"}


def canonical_json(value: Any) -> bytes:
    """RFC-8785-inspired stable JSON subset used for evidence digests."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


@dataclass(frozen=True)
class Finding:
    code: str
    message: str


def _parse_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamp must include timezone")
    return parsed.astimezone(timezone.utc)


def evaluate_release(
    policy: Mapping[str, Any],
    evidence: Mapping[str, Any],
    *,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Fail closed. Release only when every mandatory predicate is proven."""
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    findings: list[Finding] = []
    categories = tuple(policy["categories"])
    results = evidence.get("categories", {})

    unknown_categories = sorted(set(results) - set(categories))
    if unknown_categories:
        findings.append(Finding("UNDECLARED_CATEGORY", ",".join(unknown_categories)))

    passed = 0
    category_report: dict[str, Any] = {}
    for name in categories:
        item = results.get(name)
        if not isinstance(item, Mapping):
            category_report[name] = {"status": "UNKNOWN", "score": 0}
            findings.append(Finding("MISSING_EVIDENCE", name))
            continue
        status = str(item.get("status", "UNKNOWN")).upper()
        score = int(item.get("score", 0))
        digest = item.get("evidence_sha256", "")
        if status != PASS:
            findings.append(Finding("NON_PASS_STATUS", f"{name}:{status}"))
        if score != 100:
            findings.append(Finding("SCORE_BELOW_100", f"{name}:{score}"))
        if not isinstance(digest, str) or len(digest) != 64:
            findings.append(Finding("INVALID_EVIDENCE_DIGEST", name))
        try:
            observed_at = _parse_time(str(item["observed_at"]))
            max_age = int(item.get("max_age_seconds", 86400))
            if policy.get("reject_stale_evidence", True) and (now - observed_at).total_seconds() > max_age:
                findings.append(Finding("STALE_EVIDENCE", name))
        except (KeyError, TypeError, ValueError):
            findings.append(Finding("INVALID_EVIDENCE_TIME", name))
        if status == PASS and score == 100 and isinstance(digest, str) and len(digest) == 64:
            passed += 1
        category_report[name] = {"status": status, "score": score, "evidence_sha256": digest}

    executor = evidence.get("executor_agent_id")
    validator = evidence.get("validator_agent_id")
    if policy.get("reject_self_certification", True) and (not executor or not validator or executor == validator):
        findings.append(Finding("VALIDATOR_NOT_INDEPENDENT", "executor and validator must differ"))

    source_sha = evidence.get("source_sha", "")
    if not isinstance(source_sha, str) or len(source_sha) != 40:
        findings.append(Finding("INVALID_SOURCE_SHA", "source_sha must be immutable 40-character Git SHA"))

    cycles: Sequence[Mapping[str, Any]] = evidence.get("clean_cycles", [])
    required_cycles = int(policy.get("minimum_clean_cycles", 3))
    fresh_cycles = [c for c in cycles if c.get("status") == PASS and c.get("source_sha") == source_sha and not c.get("replayed", False)]
    if len(fresh_cycles) < required_cycles:
        findings.append(Finding("INSUFFICIENT_CLEAN_CYCLES", f"{len(fresh_cycles)}/{required_cycles}"))

    p0 = int(evidence.get("open_p0", 0))
    p1 = int(evidence.get("open_p1", 0))
    if p0 or p1:
        findings.append(Finding("OPEN_CRITICAL_DEFECTS", f"P0={p0},P1={p1}"))

    category_score = 0 if not categories else round((passed / len(categories)) * 100)
    release_allowed = not findings and category_score == int(policy.get("release_on_score", 100))
    report = {
        "policy_version": policy["version"],
        "source_sha": source_sha,
        "score": category_score,
        "status": PASS if release_allowed else "FAIL",
        "release_allowed": release_allowed,
        "production_locked": not release_allowed,
        "categories": category_report,
        "clean_cycles": {"required": required_cycles, "accepted": len(fresh_cycles)},
        "findings": [finding.__dict__ for finding in findings],
    }
    report["report_sha256"] = canonical_sha256(report)
    return report
