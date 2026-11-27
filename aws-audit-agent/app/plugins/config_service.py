from app.plugins.base import AuditPlugin
from app.models import Evidence
from app.aws import client
from botocore.exceptions import ClientError

class ConfigPlugin(AuditPlugin):
    name = "config"
    def collect(self, context):
        out = []
        for region in context.regions:
            cfg = client(context.session, "config", region)
            try:
                recorders = cfg.describe_configuration_recorders().get("ConfigurationRecorders", [])
                statuses = cfg.describe_configuration_recorder_status().get("ConfigurationRecordersStatus", [])
                out.append(Evidence(evidence_id=f"config:{region}", service="config",
                    resource_type="regional-service", resource_id="config-recorder", region=region,
                    source="Config.DescribeConfigurationRecorders/Status",
                    data={"recorders": recorders, "statuses": statuses}))
            except ClientError as e:
                out.append(Evidence(evidence_id=f"config:{region}", service="config",
                    resource_type="regional-service", resource_id="config-recorder", region=region,
                    source="Config.DescribeConfigurationRecorders",
                    data={"error": e.response.get("Error", {}).get("Code", "Unknown")}))
        return out
