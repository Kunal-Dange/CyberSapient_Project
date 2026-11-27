from app.plugins.base import AuditPlugin
from app.models import Evidence
from app.aws import client

class GovernancePlugin(AuditPlugin):
    name = "governance"

    def collect(self, context):
        out = []
        # Account-level IAM account alias is not a security control; capture Organizations
        # membership status without enumerating or assuming access to member accounts.
        org = client(context.session, "organizations", "us-east-1")
        try:
            info = org.describe_organization().get("Organization", {})
            out.append(Evidence(evidence_id="org:account", service="governance",
                resource_type="organization", resource_id=context.account_id,
                source="Organizations.DescribeOrganization",
                data={"organization_id": info.get("Id"), "feature_set": info.get("FeatureSet"),
                      "master_account_id": info.get("MasterAccountId")}))
        except Exception as exc:
            out.append(Evidence(evidence_id="org:account", service="governance",
                resource_type="organization", resource_id=context.account_id,
                source="Organizations.DescribeOrganization",
                data={"organization_error": type(exc).__name__}))
        return out
