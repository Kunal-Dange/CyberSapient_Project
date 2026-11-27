from botocore.exceptions import ClientError

from app.aws import client


def list_securityhub_standards(session, region: str) -> list[dict]:
    securityhub = client(session, "securityhub", region)
    available = securityhub.describe_standards().get("Standards", [])
    enabled = {}
    next_token = None
    try:
        while True:
            params = {"NextToken": next_token} if next_token else {}
            response = securityhub.get_enabled_standards(**params)
            for subscription in response.get("StandardsSubscriptions", []):
                arn = subscription.get("StandardsArn")
                if arn:
                    enabled[arn] = subscription
            next_token = response.get("NextToken")
            if not next_token:
                break
    except ClientError as exc:
        code = exc.response.get("Error", {}).get("Code")
        if code != "ResourceNotFoundException":
            raise

    standards = []
    seen = set()
    for standard in available:
        arn = standard.get("StandardsArn")
        if not arn:
            continue
        seen.add(arn)
        subscription = enabled.get(arn, {})
        standards.append({
            "standards_arn": arn,
            "name": standard.get("Name") or arn,
            "description": standard.get("Description") or "",
            "enabled": arn in enabled,
            "status": subscription.get("StandardsStatus"),
            "subscription_arn": subscription.get("StandardsSubscriptionArn"),
            "standards_managed_by": standard.get("StandardsManagedBy"),
            "enabled_by_default": standard.get("EnabledByDefault"),
        })

    for arn, subscription in enabled.items():
        if arn not in seen:
            standards.append({
                "standards_arn": arn,
                "name": arn,
                "description": "",
                "enabled": True,
                "status": subscription.get("StandardsStatus"),
                "subscription_arn": subscription.get("StandardsSubscriptionArn"),
                "standards_managed_by": None,
                "enabled_by_default": None,
            })
    return sorted(standards, key=lambda item: item["name"].casefold())


def enable_securityhub_standards(session, region: str, standards_arns: list[str]) -> dict:
    standards = list_securityhub_standards(session, region)
    available_arns = {item["standards_arn"] for item in standards}
    unknown_arns = set(standards_arns) - available_arns
    if unknown_arns:
        raise ValueError("One or more standard ARNs are not available in the requested region.")

    enabled_arns = {
        item["standards_arn"] for item in standards if item["enabled"]
    }
    to_enable = [arn for arn in dict.fromkeys(standards_arns) if arn not in enabled_arns]
    if not to_enable:
        return {"region": region, "enabled": [], "already_enabled": list(dict.fromkeys(standards_arns))}

    securityhub = client(session, "securityhub", region)
    responses = []
    for offset in range(0, len(to_enable), 25):
        requests = [{"StandardsArn": arn} for arn in to_enable[offset:offset + 25]]
        response = securityhub.batch_enable_standards(StandardsSubscriptionRequests=requests)
        responses.append(response)
    return {"region": region, "requested": to_enable, "responses": responses}


def enable_securityhub_region(session, region: str) -> dict:
    securityhub = client(session, "securityhub", region)
    try:
        status = securityhub.describe_hub()
        return {"region": region, "status": "ALREADY_ENABLED", "hub_arn": status.get("HubArn")}
    except ClientError as exc:
        code = exc.response.get("Error", {}).get("Code")
        if code not in ("InvalidAccessException", "ResourceNotFoundException"):
            raise
    response = securityhub.enable_security_hub(EnableDefaultStandards=False)
    return {"region": region, "status": "REQUESTED", "response": response}
