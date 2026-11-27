from app.plugins.base import AuditPlugin
from app.models import Evidence
from app.aws import client

class LambdaPlugin(AuditPlugin):
    name = "lambda"

    def collect(self, context):
        out = []
        for region in context.regions:
            lam = client(context.session, "lambda", region)
            for page in lam.get_paginator("list_functions").paginate():
                for fn in page.get("Functions", []):
                    out.append(Evidence(
                        evidence_id=f"lambda:{region}:{fn['FunctionArn']}",
                        service="lambda", resource_type="function",
                        resource_id=fn["FunctionArn"], region=region,
                        source="Lambda.ListFunctions",
                        data={"runtime": fn.get("Runtime"),
                              "last_modified": fn.get("LastModified"),
                              "kms_key_arn": fn.get("KMSKeyArn"),
                              "tracing_mode": fn.get("TracingConfig", {}).get("Mode"),
                              "architectures": fn.get("Architectures", [])}
                    ))
        return out
