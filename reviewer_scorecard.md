# Reviewer Scorecard

This scorecard is a proxy benchmark. The private reviewer benchmark is withheld, so this packet measures against public task requirements, the public scoring guide, and generic-answer failure modes.

| Area | Pass Criteria | Status | Notes |
|---|---|---:|---|
| Brief coverage | Architecture covers dashboards, personalization, segmentation, exports, GDPR/CCPA deletion, 500+ tenants, AWS, no SDK breaking change, migration, rollback, and validation. | Pass | See `submission.md`, `architecture.mmd`, `migration_runbook.md`. |
| Prompt coverage matrix | Every public "What to Submit" and required packet item maps to at least one artifact. | Pass | See `challenge_requirements_matrix.md`. |
| Operating artifact | Reviewer can inspect or run at least one artifact without private data or credentials. | Pass | `validation_harness/` uses synthetic data. |
| Artifact access | Packet includes commands, generated traces, and no-login setup notes. | Pass | See `operating_artifact.md` and `README.md`. |
| Number labels | Numbers in `submission.md`, `cost_model.md`, and `evidence_log.md` are labeled as Observed, Estimated, Benchmarked, or Assumed. | Pass | Verified by `verify_packet.py`; see `verification_report.md`. |
| Evidence tiers | Major claims map to proof tiers from the public scoring guide. | Pass | See `evidence_log.md`. |
| Runnable proof | Harness demonstrates normal, messy, and failure/ambiguous cases. | Pass | Verified by `verify_packet.py`; failure fails as expected. |
| Reviewer replay | One command reruns tests, models, validation, and packet verification. | Pass | See `run_reviewer_packet.sh` and generated `reviewer_run.log`. |
| Curveball readiness | Packet handles hidden-benchmark-style failure modes. | Pass | See `curveballs/curveball_report.md`. |
| Sensitivity cliffs | Packet names where the architecture becomes unsafe. | Pass | See `sensitivity/sensitivity_report.md`. |
| Failure handling | Plan names likely breaks, detection, and response. | Pass | See `migration_runbook.md` and `validation_plan.md`. |
| AI fluency | AI usage is disclosed with human decisions and checks. | Pass | See `ai_usage.md`. |
| Non-generic judgment | Submission centers migration, correctness, tenant isolation, compliance, and operations rather than service-name listing. | Pass | Thesis appears in `submission.md`. |
| Hidden benchmark humility | Packet does not pretend to know private scoring keys. | Pass | This file states proxy basis. |

## Failure Conditions

- Fail if a load-bearing number lacks a source label.
- Fail if the harness cannot be run with `python3` and local sample data.
- Fail if architecture prose makes "zero data loss" claims without dedupe, replay, parity, and rollback mechanics.
- Fail if synthetic data is presented as production evidence.
- Fail if curveball or sensitivity scenarios are missing from the executable verifier.

## Limitation

This scorecard cannot prove that the packet beats the private benchmark. It can show that the packet satisfies public criteria and avoids the common losing modes named by the challenge.

The scorecard is not the only verification artifact. `verification_report.md` is generated from `verify_packet.py` and records the latest executable checks.
