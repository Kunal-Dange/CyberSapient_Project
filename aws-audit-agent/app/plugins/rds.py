from app.plugins.base import AuditPlugin
from app.models import Evidence
from app.aws import client

class RDSPlugin(AuditPlugin):
    name = "rds"

    def collect(self, context):
        out = []
        for region in context.regions:
            rds = client(context.session, "rds", region)
            for page in rds.get_paginator("describe_db_instances").paginate():
                for db in page.get("DBInstances", []):
                    out.append(Evidence(
                        evidence_id=f"rds:db:{region}:{db['DBInstanceIdentifier']}",
                        service="rds", resource_type="db-instance",
                        resource_id=db["DBInstanceIdentifier"], region=region,
                        source="RDS.DescribeDBInstances",
                        data={"publicly_accessible": db.get("PubliclyAccessible", False),
                              "storage_encrypted": db.get("StorageEncrypted", False),
                              "engine": db.get("Engine"),
                              "multi_az": db.get("MultiAZ", False),
                              "backup_retention_period": db.get("BackupRetentionPeriod", 0),
                              "deletion_protection": db.get("DeletionProtection", False),
                              "status": db.get("DBInstanceStatus")}
                    ))
            for page in rds.get_paginator("describe_db_clusters").paginate():
                for db in page.get("DBClusters", []):
                    out.append(Evidence(
                        evidence_id=f"rds:cluster:{region}:{db['DBClusterIdentifier']}",
                        service="rds", resource_type="db-cluster",
                        resource_id=db["DBClusterIdentifier"], region=region,
                        source="RDS.DescribeDBClusters",
                        data={"storage_encrypted": db.get("StorageEncrypted", False),
                              "backup_retention_period": db.get("BackupRetentionPeriod", 0),
                              "deletion_protection": db.get("DeletionProtection", False),
                              "engine": db.get("Engine")}
                    ))
        return out
