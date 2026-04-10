#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SEVERITY_ORDER = {
    "low": 1,
    "medium": 2,
    "high": 3,
    "critical": 4,
}

HIGH_SECURITY_RULES = {
    "security/detect-child-process",
    "security/detect-disable-mustache-escape",
    "security/detect-eval-with-expression",
    "security/detect-new-buffer",
    "security/detect-non-literal-fs-filename",
    "security/detect-non-literal-require",
    "security/detect-pseudoRandomBytes",
    "security/detect-unsafe-regex",
    "no-secrets/no-secrets",
}


@dataclass
class Finding:
    tool: str
    severity: str
    path: str
    rule: str
    message: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fail the pipeline when SAST results contain high or critical issues."
    )
    parser.add_argument("--bandit", required=True, type=Path)
    parser.add_argument("--eslint", required=True, type=Path)
    parser.add_argument("--semgrep", required=True, type=Path)
    return parser.parse_args()


def load_json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"Missing report: {path}")
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def normalize_severity(value: Any) -> str:
    if value is None:
        return "medium"

    if isinstance(value, (int, float)):
        if value >= 9:
            return "critical"
        if value >= 7:
            return "high"
        if value >= 4:
            return "medium"
        return "low"

    text = str(value).strip().lower()
    aliases = {
        "error": "high",
        "warning": "medium",
        "warn": "medium",
        "info": "low",
    }
    if text in aliases:
        return aliases[text]
    if text in SEVERITY_ORDER:
        return text

    try:
        return normalize_severity(float(text))
    except ValueError:
        return "medium"


def bandit_findings(payload: dict[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    for result in payload.get("results", []):
        findings.append(
            Finding(
                tool="bandit",
                severity=normalize_severity(result.get("issue_severity")),
                path=result.get("filename", ""),
                rule=result.get("test_id", "bandit"),
                message=result.get("issue_text", ""),
            )
        )
    return findings


def eslint_findings(payload: list[dict[str, Any]]) -> list[Finding]:
    findings: list[Finding] = []
    for file_result in payload:
        path = file_result.get("filePath", "")
        for message in file_result.get("messages", []):
            rule_id = message.get("ruleId") or "eslint"
            if not (
                rule_id.startswith("security/") or rule_id.startswith("no-secrets/")
            ):
                continue

            severity = "high" if rule_id in HIGH_SECURITY_RULES else "medium"
            if message.get("severity") == 1:
                severity = "low"

            findings.append(
                Finding(
                    tool="eslint",
                    severity=severity,
                    path=path,
                    rule=rule_id,
                    message=message.get("message", ""),
                )
            )
        for suppressed in file_result.get("suppressedMessages", []):
            rule_id = suppressed.get("ruleId") or "eslint"
            if not (
                rule_id.startswith("security/") or rule_id.startswith("no-secrets/")
            ):
                continue
            findings.append(
                Finding(
                    tool="eslint",
                    severity="low",
                    path=path,
                    rule=rule_id,
                    message=f"Suppressed: {suppressed.get('message', '')}",
                )
            )
    return findings


def semgrep_findings(payload: dict[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    for result in payload.get("results", []):
        extra = result.get("extra", {})
        metadata = extra.get("metadata", {})
        severity = normalize_severity(
            metadata.get("security-severity")
            or metadata.get("severity")
            or extra.get("severity")
        )
        findings.append(
            Finding(
                tool="semgrep",
                severity=severity,
                path=result.get("path", ""),
                rule=result.get("check_id", "semgrep"),
                message=extra.get("message", ""),
            )
        )
    return findings


def summarize(findings: list[Finding]) -> dict[str, int]:
    counts = {key: 0 for key in SEVERITY_ORDER}
    for finding in findings:
        counts[finding.severity] += 1
    return counts


def main() -> int:
    args = parse_args()

    findings = [
        *bandit_findings(load_json(args.bandit)),
        *eslint_findings(load_json(args.eslint)),
        *semgrep_findings(load_json(args.semgrep)),
    ]

    counts = summarize(findings)
    blocked = [
        finding
        for finding in findings
        if SEVERITY_ORDER[finding.severity] >= SEVERITY_ORDER["high"]
    ]

    print("Security scan summary:")
    for severity in ("critical", "high", "medium", "low"):
        print(f"  {severity}: {counts[severity]}")

    if not blocked:
        print("Security gate passed: no high or critical findings detected.")
        return 0

    print("Security gate failed. Blocking findings:")
    for finding in blocked:
        print(
            f"  [{finding.tool}] {finding.severity.upper()} {finding.rule} "
            f"{finding.path}: {finding.message}"
        )
    return 1


if __name__ == "__main__":
    sys.exit(main())
