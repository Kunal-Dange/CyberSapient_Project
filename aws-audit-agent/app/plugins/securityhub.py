from app.plugins.base import AuditPlugin
from app.models import Evidence
from app.aws import client
from botocore.exceptions import ClientError
from app.securityhub import list_securityhub_standards

class SecurityHubPlugin(AuditPlugin):
    name = "securityhub"

    def collect(self, context):
        out = []
        for region in context.regions:
            sh = client(context.session, "securityhub", region)
            try:
                status = sh.describe_hub()
                regional_data = {"enabled": True, "hub_arn": status.get("HubArn")}
            except ClientError as e:
                code = e.response.get("Error", {}).get("Code", "Unknown")
                disabled = code == "ResourceNotFoundException"
                regional_data = {
                    "enabled": False if disabled else None,
                    "collection_error": None if disabled else code,
                }
                try:
                    standards = list_securityhub_standards(context.session, region)
                    for standard in standards:
                        out.append(Evidence(
                            evidence_id=f"securityhub:standard:{region}:{standard['standards_arn']}",
                            service="securityhub", resource_type="standard",
                            resource_id=standard["standards_arn"], region=region,
                            source="SecurityHub.GetEnabledStandards/DescribeStandards",
                            data=standard
                        ))
                except ClientError as standards_error:
                    regional_data["standards_error"] = (
                        standards_error.response.get("Error", {}).get("Code", "Unknown")
                    )
                out.append(Evidence(
                    evidence_id=f"securityhub:{region}", service="securityhub",
                    resource_type="regional-service", resource_id="securityhub",
                    region=region, source="SecurityHub.DescribeHub",
                    data=regional_data
                ))
                continue

            try:
                for standard in list_securityhub_standards(context.session, region):
                    out.append(Evidence(
                        evidence_id=f"securityhub:standard:{region}:{standard['standards_arn']}",
                        service="securityhub", resource_type="standard",
                        resource_id=standard["standards_arn"], region=region,
                        source="SecurityHub.GetEnabledStandards/DescribeStandards",
                        data=standard
                    ))
            except ClientError as e:
                regional_data["standards_error"] = e.response.get("Error", {}).get("Code", "Unknown")

            try:
                paginator = sh.get_paginator("get_findings")
                for page in paginator.paginate(
                    Filters={"RecordState": [{"Value": "ACTIVE", "Comparison": "EQUALS"}]}
                ):
                    for finding in page.get("Findings", []):
                        compliance = finding.get("Compliance") or {}
                        product_fields = finding.get("ProductFields") or {}
                        remediation = (finding.get("Remediation") or {}).get("Recommendation") or {}
                        out.append(Evidence(
                            evidence_id=f"securityhub:finding:{region}:{finding.get('Id')}",
                            service="securityhub", resource_type="finding",
                            resource_id=finding.get("Id", "unknown"), region=region,
                            source="SecurityHub.GetFindings",
                            data={
                                "title": finding.get("Title"),
                                "description": finding.get("Description"),
                                "severity": (finding.get("Severity") or {}).get("Label"),
                                "compliance_status": compliance.get("Status"),
                                "workflow_status": (finding.get("Workflow") or {}).get("Status"),
                                "record_state": finding.get("RecordState"),
                                "product_name": product_fields.get("aws/securityhub/ProductName")
                                    or finding.get("ProductName"),
                                "generator_id": finding.get("GeneratorId"),
                                "standard_id": compliance.get("AssociatedStandards", []),
                                "created_at": finding.get("CreatedAt"),
                                "updated_at": finding.get("UpdatedAt"),
                                "resources": [
                                    {
                                        "type": resource.get("Type"),
                                        "id": resource.get("Id"),
                                        "region": resource.get("Region"),
                                        "name": ((resource.get("Details") or {}).get("Other") or {}).get("Name"),
                                    }
                                    for resource in (finding.get("Resources") or [])
                                ],
                                "remediation": remediation,
                            }
                        ))
            except ClientError as e:
                regional_data["findings_error"] = e.response.get("Error", {}).get("Code", "Unknown")
            out.append(Evidence(
                evidence_id=f"securityhub:{region}", service="securityhub",
                resource_type="regional-service", resource_id="securityhub",
                region=region, source="SecurityHub.DescribeHub",
                data=regional_data
            ))
        return out
