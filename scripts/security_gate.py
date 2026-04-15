#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


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
    cvss_score: float | None = None
    package: str | None = None
    version: str | None = None
    fixed_version: str | None = None


@dataclass
class SecurityPolicy:
    max_cvss_score: float | None
    auto_block_severities: set[str]
    warn_severities: set[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fail the pipeline when SAST/SCA results violate security policy."
    )
    parser.add_argument("--bandit", required=True, type=Path)
    parser.add_argument("--eslint", required=True, type=Path)
    parser.add_argument("--semgrep", required=True, type=Path)
    parser.add_argument("--policy", required=True, type=Path)
    parser.add_argument("--trivy", action="append", default=[], type=Path)
    return parser.parse_args()


def load_json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"Missing report: {path}")
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_policy(path: Path) -> SecurityPolicy:
    if not path.exists():
        raise FileNotFoundError(f"Missing security policy: {path}")

    with path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle) or {}

    policy = payload.get("policy", {})
    return SecurityPolicy(
        max_cvss_score=(
            float(policy["max_cvss_score"])
            if policy.get("max_cvss_score") is not None
            else None
        ),
        auto_block_severities={
            str(value).strip().lower()
            for value in policy.get("auto_block_severities", [])
        },
        warn_severities={
            str(value).strip().lower() for value in policy.get("warn_severities", [])
        },
    )


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


def best_cvss_score(vulnerability: dict[str, Any]) -> float | None:
    scores: list[float] = []
    for source in (vulnerability.get("CVSS") or {}).values():
        for key in ("V3Score", "V2Score"):
            value = source.get(key)
            if value is None:
                continue
            try:
                scores.append(float(value))
            except (TypeError, ValueError):
                continue
    return max(scores) if scores else None


def trivy_findings(payload: dict[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    for result in payload.get("Results", []):
        target = result.get("Target", "")
        for vulnerability in result.get("Vulnerabilities") or []:
            findings.append(
                Finding(
                    tool="trivy",
                    severity=normalize_severity(vulnerability.get("Severity")),
                    path=target,
                    rule=vulnerability.get("VulnerabilityID", "trivy"),
                    message=(
                        vulnerability.get("Title")
                        or vulnerability.get("Description")
                        or ""
                    ),
                    cvss_score=best_cvss_score(vulnerability),
                    package=vulnerability.get("PkgName"),
                    version=vulnerability.get("InstalledVersion"),
                    fixed_version=vulnerability.get("FixedVersion"),
                )
            )
    return findings


def summarize(findings: list[Finding]) -> dict[str, int]:
    counts = {key: 0 for key in SEVERITY_ORDER}
    for finding in findings:
        counts[finding.severity] += 1
    return counts


def is_blocked(finding: Finding, policy: SecurityPolicy) -> bool:
    if finding.tool != "trivy":
        return SEVERITY_ORDER[finding.severity] >= SEVERITY_ORDER["high"]

    if finding.severity in policy.auto_block_severities:
        return True

    if (
        policy.max_cvss_score is not None
        and finding.cvss_score is not None
        and finding.cvss_score > policy.max_cvss_score
    ):
        return True

    return False


def is_warning(finding: Finding, policy: SecurityPolicy) -> bool:
    return finding.tool == "trivy" and finding.severity in policy.warn_severities


def format_finding(finding: Finding) -> str:
    if finding.tool != "trivy":
        return (
            f"  [{finding.tool}] {finding.severity.upper()} {finding.rule} "
            f"{finding.path}: {finding.message}"
        )

    package = finding.package or "unknown-package"
    version = finding.version or "unknown-version"
    fixed_version = finding.fixed_version or "-"
    cvss = f"{finding.cvss_score:.1f}" if finding.cvss_score is not None else "-"
    return (
        f"  [trivy] {finding.severity.upper()} {package}@{version} "
        f"{finding.rule} target={finding.path} cvss={cvss} fixed={fixed_version}: "
        f"{finding.message}"
    )


def main() -> int:
    args = parse_args()
    policy = load_policy(args.policy)

    findings = [
        *bandit_findings(load_json(args.bandit)),
        *eslint_findings(load_json(args.eslint)),
        *semgrep_findings(load_json(args.semgrep)),
        *[
            finding
            for report in args.trivy
            for finding in trivy_findings(load_json(report))
        ],
    ]

    counts = summarize(findings)
    blocked = [finding for finding in findings if is_blocked(finding, policy)]
    warnings = [finding for finding in findings if is_warning(finding, policy)]

    print("Security scan summary:")
    for severity in ("critical", "high", "medium", "low"):
        print(f"  {severity}: {counts[severity]}")

    if args.trivy:
        policy_cvss = (
            f"{policy.max_cvss_score:.1f}"
            if policy.max_cvss_score is not None
            else "disabled"
        )
        print("Trivy policy:")
        print(
            "  auto_block_severities: "
            + ", ".join(sorted(policy.auto_block_severities))
        )
        print(f"  max_cvss_score: {policy_cvss}")

    if warnings:
        print("Security warnings:")
        for finding in warnings:
            print(format_finding(finding))

    if not blocked:
        print("Security gate passed: no blocking findings detected.")
        return 0

    print("Security gate failed. Blocking findings:")
    for finding in blocked:
        print(format_finding(finding))
    return 1


if __name__ == "__main__":
    sys.exit(main())
