from app.plugins.base import AuditPlugin
from app.models import Evidence
from app.aws import client

class NetworkingPlugin(AuditPlugin):
    name = "networking"

    def collect(self, context):
        out = []
        for region in context.regions:
            ec2 = client(context.session, "ec2", region)
            for page in ec2.get_paginator("describe_vpcs").paginate():
                for vpc in page.get("Vpcs", []):
                    out.append(Evidence(
                        evidence_id=f"vpc:{region}:{vpc['VpcId']}", service="networking",
                        resource_type="vpc", resource_id=vpc["VpcId"], region=region,
                        source="EC2.DescribeVpcs",
                        data={"is_default": vpc.get("IsDefault", False),
                              "cidr": vpc.get("CidrBlock"),
                              "flow_logs_enabled": False}
                    ))
            for page in ec2.get_paginator("describe_flow_logs").paginate():
                for flow in page.get("FlowLogs", []):
                    out.append(Evidence(
                        evidence_id=f"flowlog:{region}:{flow['FlowLogId']}", service="networking",
                        resource_type="flow-log", resource_id=flow["FlowLogId"], region=region,
                        source="EC2.DescribeFlowLogs",
                        data={"resource_ids": flow.get("ResourceIds", []),
                              "status": flow.get("FlowLogStatus"),
                              "traffic_type": flow.get("TrafficType")}
                    ))
            for page in ec2.get_paginator("describe_network_acls").paginate():
                for acl in page.get("NetworkAcls", []):
                    out.append(Evidence(
                        evidence_id=f"nacl:{region}:{acl['NetworkAclId']}", service="networking",
                        resource_type="network-acl", resource_id=acl["NetworkAclId"], region=region,
                        source="EC2.DescribeNetworkAcls",
                        data={"is_default": acl.get("IsDefault", False),
                              "entries": acl.get("Entries", [])}
                    ))
        return out
