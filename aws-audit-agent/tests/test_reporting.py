from app.engine import _score_findings, _securityhub_report
from app.models import Evidence, Finding
from app.reporting import prepare_report


def test_score_excludes_unknown_and_not_applicable_checks():
    findings = [
        Finding(control_id="A", title="A", service="test", severity="LOW", status="PASS", description=""),
        Finding(control_id="B", title="B", service="test", severity="LOW", status="FAIL", description=""),
        Finding(control_id="C", title="C", service="test", severity="LOW", status="UNKNOWN", description=""),
        Finding(control_id="D", title="D", service="test", severity="LOW", status="NOT_APPLICABLE", description=""),
    ]

    assert _score_findings(findings) == {
        "value": 50,
        "passed": 1,
        "failed": 1,
        "evaluated": 2,
        "excluded": 2,
    }


def test_securityhub_report_separates_resolved_findings_and_lists_regional_standards():
    evidence = [
        Evidence(
            evidence_id="hub",
            service="securityhub",
            resource_type="regional-service",
            resource_id="securityhub",
            region="ap-south-1",
            source="SecurityHub.DescribeHub",
            data={"enabled": True},
        ),
        Evidence(
            evidence_id="standard",
            service="securityhub",
            resource_type="standard",
            resource_id="arn:aws:securityhub:::ruleset/test",
            region="ap-south-1",
            source="SecurityHub.DescribeStandards",
            data={"name": "Example standard", "enabled": True, "status": "READY"},
        ),
        Evidence(
            evidence_id="open",
            service="securityhub",
            resource_type="finding",
            resource_id="finding-open",
            region="ap-south-1",
            source="SecurityHub.GetFindings",
            data={"severity": "HIGH", "workflow_status": "NEW"},
        ),
        Evidence(
            evidence_id="resolved",
            service="securityhub",
            resource_type="finding",
            resource_id="finding-resolved",
            region="ap-south-1",
            source="SecurityHub.GetFindings",
            data={"severity": "CRITICAL", "workflow_status": "RESOLVED"},
        ),
    ]

    result = _securityhub_report(evidence)

    assert result["active_findings"] == 1
    assert result["severity_counts"] == {"HIGH": 1}
    assert result["standards"][0]["enabled_regions"] == ["ap-south-1"]
    assert result["standards"][0]["region_statuses"] == {"ap-south-1": "READY"}
    assert [finding["id"] for finding in result["findings"] if finding["is_open"]] == ["finding-open"]


def test_legacy_audit_gets_safe_defaults_for_the_new_report():
    report = prepare_report({
        "audit_id": "old-audit",
        "summary": {"PASS": 3, "FAIL": 1, "UNKNOWN": 1},
        "findings": [],
    })

    assert report["score"]["value"] == 75
    assert report["securityhub"]["findings"] == []
    assert report["charts"]["control_status"][0]["count"] == 3
