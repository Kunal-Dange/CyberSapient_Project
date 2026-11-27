from app.plugins.base import AuditPlugin
from app.models import Evidence
from app.aws import client

class ContainersPlugin(AuditPlugin):
    name = "containers"

    def collect(self, context):
        out = []
        for region in context.regions:
            ecr = client(context.session, "ecr", region)
            for page in ecr.get_paginator("describe_repositories").paginate():
                for repo in page.get("repositories", []):
                    out.append(Evidence(
                        evidence_id=f"ecr:{region}:{repo['repositoryArn']}",
                        service="containers", resource_type="ecr-repository",
                        resource_id=repo["repositoryName"], region=region,
                        source="ECR.DescribeRepositories",
                        data={"scan_on_push": repo.get("imageScanningConfiguration", {}).get("scanOnPush", False),
                              "tag_mutability": repo.get("imageTagMutability"),
                              "encryption_type": repo.get("encryptionConfiguration", {}).get("encryptionType")}
                    ))
            ecs = client(context.session, "ecs", region)
            for page in ecs.get_paginator("list_clusters").paginate():
                for arn in page.get("clusterArns", []):
                    desc = ecs.describe_clusters(clusters=[arn], include=["SETTINGS"])["clusters"][0]
                    settings = {x.get("name"): x.get("value") for x in desc.get("settings", [])}
                    out.append(Evidence(
                        evidence_id=f"ecs:{region}:{arn}", service="containers",
                        resource_type="ecs-cluster", resource_id=arn, region=region,
                        source="ECS.DescribeClusters",
                        data={"status": desc.get("status"), "settings": settings,
                              "execute_command_configuration": desc.get("configuration", {}).get("executeCommandConfiguration", {})}
                    ))
        return out
