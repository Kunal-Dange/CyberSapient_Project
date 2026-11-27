import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError

AWS_CONFIG = Config(
    retries={"max_attempts": 8, "mode": "adaptive"},
    user_agent_extra="aws-account-audit-agent/0.1",
)

def make_session(profile_name: str | None = None):
    return boto3.Session(profile_name=profile_name) if profile_name else boto3.Session()

def get_identity(session):
    return session.client("sts", config=AWS_CONFIG).get_caller_identity()

def discover_regions(session) -> list[str]:
    ec2 = session.client("ec2", region_name=session.region_name or "us-east-1", config=AWS_CONFIG)
    response = ec2.describe_regions(AllRegions=False)
    return sorted(r["RegionName"] for r in response.get("Regions", []))

def client(session, service: str, region: str | None = None):
    return session.client(service, region_name=region, config=AWS_CONFIG)
