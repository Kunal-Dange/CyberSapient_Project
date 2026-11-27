from app.plugins.base import AuditPlugin
from app.models import Evidence
from app.aws import client

class EC2Plugin(AuditPlugin):
    name = "ec2"
    def collect(self, context):
        out = []
        for region in context.regions:
            ec2 = client(context.session, "ec2", region)
            for page in ec2.get_paginator("describe_security_groups").paginate():
                for sg in page.get("SecurityGroups", []):
                    out.append(Evidence(
                        evidence_id=f"ec2:sg:{region}:{sg['GroupId']}", service="ec2",
                        resource_type="security-group", resource_id=sg["GroupId"],
                        region=region, source="EC2.DescribeSecurityGroups",
                        data={"group_name": sg.get("GroupName"), "ingress": sg.get("IpPermissions", [])}
                    ))
            for page in ec2.get_paginator("describe_volumes").paginate():
                for vol in page.get("Volumes", []):
                    out.append(Evidence(
                        evidence_id=f"ec2:ebs:{region}:{vol['VolumeId']}", service="ec2",
                        resource_type="ebs-volume", resource_id=vol["VolumeId"], region=region,
                        source="EC2.DescribeVolumes",
                        data={"encrypted": vol.get("Encrypted", False), "state": vol.get("State")}
                    ))
            for page in ec2.get_paginator("describe_instances").paginate():
                for reservation in page.get("Reservations", []):
                    for instance in reservation.get("Instances", []):
                        metadata = instance.get("MetadataOptions", {})
                        out.append(Evidence(
                            evidence_id=f"ec2:instance:{region}:{instance['InstanceId']}",
                            service="ec2", resource_type="instance",
                            resource_id=instance["InstanceId"], region=region,
                            source="EC2.DescribeInstances",
                            data={"state": instance.get("State", {}).get("Name"),
                                  "http_tokens": metadata.get("HttpTokens"),
                                  "public_ip": instance.get("PublicIpAddress")}
                        ))
        return out
