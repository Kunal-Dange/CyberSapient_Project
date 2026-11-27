from app.plugins.base import AuditPlugin
from app.models import Evidence
from app.aws import client

class IAMPlugin(AuditPlugin):
    name = "iam"
    def collect(self, context):
        iam = client(context.session, "iam", "us-east-1")
        out = []
        summary = iam.get_account_summary().get("SummaryMap", {})
        out.append(Evidence(
            evidence_id="iam:account-summary", service="iam", resource_type="account",
            resource_id=context.account_id, source="IAM.GetAccountSummary",
            data={"AccountMFAEnabled": summary.get("AccountMFAEnabled", 0),
                  "AccountAccessKeysPresent": summary.get("AccountAccessKeysPresent", 0)}
        ))
        try:
            policy = iam.get_account_password_policy().get("PasswordPolicy", {})
            out.append(Evidence(
                evidence_id="iam:password-policy", service="iam", resource_type="account",
                resource_id=context.account_id, source="IAM.GetAccountPasswordPolicy",
                data={"policy_present": True, "policy": policy}
            ))
        except iam.exceptions.NoSuchEntityException:
            out.append(Evidence(
                evidence_id="iam:password-policy", service="iam", resource_type="account",
                resource_id=context.account_id, source="IAM.GetAccountPasswordPolicy",
                data={"policy_present": False}
            ))
        return out
