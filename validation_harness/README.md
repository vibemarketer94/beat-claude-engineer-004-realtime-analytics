# Validation Harness

Run from `engineer-004-packet/`:

```bash
python3 validation_harness/run_validation.py validation_harness/sample_events.jsonl
```

The script uses only Python standard library modules.

## Cases

- `normal`: clean multi-tenant events pass.
- `messy`: duplicate and out-of-order events are detected; deduped parity still passes.
- `failure`: missing sequence and old/new parity mismatch fail the gate and require human review.

Exit code is `1` when any case fails. That is expected for the included sample because it includes the failure case.

