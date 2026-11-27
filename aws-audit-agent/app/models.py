from datetime import datetime, timezone
from typing import Any
from pydantic import BaseModel, Field

def utcnow() -> datetime:
    return datetime.now(timezone.utc)

class AuditContext:
    def __init__(self, session, account_id: str, caller_arn: str, regions: list[str]):
        self.session = session
        self.account_id = account_id
        self.caller_arn = caller_arn
        self.regions = regions

class Evidence(BaseModel):
    evidence_id: str
    service: str
    resource_type: str
    resource_id: str
    region: str | None = None
    source: str
    observed_at: datetime = Field(default_factory=utcnow)
    data: dict[str, Any] = Field(default_factory=dict)

class Finding(BaseModel):
    control_id: str
    title: str
    service: str
    severity: str
    status: str
    description: str
    resource_id: str = "account"
    region: str | None = None
    evidence: list[dict[str, Any]] = Field(default_factory=list)
    remediation: str = ""
    frameworks: list[str] = Field(default_factory=list)
    confidence: str = "medium"

class PluginResult(BaseModel):
    plugin: str
    status: str
    evidence_count: int = 0
    error: str | None = None
