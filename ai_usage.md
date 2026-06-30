# AI Usage Disclosure

## Tools Used

- ChatGPT/Codex for brainstorming, packet planning, drafting, and critique.
- Web research for current public AWS pricing and quota source links.
- Local Python harnesses for synthetic validation, before/after benchmarking, curveball scenarios, sensitivity modeling, and packet verification.
- Test-driven development for the curveball and sensitivity scripts: tests were written and run before implementation.

## What AI Helped With

- Structuring the packet around the public scoring guide.
- Drafting first-pass architecture and operating artifacts.
- Generating synthetic test cases for validation.
- Generating hidden-benchmark-style curveball scenarios and scale/cost sensitivity cliffs.
- Creating the one-command reviewer replay script and verification report checks.
- Finding gaps where a generic answer would be weak.

## Human Decisions

- Centered the answer on migration, correctness, tenant isolation, compliance, and operations.
- Chose a narrow validation harness instead of a fake production pipeline.
- Treated hidden benchmark scoring as unknowable and used a public proxy scorecard.
- Kept confidential data out of the packet.

## What Was Checked

- Public brief and scoring guide coverage.
- AWS source links for pricing and quotas.
- Validation harness output against normal, messy, and failure cases.
- Before/after benchmark tests, curveball tests, sensitivity tests, model generation, and reviewer replay output.
- Number labels and evidence-tier mapping.
- That the reviewer replay reproduces in a clean environment: GitHub Actions runs `./run_reviewer_packet.sh` on every push and is green.

## Known Weak Spots

- The cost model is a planning model, not an AWS quote.
- The validation harness uses synthetic data.
- The curveball and sensitivity artifacts are synthetic operating evidence, not production incidents or load tests.
- The replay is reproduced by CI (GitHub Actions), but no external human or customer has verified the result, so no Tier 5 human verification is claimed.
- The architecture assumes AWS regions and account limits that must be verified before production buildout.
