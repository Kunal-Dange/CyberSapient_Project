from app.plugins.base import AuditPlugin
from app.models import Evidence
from app.aws import client

class DynamoDBPlugin(AuditPlugin):
    name = "dynamodb"

    def collect(self, context):
        out = []
        for region in context.regions:
            ddb = client(context.session, "dynamodb", region)
            for page in ddb.get_paginator("list_tables").paginate():
                for name in page.get("TableNames", []):
                    desc = ddb.describe_table(TableName=name)["Table"]
                    pitr = ddb.describe_continuous_backups(TableName=name).get("ContinuousBackupsDescription", {})
                    out.append(Evidence(
                        evidence_id=f"dynamodb:{region}:{name}", service="dynamodb",
                        resource_type="table", resource_id=name, region=region,
                        source="DynamoDB.DescribeTable/ContinuousBackups",
                        data={"status": desc.get("TableStatus"),
                              "sse_description": desc.get("SSEDescription", {}),
                              "point_in_time_recovery": pitr.get("PointInTimeRecoveryDescription", {}).get("PointInTimeRecoveryStatus")}
                    ))
        return out
