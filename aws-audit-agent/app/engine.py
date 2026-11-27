from datetime import datetime, timezone
from app.aws import get_identity, discover_regions
from app.models import AuditContext, PluginResult
from app.plugins import get_plugins
from app.controls.evaluator import evaluate

def _score_findings(findings):
    counts = {}
    for finding in findings:
        counts[finding.status] = counts.get(finding.status, 0) + 1
    evaluated = counts.get("PASS", 0) + counts.get("FAIL", 0)
    return {
        "value": round(counts.get("PASS", 0) * 100 / evaluated) if evaluated else None,
        "passed": counts.get("PASS", 0),
        "failed": counts.get("FAIL", 0),
        "evaluated": evaluated,
        "excluded": counts.get("UNKNOWN", 0) + counts.get("NOT_APPLICABLE", 0),
    }

def _securityhub_report(evidence):
    standards = {}
    findings = []
    regions = []
    for item in evidence:
        if item.resource_type == "regional-service":
            regions.append({
                "region": item.region,
                "enabled": item.data.get("enabled"),
                "error": item.data.get("collection_error"),
                "standards_error": item.data.get("standards_error"),
                "findings_error": item.data.get("findings_error"),
            })
        elif item.resource_type == "standard":
            standard = standards.setdefault(item.resource_id, {
                "arn": item.resource_id,
                "name": item.data.get("name") or item.resource_id,
                "description": item.data.get("description") or "",
                "enabled_regions": [],
                "available_regions": [],
                "region_statuses": {},
            })
            if item.region and item.region not in standard["available_regions"]:
                standard["available_regions"].append(item.region)
            if item.region:
                standard["region_statuses"][item.region] = (
                    item.data.get("status") or ("ENABLED" if item.data.get("enabled") else "AVAILABLE")
                )
            if item.data.get("enabled") and item.region and item.region not in standard["enabled_regions"]:
                standard["enabled_regions"].append(item.region)
        elif item.resource_type == "finding":
            finding = dict(item.data)
            finding["id"] = item.resource_id
            finding["region"] = item.region
            finding["is_open"] = finding.get("workflow_status") not in ("RESOLVED", "SUPPRESSED")
            findings.append(finding)

    active_findings = [finding for finding in findings if finding["is_open"]]
    severity_counts = {}
    compliance_counts = {}
    for finding in active_findings:
        severity = (finding.get("severity") or "UNKNOWN").upper()
        compliance = (finding.get("compliance_status") or "UNKNOWN").upper()
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
        compliance_counts[compliance] = compliance_counts.get(compliance, 0) + 1

    return {
        "regions": sorted(regions, key=lambda item: item["region"] or ""),
        "standards": sorted(standards.values(), key=lambda item: item["name"].casefold()),
        "findings": findings,
        "active_findings": len(active_findings),
        "severity_counts": severity_counts,
        "compliance_counts": compliance_counts,
    }

def _recommendations(score, securityhub, plugin_results, regions):
    recommendations = []
    enabled_regions = {item["region"] for item in securityhub["regions"] if item.get("enabled")}
    collection_errors = any(
        item.get("error") or item.get("standards_error") or item.get("findings_error")
        for item in securityhub["regions"]
    )
    if not enabled_regions:
        if collection_errors:
            recommendations.append("Resolve Security Hub access or collection errors before concluding whether it is enabled or interpreting its coverage.")
        else:
            recommendations.append("Enable Security Hub in the regions in scope, then activate the standards required by your organization.")
    elif enabled_regions != set(regions):
        recommendations.append("Review Security Hub coverage: it is not enabled in every region included in this audit.")
    if collection_errors:
        recommendations.append("Review Security Hub collection errors; standards or findings may be missing from this report.")
    if securityhub["severity_counts"].get("CRITICAL", 0):
        recommendations.append("Triage the active Critical Security Hub findings first and record approved exceptions.")
    if securityhub["severity_counts"].get("HIGH", 0):
        recommendations.append("Prioritize active High Security Hub findings and assign owners and remediation dates.")
    if score["failed"]:
        recommendations.append("Review failed built-in checks and validate remediation against workload requirements before making changes.")
    if any(item.status == "ERROR" for item in plugin_results):
        recommendations.append("Resolve collector errors and rerun the audit; incomplete evidence can leave controls unknown.")
    if not recommendations:
        recommendations.append("No immediate recommendations were generated from the collected evidence; review unknowns, exceptions, and the coverage notes before relying on this result.")
    return recommendations

