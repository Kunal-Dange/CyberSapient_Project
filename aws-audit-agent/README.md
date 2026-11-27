# AWS Account Audit Agent

A read-only-by-default, extensible AWS account security auditor. It scans one AWS account across enabled regions, collects active Security Hub findings and discovered standards, evaluates built-in deterministic controls, and produces a self-contained HTML report. Standard activation is a separate, explicit, token-gated operation.

## Features

- FastAPI web UI and API
- AWS identity and enabled-region discovery
- Plugin registry with initial IAM, EC2, S3, CloudTrail, Security Hub and AWS Config collectors
- Deterministic controls; no LLM decides pass/fail
- Findings include severity, resource, evidence source and remediation
- Security Hub standards discovery and active findings across scanned regions
- Client-oriented HTML reports with a transparent built-in check score, coverage tables and charts
- HTML report and JSON output
- SQLite audit history
- Read-only AWS access during audits; optional explicit Security Hub standard activation
- Docker packaging

## Requirements

- Python 3.12+
- AWS credentials supplied through the standard AWS credential chain
- Read-only IAM permissions for scans (start with AWS managed `SecurityAudit`; validate and add only required read actions)
- Network access to AWS APIs

Do not use root credentials or embed long-lived access keys in the application.

## Run locally

```bash
cd audit_agent
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
aws sts get-caller-identity      # verify the intended identity
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Open http://127.0.0.1:8000.

The application uses the default Boto3 credential chain (environment, shared profile, SSO, instance/task role). For a named profile:

```bash
AWS_PROFILE=my-audit-profile uvicorn app.main:app --host 127.0.0.1 --port 8000
```

## Run with Docker

```bash
docker compose up --build
```

Mount credentials read-only if using a local profile, or preferably run the container on AWS with an ECS task role / EC2 instance profile:

```bash
docker run --rm -p 8000:8000 \
  -e AWS_REGION=ap-south-1 \
  -v "$HOME/.aws:/home/app/.aws:ro" \
  aws-account-audit-agent:local
```

Never expose port 8000 publicly without authentication and TLS.

## Audit API

- `GET /api/health`
- `GET /api/identity` - shows the caller identity (account ID and ARN only)
- `POST /api/audits` - starts a scan; optional JSON body `{"regions": ["ap-south-1"], "include_global": true}`
- `GET /api/securityhub/standards?region=ap-south-1` - lists standards available and enabled in a region
- `POST /api/securityhub/enable` - explicitly enables Security Hub in a region
- `POST /api/securityhub/standards/enable` - explicitly enables selected standards in one or more regions
- `GET /api/audits` - list recent scans
- `GET /api/audits/{audit_id}` - audit status and summary
- `GET /reports/{audit_id}` - rendered HTML report
- `GET /api/audits/{audit_id}/json` - raw JSON result

Example:

```bash
curl -X POST http://127.0.0.1:8000/api/audits \
  -H 'Content-Type: application/json' \
  -d '{"regions":["ap-south-1"],"include_global":true}'
