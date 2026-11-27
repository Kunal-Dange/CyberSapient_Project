from app.plugins.base import AuditPlugin
from app.models import Evidence
from app.aws import client

class KMSPlugin(AuditPlugin):
    name = "kms"

    def collect(self, context):
        out = []
        for region in context.regions:
            kms = client(context.session, "kms", region)
            paginator = kms.get_paginator("list_keys")
            for page in paginator.paginate():
                for key in page.get("Keys", []):
                    key_id = key["KeyId"]
                    try:
                        meta = kms.describe_key(KeyId=key_id)["KeyMetadata"]
                        if meta.get("KeyManager") != "CUSTOMER":
                            continue
                        rotation = kms.get_key_rotation_status(KeyId=key_id).get("KeyRotationEnabled", False) if meta.get("KeySpec", "SYMMETRIC_DEFAULT") == "SYMMETRIC_DEFAULT" and meta.get("KeyUsage") == "ENCRYPT_DECRYPT" else None
                        out.append(Evidence(
                            evidence_id=f"kms:{region}:{key_id}", service="kms",
                            resource_type="customer-managed-key", resource_id=key_id,
                            region=region, source="KMS.DescribeKey/GetKeyRotationStatus",
                            data={"enabled": meta.get("Enabled", False),
                                  "key_state": meta.get("KeyState"),
                                  "key_manager": meta.get("KeyManager"),
                                  "key_spec": meta.get("KeySpec"),
                                  "rotation_enabled": rotation,
                                  "key_arn": meta.get("Arn")}
                        ))
                    except Exception as exc:
                        out.append(Evidence(
                            evidence_id=f"kms:{region}:{key_id}", service="kms",
                            resource_type="customer-managed-key", resource_id=key_id,
                            region=region, source="KMS.DescribeKey",
                            data={"collection_error": type(exc).__name__}
                        ))
        return out
