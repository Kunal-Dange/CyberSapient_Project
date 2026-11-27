from app.models import Finding, Evidence
from app.controls.catalog import CONTROL_CATALOG

def _finding(cid, status, evidence=None, resource="account", region=None, detail=None):
    c = CONTROL_CATALOG[cid]
    return Finding(control_id=cid, title=c["title"], service=c["service"],
        severity=c["severity"], status=status, description=detail or c["description"],
        resource_id=resource, region=region,
        evidence=[e.model_dump(mode="json") for e in (evidence or [])],
        remediation=c["remediation"], frameworks=c["frameworks"],
        confidence="high" if evidence else "low")

def evaluate(evidence: list[Evidence]) -> list[Finding]:
    findings = []
    by_service = {}
    for e in evidence:
        by_service.setdefault(e.service, []).append(e)

    iam = by_service.get("iam", [])
    summary = next((e for e in iam if e.resource_type == "account"), None)
    if summary:
        findings.append(_finding("IAM-001", "FAIL" if summary.data.get("AccountAccessKeysPresent", 0) else "PASS", [summary]))
        findings.append(_finding("IAM-002", "PASS" if summary.data.get("AccountMFAEnabled", 0) else "FAIL", [summary]))
    else:
        findings.extend([_finding("IAM-001","UNKNOWN"), _finding("IAM-002","UNKNOWN")])
    pwd = next((e for e in iam if e.evidence_id == "iam:password-policy"), None)
    findings.append(_finding("IAM-003", "UNKNOWN" if not pwd else ("PASS" if pwd.data.get("policy_present") else "FAIL"), [pwd] if pwd else []))

    ec2 = by_service.get("ec2", [])
    for e in [x for x in ec2 if x.resource_type == "security-group"]:
        for cid, port in (("EC2-001",22),("EC2-002",3389)):
            exposed = False
            for perm in e.data.get("ingress", []):
                proto = perm.get("IpProtocol")
                fp, tp = perm.get("FromPort"), perm.get("ToPort")
                if proto == "-1" or (fp is not None and tp is not None and fp <= port <= tp):
                    if any(r.get("CidrIp") == "0.0.0.0/0" for r in perm.get("IpRanges", [])) or any(r.get("CidrIpv6") == "::/0" for r in perm.get("Ipv6Ranges", [])):
                        exposed = True
            findings.append(_finding(cid, "FAIL" if exposed else "PASS", [e], e.resource_id, e.region))
    volumes = [x for x in ec2 if x.resource_type == "ebs-volume"]
    for e in volumes:
        findings.append(_finding("EC2-003","PASS" if e.data.get("encrypted") else "FAIL",[e],e.resource_id,e.region))
    instances = [x for x in ec2 if x.resource_type == "instance"]
    for e in instances:
        findings.append(_finding("EC2-004","PASS" if e.data.get("http_tokens") == "required" else "FAIL",[e],e.resource_id,e.region))
    if not any(x.resource_type == "security-group" for x in ec2):
        findings.extend([_finding("EC2-001","NOT_APPLICABLE"),_finding("EC2-002","NOT_APPLICABLE")])
    if not volumes: findings.append(_finding("EC2-003","NOT_APPLICABLE"))
    if not instances: findings.append(_finding("EC2-004","NOT_APPLICABLE"))

    s3 = by_service.get("s3", [])
    acct = next((x for x in s3 if x.resource_type == "account"), None)
    if acct:
        block = acct.data.get("block", {})
        ok = all(block.get(k, False) for k in ("BlockPublicAcls","IgnorePublicAcls","BlockPublicPolicy","RestrictPublicBuckets"))
        findings.append(_finding("S3-001","UNKNOWN" if acct.data.get("error") else ("PASS" if ok else "FAIL"),[acct]))
    else:
        findings.append(_finding("S3-001","UNKNOWN"))
    buckets = [x for x in s3 if x.resource_type == "bucket"]
    for e in buckets:
        pab = e.data.get("public_access_block", {})
        ok = all(pab.get(k, False) for k in ("BlockPublicAcls","IgnorePublicAcls","BlockPublicPolicy","RestrictPublicBuckets"))
        findings.append(_finding("S3-002","PASS" if ok else ("UNKNOWN" if e.data.get("public_access_block_error") else "FAIL"),[e],e.resource_id))
        enc = bool(e.data.get("encryption"))
        findings.append(_finding("S3-003","PASS" if enc else ("UNKNOWN" if e.data.get("encryption_error") else "FAIL"),[e],e.resource_id))
    if not buckets:
        findings.extend([_finding("S3-002","NOT_APPLICABLE"),_finding("S3-003","NOT_APPLICABLE")])

    trails = by_service.get("cloudtrail", [])
    multi = [e for e in trails if e.data.get("is_multi_region") and e.data.get("is_logging")]
    findings.append(_finding("CT-001","PASS" if multi else ("FAIL" if trails else "UNKNOWN"),multi or trails[:3]))

    sh = by_service.get("securityhub", [])
    sh_regions = {e.region for e in sh if e.resource_type == "regional-service" and e.data.get("enabled")}
    for region in sorted({e.region for e in sh if e.resource_type == "regional-service"}):
        e = next(x for x in sh if x.resource_type == "regional-service" and x.region == region)
        if e.data.get("collection_error"):
            status = "UNKNOWN"
        elif e.data.get("enabled") is None:
            status = "UNKNOWN"
        else:
            status = "PASS" if e.data.get("enabled") else "FAIL"
        findings.append(_finding("SH-001", status, [e], region=region))
    if not sh:
        findings.append(_finding("SH-001","UNKNOWN"))

    cfg = by_service.get("config", [])
    if cfg:
        for e in [x for x in cfg if x.resource_type == "regional-service"]:
            active = any(s.get("recording") for s in e.data.get("statuses", []))
            findings.append(_finding("CFG-001","PASS" if active else ("UNKNOWN" if e.data.get("error") else "FAIL"),[e],region=e.region))
    else:
        findings.append(_finding("CFG-001","UNKNOWN"))



    # RDS instances and Aurora clusters
    rds_items = by_service.get("rds", [])
    for e in [x for x in rds_items if x.resource_type in ("db-instance", "db-cluster")]:
        d = e.data
        if e.resource_type == "db-instance":
            findings.append(_finding("RDS-001", "FAIL" if d.get("publicly_accessible") else "PASS", [e], e.resource_id, e.region))
            findings.append(_finding("RDS-002", "PASS" if d.get("storage_encrypted") else "FAIL", [e], e.resource_id, e.region))
            findings.append(_finding("RDS-003", "PASS" if d.get("deletion_protection") else "FAIL", [e], e.resource_id, e.region))
            findings.append(_finding("RDS-004", "PASS" if d.get("backup_retention_period", 0) > 0 else "FAIL", [e], e.resource_id, e.region))
        else:
            findings.append(_finding("RDS-002", "PASS" if d.get("storage_encrypted") else "FAIL", [e], e.resource_id, e.region))
            findings.append(_finding("RDS-003", "PASS" if d.get("deletion_protection") else "FAIL", [e], e.resource_id, e.region))
            findings.append(_finding("RDS-004", "PASS" if d.get("backup_retention_period", 0) > 0 else "FAIL", [e], e.resource_id, e.region))
    if not rds_items:
        for cid in ("RDS-001","RDS-002","RDS-003","RDS-004"):
            findings.append(_finding(cid, "NOT_APPLICABLE"))

    # Network telemetry: map flow logs to each VPC. Missing telemetry remains FAIL
    # only when VPC discovery completed; failed collection is surfaced by plugin status.
    net_items = by_service.get("networking", [])
    vpcs = [x for x in net_items if x.resource_type == "vpc"]
    flowlogs = [x for x in net_items if x.resource_type == "flow-log"]
    logged_vpcs = {rid for fl in flowlogs if fl.data.get("status") == "ACTIVE" for rid in fl.data.get("resource_ids", [])}
    for vpc in vpcs:
        findings.append(_finding("NET-001", "PASS" if vpc.resource_id in logged_vpcs else "FAIL", [vpc] + [x for x in flowlogs if vpc.resource_id in x.data.get("resource_ids", [])], vpc.resource_id, vpc.region))
    if not vpcs:
        findings.append(_finding("NET-001", "NOT_APPLICABLE"))

    # Lambda X-Ray tracing is an operational recommendation, not a universal security mandate.
    lambda_items = [x for x in by_service.get("lambda", []) if x.resource_type == "function"]
    for e in lambda_items:
        findings.append(_finding("LAMBDA-001", "PASS" if e.data.get("tracing_mode") == "Active" else "FAIL", [e], e.resource_id, e.region))
    if not lambda_items:
        findings.append(_finding("LAMBDA-001", "NOT_APPLICABLE"))

    # Rotation is evaluated only where the API returns an applicable boolean.
    kms_items = [x for x in by_service.get("kms", []) if x.resource_type == "customer-managed-key"]
    for e in kms_items:
        rotation = e.data.get("rotation_enabled")
        if rotation is not None:
            findings.append(_finding("KMS-001", "PASS" if rotation else "FAIL", [e], e.resource_id, e.region))
    if not kms_items:
        findings.append(_finding("KMS-001", "NOT_APPLICABLE"))

    ecr_items = [x for x in by_service.get("containers", []) if x.resource_type == "ecr-repository"]
    for e in ecr_items:
        findings.append(_finding("ECR-001", "PASS" if e.data.get("scan_on_push") else "FAIL", [e], e.resource_id, e.region))
        findings.append(_finding("ECR-002", "PASS" if e.data.get("tag_mutability") == "IMMUTABLE" else "FAIL", [e], e.resource_id, e.region))
    if not ecr_items:
        findings.extend([_finding("ECR-001","NOT_APPLICABLE"),_finding("ECR-002","NOT_APPLICABLE")])

    ddb_items = [x for x in by_service.get("dynamodb", []) if x.resource_type == "table"]
    for e in ddb_items:
        findings.append(_finding("DDB-001", "PASS" if e.data.get("point_in_time_recovery") == "ENABLED" else "FAIL", [e], e.resource_id, e.region))
    if not ddb_items:
        findings.append(_finding("DDB-001", "NOT_APPLICABLE"))

    return findings
