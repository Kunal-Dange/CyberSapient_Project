from app.plugins.base import AuditPlugin
from app.models import Evidence
from app.aws import client

class CloudTrailPlugin(AuditPlugin):
    name = "cloudtrail"
    def collect(self, context):
        out = []
        for region in context.regions:
            ct = client(context.session, "cloudtrail", region)
            trails = ct.describe_trails(includeShadowTrails=False).get("trailList", [])
            for trail in trails:
                status = ct.get_trail_status(Name=trail["TrailARN"])
                out.append(Evidence(
                    evidence_id=f"cloudtrail:{region}:{trail['TrailARN']}", service="cloudtrail",
                    resource_type="trail", resource_id=trail["TrailARN"], region=region,
                    source="CloudTrail.DescribeTrails/GetTrailStatus",
                    data={"is_multi_region": trail.get("IsMultiRegionTrail", False),
                          "is_logging": status.get("IsLogging", False),
                          "log_file_validation": trail.get("LogFileValidationEnabled", False),
                          "kms_key_id": trail.get("KmsKeyId")}
                ))
        return out
