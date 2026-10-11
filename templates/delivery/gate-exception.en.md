---
template_name: gate-exception
template_version: 1
lifecycle_stages: [4, 5, 6]
traceability_fields:
  - record_id
  - record_type
  - status
  - owner
  - decision_authority
  - risk_level
  - related_records
  - source_version
  - environment_scope
  - evidence
  - created_at
  - updated_at
---

# Gate exception record

[中文](gate-exception.md)

## Traceability

- Record ID:
- Record type:
- Record status:
- Owner:
- Decision authority:
- Risk level:
- Related records:
- Source/artifact version:
- Environment and scope:
- Evidence:
- Created at with timezone:
- Updated at with timezone:

## Decision and limits

- rule_id and original rule permitting the exception:
- Gate node, actual object/scope and original check result:
- Authorizing person, identity verifier and traceable authorization source:
- Reason, remaining risk and permitted progression scope:
- Decision and expiry timestamps with timezones:
- Remediation task, owner and deadline:
- Revocation conditions, revalidation conditions and actual recheck record:

Apply the [gate standard](../../docs/quality-gates.md) (Chinese). Required documents, applicable translations, evidence, independence, existing required CI and human production/high-risk authorization cannot be waived. Author entry does not establish authority. A conditional conclusion preserves original failed results and does not automatically approve merging or release.
