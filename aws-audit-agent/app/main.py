from fastapi import FastAPI, BackgroundTasks, HTTPException, Header
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import Request
from pydantic import BaseModel, Field
from pathlib import Path
import boto3, hmac, logging
from botocore.exceptions import ClientError
from app.config import APP_NAME, LOG_LEVEL, SECURITY_HUB_ADMIN_TOKEN
from app.engine import run_audit
from app.store import save_audit, list_audits, get_audit
from app.reporting import prepare_report
from app.securityhub import (
    enable_securityhub_region,
    enable_securityhub_standards,
    list_securityhub_standards,
)

logging.basicConfig(level=getattr(logging, LOG_LEVEL.upper(), logging.INFO))
app = FastAPI(title=APP_NAME, version="0.1.0")
BASE = Path(__file__).parent
templates = Jinja2Templates(directory=str(BASE / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE / "static")), name="static")

class AuditRequest(BaseModel):
    regions: list[str] | None = Field(default=None, description="Optional explicit region allow-list")
    include_global: bool = True

class EnableStandardsRequest(BaseModel):
    regions: list[str] = Field(min_length=1, max_length=50)
    standards_arns: list[str] = Field(min_length=1, max_length=100)

class EnableSecurityHubRequest(BaseModel):
    region: str

def _require_securityhub_admin(admin_token):
    if not SECURITY_HUB_ADMIN_TOKEN or not admin_token or not hmac.compare_digest(
        admin_token, SECURITY_HUB_ADMIN_TOKEN
    ):
        raise HTTPException(403, "Security Hub changes are disabled or the admin token is invalid.")

def do_scan(regions):
    try:
        session = boto3.Session()
        result = run_audit(session, regions)
        save_audit(result["audit_id"], result)
    except Exception:
        logging.exception("Audit scan failed")

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "audits": list_audits(),
            "app_name": APP_NAME
        }
    )

@app.get("/api/health")
def health():
    return {"status":"ok","application":APP_NAME}

@app.get("/api/identity")
def identity():
    try:
        ident = boto3.client("sts").get_caller_identity()
        return {"account_id":ident["Account"],"arn":ident["Arn"]}
    except Exception as exc:
        raise HTTPException(503, f"AWS identity unavailable: {type(exc).__name__}")

@app.get("/api/securityhub/standards")
def securityhub_standards(region: str):
    try:
        return {"region": region, "standards": list_securityhub_standards(boto3.Session(), region)}
    except ClientError as exc:
        code = exc.response.get("Error", {}).get("Code", "Unknown")
        raise HTTPException(502, f"Security Hub standards unavailable: {code}")

@app.post("/api/securityhub/enable")
def enable_securityhub(
    body: EnableSecurityHubRequest,
    admin_token: str | None = Header(default=None, alias="X-Admin-Token"),
):
    _require_securityhub_admin(admin_token)
    try:
        return enable_securityhub_region(boto3.Session(), body.region)
    except ClientError as exc:
        code = exc.response.get("Error", {}).get("Code", "Unknown")
        raise HTTPException(502, f"Security Hub activation failed: {code}")

@app.post("/api/securityhub/standards/enable")
def enable_standards(
    body: EnableStandardsRequest,
    admin_token: str | None = Header(default=None, alias="X-Admin-Token"),
):
    _require_securityhub_admin(admin_token)

    session = boto3.Session()
    for region in body.regions:
        try:
            available_arns = {
                item["standards_arn"] for item in list_securityhub_standards(session, region)
            }
        except ClientError as exc:
            code = exc.response.get("Error", {}).get("Code", "Unknown")
            raise HTTPException(502, f"Security Hub standards unavailable in {region}: {code}")
        if set(body.standards_arns) - available_arns:
            raise HTTPException(400, f"One or more standard ARNs are not available in {region}.")

    outcomes = []
    for region in body.regions:
        try:
            result = enable_securityhub_standards(session, region, body.standards_arns)
            has_errors = any(
                response.get("UnprocessedStandards") or response.get("Errors")
                for response in result.get("responses", [])
            )
            outcomes.append({
                **result,
                "status": "PARTIAL" if has_errors else "REQUESTED",
            })
        except ValueError as exc:
            raise HTTPException(400, str(exc))
        except ClientError as exc:
            code = exc.response.get("Error", {}).get("Code", "Unknown")
            outcomes.append({"region": region, "status": "ERROR", "error": code})
    has_errors = any(item["status"] in ("ERROR", "PARTIAL") for item in outcomes)
    return JSONResponse(
        status_code=207 if has_errors else 200,
        content={"regions": outcomes},
    )

@app.post("/api/audits", status_code=202)
def start_audit(body: AuditRequest, background: BackgroundTasks):
    background.add_task(do_scan, body.regions)
    return {"status":"accepted","message":"Audit started. Refresh audit history to see the report when complete."}

@app.get("/api/audits")
def audits():
    return list_audits()

@app.get("/api/audits/{audit_id}")
def audit_detail(audit_id: str):
    result = get_audit(audit_id)
    if not result: raise HTTPException(404,"Audit not found")
    return result

@app.get("/api/audits/{audit_id}/json")
def audit_json(audit_id: str):
    result = get_audit(audit_id)
    if not result: raise HTTPException(404,"Audit not found")
    return JSONResponse(result)

@app.get("/reports/{audit_id}", response_class=HTMLResponse)
def report(audit_id: str, request: Request):
    result = get_audit(audit_id)
    if not result: raise HTTPException(404,"Audit not found")
    result = prepare_report(result)
    return templates.TemplateResponse(
    request=request,
    name="report.html",
    context={
        "audit": result
    }
)