```

The scan runs as a FastAPI background task. For production workloads, move long-running jobs to SQS/Celery/Step Functions and use a durable job store.

Audits do not change AWS configuration. Security Hub and standard activation are separate operations and are disabled unless a strong `SECURITY_HUB_ADMIN_TOKEN` is configured. The activation endpoints require the `X-Admin-Token` header and an authorized AWS identity with appropriate Security Hub write permissions. Review current AWS pricing before activation. The app has no general user authentication; protect every route behind an authenticated, authorized proxy before team or client use.

## Current control coverage

This is a starter implementation, not exhaustive AWS coverage. The implemented controls include:

| ID | Service | Check |
|---|---|---|
| IAM-001 | IAM | Root account access key present |
| IAM-002 | IAM | Root MFA enabled |
| IAM-003 | IAM | Account password policy configured |
| EC2-001 | EC2 | Security group permits unrestricted SSH |
| EC2-002 | EC2 | Security group permits unrestricted RDP |
| EC2-003 | EC2 | EBS volume encryption |
| EC2-004 | EC2 | Instance metadata options require IMDSv2 |
| S3-001 | S3 | Account-level Block Public Access |
| S3-002 | S3 | Bucket-level Block Public Access |
| S3-003 | S3 | Default bucket encryption |
| CT-001 | CloudTrail | Multi-region trail enabled |
| SH-001 | Security Hub | Security Hub enabled in region |
| CFG-001 | AWS Config | Configuration recorder present and recording |

Controls are deliberately conservative. `UNKNOWN` means evidence could not be collected; it is not a pass. `NOT_APPLICABLE` means the control did not apply to discovered resources. A service not found is not proof that the service is unused or compliant.

## Extending the auditor

1. Add a collector under `app/plugins/`.
2. Implement `collect(context) -> list[Evidence]`.
3. Register the plugin in `app/plugins/__init__.py`.
4. Add deterministic evaluators under `app/controls/`.
5. Add control metadata and framework mappings in `app/controls/catalog.py`.
6. Add unit tests with mocked Boto3 clients.

The shared `AuditContext` carries account ID, regions and a Boto3 session. Later, a multi-account runner can create one context per account using `sts:AssumeRole`; the plugins and control engine need not be rewritten.

## Team deployment recommendation

For a team, deploy one private instance (for example, ECS Fargate behind an internal Application Load Balancer). Use:
- ECS task role with read-only audit permissions
- Internal ALB with HTTPS
- ALB OIDC authentication integrated with your company identity provider / IAM Identity Center-compatible federation
- Network access restricted to VPN or corporate network
- Centralized logs, encrypted report storage, backups and retention
- Per-user audit attribution at the authenticated proxy / identity layer

The starter app intentionally does not implement its own user/password database. Do not make it internet-facing until authentication, authorization, CSRF protections, rate limits and secure report access are configured. SQLite is for local MVP only; use RDS/Aurora or DynamoDB and private S3 report storage for shared production use.

## Standards and interpretation

The control metadata references AWS Foundational Security Best Practices (FSBP), CIS AWS Foundations Benchmark and AWS Well-Architected Security Pillar where appropriate. Framework mappings are pointers, not a claim of certification. Some framework requirements need manual evidence and are not automated here.

Useful official references:
- AWS SecurityAudit managed policy: https://docs.aws.amazon.com/aws-managed-policy/latest/reference/SecurityAudit.html
- AWS Security Hub FSBP: https://docs.aws.amazon.com/securityhub/latest/userguide/fsbp-standard.html
- CIS AWS Foundations in Security Hub: https://docs.aws.amazon.com/securityhub/latest/userguide/cis-aws-foundations-benchmark.html
- AWS Well-Architected Security Pillar: https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/welcome.html
- Boto3: https://boto3.amazonaws.com/v1/documentation/api/latest/index.html

## Limitations

- Scans only implemented controls and configured regions.
- Some account-global services and opt-in regions have special behavior.
- AWS API permission gaps are reported as collection errors / unknowns.
- No operating-system-level inspection, penetration testing, policy enforcement or auto-remediation.
- Findings and score are posture indicators, not legal compliance certification.
- AWS Security Hub findings and standards depend on regional enablement, permissions, and the standards configured in the account; this app does not discover or evaluate every AWS service or every benchmark control.


## Expanded development phase

The current code additionally discovers and evaluates selected controls for:
- Networking: VPC inventory and VPC Flow Logs
- RDS/Aurora: public accessibility, storage encryption, deletion protection and backup retention
- Lambda: X-Ray tracing posture (operational recommendation)
- KMS: automatic rotation for eligible customer-managed symmetric keys
- ECR: scan-on-push and immutable tags
- DynamoDB: point-in-time recovery
- Organizations: organization membership metadata

The framework mappings in `app/controls/catalog.py` are broad references to FSBP, CIS AWS Foundations and the Well-Architected Security Pillar. They are not an assertion that all requirements in those standards are covered. Exact benchmark IDs and versions should be verified against the version adopted by your organization.

The report's built-in score is `PASS / (PASS + FAIL)` across this application's deterministic checks. `UNKNOWN` and `NOT_APPLICABLE` are excluded. It is not AWS Security Hub's score or a complete benchmark score. Security Hub findings are reported separately from this score. The report lists discovered standards, their enabled regions, and collector errors so that scope gaps are visible.

### Local access mode

The application is intended to bind to `127.0.0.1` for this phase. It has no built-in user authentication. Do not bind to `0.0.0.0`, expose it on a LAN, or share the URL beyond the local machine until an authentication layer and authorization model are implemented.


## Tests

Install test tooling and run the evaluator unit tests:

```bash
pip install pytest
pytest -q
```

The test suite currently exercises deterministic security-group evaluation. Expand it with mocked client responses for each plugin before production deployment.