def run_audit(session, requested_regions=None):
    started_at = datetime.now(timezone.utc)
    identity = get_identity(session)
    regions = requested_regions or discover_regions(session)
    context = AuditContext(session, identity["Account"], identity["Arn"], regions)
    evidence, plugin_results = [], []
    for plugin in get_plugins():
        try:
            collected = plugin.collect(context)
            evidence.extend(collected)
            plugin_results.append(PluginResult(plugin=plugin.name, status="COMPLETED", evidence_count=len(collected)))
        except Exception as exc:
            # Keep scans resilient; surface the error in the report. Avoid dumping credentials or request headers.
            plugin_results.append(PluginResult(plugin=plugin.name, status="ERROR",
                error=f"{type(exc).__name__}: {str(exc)[:400]}"))
    findings = evaluate(evidence)
    failed_plugins = {p.plugin for p in plugin_results if p.status == "ERROR"}
    plugin_to_services = {
        "iam": {"iam"}, "ec2": {"ec2"}, "s3": {"s3"},
        "cloudtrail": {"cloudtrail"}, "securityhub": {"securityhub"},
        "config": {"config"}, "networking": {"networking"},
        "rds": {"rds"}, "lambda": {"lambda"}, "kms": {"kms"},
        "containers": {"containers"}, "dynamodb": {"dynamodb"},
        "governance": {"governance"},
    }
    unavailable_services = set().union(*(plugin_to_services.get(name, set()) for name in failed_plugins))
    for finding in findings:
        if finding.service in unavailable_services and not finding.evidence:
            finding.status = "UNKNOWN"
            finding.confidence = "low"
            finding.description += " Evidence collection failed for this service; review the collection error before interpreting this control."
    counts = {}
    for f in findings:
        counts[f.status] = counts.get(f.status, 0) + 1
    securityhub_report = _securityhub_report(
        [item for item in evidence if item.service == "securityhub"]
    )
    score = _score_findings(findings)
    control_total = sum(counts.values())
    control_chart = [
        {
            "label": status.replace("_", " ").title(),
            "status": status,
            "count": counts.get(status, 0),
            "percent": round(counts.get(status, 0) * 100 / control_total, 1) if control_total else 0,
        }
        for status in ("PASS", "FAIL", "UNKNOWN", "NOT_APPLICABLE")
    ]
    hub_severity_chart = [
        {"label": severity.title(), "count": securityhub_report["severity_counts"].get(severity, 0)}
        for severity in ("CRITICAL", "HIGH", "MEDIUM", "LOW", "INFORMATIONAL", "UNKNOWN")
    ]
    hub_compliance_chart = [
        {
            "label": status.replace("_", " ").title(),
            "status": status,
            "count": securityhub_report["compliance_counts"].get(status, 0),
            "percent": round(
                securityhub_report["compliance_counts"].get(status, 0) * 100
                / securityhub_report["active_findings"],
                1,
            ) if securityhub_report["active_findings"] else 0,
        }
        for status in ("FAILED", "PASSED", "WARNING", "NOT_AVAILABLE", "UNKNOWN")
    ]
    return {
        "audit_id": started_at.strftime("%Y%m%dT%H%M%S%fZ"),
        "started_at": started_at.isoformat(),
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "account_id": identity["Account"],
        "caller_arn": identity["Arn"],
        "regions": regions,
        "services_scanned": [p.plugin for p in plugin_results],
        "plugin_results": [p.model_dump(mode="json") for p in plugin_results],
        "evidence_count": len(evidence),
        "findings": [f.model_dump(mode="json") for f in findings],
        "summary": counts,
        "score": score,
        "securityhub": securityhub_report,
        "charts": {
            "control_status": control_chart,
            "securityhub_severity": hub_severity_chart,
            "securityhub_compliance": hub_compliance_chart,
        },
        "recommendations": _recommendations(score, securityhub_report, plugin_results, regions),
    }
