from app.models import Evidence
from app.controls.evaluator import evaluate

def test_open_ssh_is_failed():
    e = Evidence(evidence_id="sg", service="ec2", resource_type="security-group",
        resource_id="sg-test", region="ap-south-1", source="EC2.DescribeSecurityGroups",
        data={"ingress":[{"IpProtocol":"tcp","FromPort":22,"ToPort":22,
                          "IpRanges":[{"CidrIp":"0.0.0.0/0"}]}]})
    findings = evaluate([e])
    ssh = [f for f in findings if f.control_id == "EC2-001" and f.resource_id == "sg-test"]
    assert ssh and ssh[0].status == "FAIL"

def test_no_ssh_ingress_passes():
    e = Evidence(evidence_id="sg", service="ec2", resource_type="security-group",
        resource_id="sg-test", region="ap-south-1", source="EC2.DescribeSecurityGroups",
        data={"ingress":[]})
    findings = evaluate([e])
    ssh = [f for f in findings if f.control_id == "EC2-001" and f.resource_id == "sg-test"]
    assert ssh and ssh[0].status == "PASS"
