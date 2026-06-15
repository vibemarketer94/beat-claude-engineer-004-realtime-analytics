# Expected Output

The bundled sample intentionally includes one failing case, so the script exits with code `1`.

```text
FAIL case=failure input=3 unique=3 old_expected=4 parity_ok=False
  warning: missing_sequences=1
  warning: parity_mismatch old=4 new=3
  review: tenant_d:anon_5 missing [2]
  action: hold rollout and require human review
PASS case=messy input=4 unique=3 old_expected=3 parity_ok=True
  warning: duplicates=1
PASS case=normal input=4 unique=4 old_expected=4 parity_ok=True
OVERALL FAIL_REQUIRES_REVIEW
```

