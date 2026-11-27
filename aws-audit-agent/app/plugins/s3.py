from app.plugins.base import AuditPlugin
from app.models import Evidence
from app.aws import client
from botocore.exceptions import ClientError

class S3Plugin(AuditPlugin):
    name = "s3"
    def collect(self, context):
        s3 = client(context.session, "s3", "us-east-1")
        out = []
        s3control = client(context.session, "s3control", "us-east-1")
        try:
            account_pab = s3control.get_public_access_block(AccountId=context.account_id).get("PublicAccessBlockConfiguration", {})
            account_pab_error = None
        except ClientError as e:
            account_pab, account_pab_error = {}, e.response.get("Error", {}).get("Code", "Unknown")
        out.append(Evidence(evidence_id="s3:account-pab", service="s3", resource_type="account",
            resource_id=context.account_id, source="S3Control.GetPublicAccessBlock",
            data={"block": account_pab, "error": account_pab_error}))
        for bucket in s3.list_buckets().get("Buckets", []):
            name = bucket["Name"]
            data = {"name": name}
            try:
                data["public_access_block"] = s3.get_public_access_block(Bucket=name).get("PublicAccessBlockConfiguration", {})
            except ClientError as e:
                data["public_access_block_error"] = e.response.get("Error", {}).get("Code", "Unknown")
            try:
                loc = s3.get_bucket_location(Bucket=name).get("LocationConstraint")
                region = loc or "us-east-1"
                regional = client(context.session, "s3", region)
                data["encryption"] = regional.get_bucket_encryption(Bucket=name).get("ServerSideEncryptionConfiguration", {})
            except ClientError as e:
                data["encryption_error"] = e.response.get("Error", {}).get("Code", "Unknown")
            out.append(Evidence(evidence_id=f"s3:bucket:{name}", service="s3",
                resource_type="bucket", resource_id=name, source="S3.GetBucket*",
                data=data))
        return out
