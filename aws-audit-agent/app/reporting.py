def prepare_report(audit: dict) -> dict:
    report = dict(audit)
    findings = report.get("findings", [])
    summary = report.get("summary", {})
    statuses = ("PASS", "FAIL", "UNKNOWN", "NOT_APPLICABLE")
    total = sum(summary.get(status, 0) for status in statuses)
    if not report.get("score"):
        passed = summary.get("PASS", 0)
        failed = summary.get("FAIL", 0)
        evaluated = passed + failed
        report["score"] = {
            "value": round(passed * 100 / evaluated) if evaluated else None,
            "passed": passed,
            "failed": failed,
            "evaluated": evaluated,
            "excluded": summary.get("UNKNOWN", 0) + summary.get("NOT_APPLICABLE", 0),
        }
    if not report.get("charts"):
        report["charts"] = {
            "control_status": [
                {
                    "label": status.replace("_", " ").title(),
                    "status": status,
                    "count": summary.get(status, 0),
                    "percent": round(summary.get(status, 0) * 100 / total, 1) if total else 0,
                }
                for status in statuses
            ],
            "securityhub_severity": [
                {"label": severity.title(), "count": 0}
                for severity in ("CRITICAL", "HIGH", "MEDIUM", "LOW", "INFORMATIONAL", "UNKNOWN")
            ],
            "securityhub_compliance": [
                {"label": status.replace("_", " ").title(), "status": status, "count": 0, "percent": 0}
                for status in ("FAILED", "PASSED", "WARNING", "NOT_AVAILABLE", "UNKNOWN")
            ],
        }
    if not report.get("securityhub"):
        report["securityhub"] = {
            "regions": [],
            "standards": [],
            "findings": [],
            "active_findings": 0,
            "severity_counts": {},
            "compliance_counts": {},
        }
    report.setdefault("recommendations", [
        "Review the report scope and collector limitations before interpreting these results."
    ])
    report.setdefault("services_scanned", [])
    report.setdefault("plugin_results", [])
    report.setdefault("evidence_count", 0)
    report.setdefault("regions", [])
    report.setdefault("caller_arn", "Not recorded")
    report.setdefault("account_id", "Not recorded")
    report.setdefault("started_at", "Not recorded")
    report.setdefault("completed_at", report["started_at"])
    report.setdefault("summary", {})
    report["findings"] = findings
    return report
