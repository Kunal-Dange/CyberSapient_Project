from botocore.exceptions import ClientError
from fastapi import HTTPException
import pytest

from app.securityhub import (
    enable_securityhub_region,
    enable_securityhub_standards,
    list_securityhub_standards,
)


class FakeSecurityHub:
    def __init__(self):
        self.enabled_calls = []

    def describe_standards(self):
        return {
            "Standards": [
                {"StandardsArn": "arn:aws:securityhub:::ruleset/fsbp", "Name": "FSBP"},
                {"StandardsArn": "arn:aws:securityhub:::ruleset/cis", "Name": "CIS"},
                {"StandardsArn": "arn:aws:securityhub:::ruleset/nist", "Name": "NIST"},
            ]
        }

    def get_enabled_standards(self, **kwargs):
        if kwargs.get("NextToken"):
            return {"StandardsSubscriptions": [{
                "StandardsArn": "arn:aws:securityhub:::ruleset/cis",
                "StandardsStatus": "READY",
                "StandardsSubscriptionArn": "subscription-cis",
            }]}
        return {
            "StandardsSubscriptions": [{
                "StandardsArn": "arn:aws:securityhub:::ruleset/fsbp",
                "StandardsStatus": "READY",
                "StandardsSubscriptionArn": "subscription-fsbp",
            }],
            "NextToken": "next",
        }

    def batch_enable_standards(self, **kwargs):
        self.enabled_calls.append(kwargs)
        return {"StandardsSubscriptions": []}


def test_standards_are_discovered_from_aws_and_include_subscription_state(monkeypatch):
    fake = FakeSecurityHub()
    monkeypatch.setattr("app.securityhub.client", lambda session, service, region: fake)

    standards = list_securityhub_standards(object(), "ap-south-1")

    by_name = {item["name"]: item for item in standards}
    assert set(by_name) == {"CIS", "FSBP", "NIST"}
    assert by_name["CIS"]["enabled"] is True
    assert by_name["CIS"]["status"] == "READY"
    assert by_name["NIST"]["enabled"] is False


def test_activation_requests_only_selected_standards_not_already_enabled(monkeypatch):
    fake = FakeSecurityHub()
    monkeypatch.setattr("app.securityhub.client", lambda session, service, region: fake)

    result = enable_securityhub_standards(
        object(),
        "ap-south-1",
        ["arn:aws:securityhub:::ruleset/cis", "arn:aws:securityhub:::ruleset/nist"],
    )

    assert result["requested"] == ["arn:aws:securityhub:::ruleset/nist"]
    assert fake.enabled_calls == [{
        "StandardsSubscriptionRequests": [
            {"StandardsArn": "arn:aws:securityhub:::ruleset/nist"}
        ]
    }]


def test_disabled_hub_can_still_list_available_standards(monkeypatch):
    class DisabledHub(FakeSecurityHub):
        def get_enabled_standards(self, **kwargs):
            raise ClientError(
                {"Error": {"Code": "ResourceNotFoundException", "Message": "Hub is not enabled"}},
                "GetEnabledStandards",
            )

    fake = DisabledHub()
    monkeypatch.setattr("app.securityhub.client", lambda session, service, region: fake)

    standards = list_securityhub_standards(object(), "ap-south-1")

    assert len(standards) == 3
    assert all(not item["enabled"] for item in standards)


def test_explicit_securityhub_enable_handles_not_yet_enabled_hub(monkeypatch):
    class NotEnabledHub:
        def __init__(self):
            self.enable_calls = []

        def describe_hub(self):
            raise ClientError(
                {"Error": {"Code": "InvalidAccessException", "Message": "Hub is not enabled"}},
                "DescribeHub",
            )

        def enable_security_hub(self, **kwargs):
            self.enable_calls.append(kwargs)
            return {}

    fake = NotEnabledHub()
    monkeypatch.setattr("app.securityhub.client", lambda session, service, region: fake)

    result = enable_securityhub_region(object(), "ap-south-1")

    assert result["status"] == "REQUESTED"
    assert fake.enable_calls == [{"EnableDefaultStandards": False}]


def test_securityhub_changes_require_admin_token(monkeypatch):
    from app import main

    monkeypatch.setattr(main, "SECURITY_HUB_ADMIN_TOKEN", "")

    with pytest.raises(HTTPException) as error:
        main._require_securityhub_admin(None)
    assert error.value.status_code == 403


def test_securityhub_changes_accept_configured_admin_token(monkeypatch):
    from app import main

    monkeypatch.setattr(main, "SECURITY_HUB_ADMIN_TOKEN", "test-token")

    main._require_securityhub_admin("test-token")
