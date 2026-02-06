# Test Plan

## Goal
Provide an automated, repeatable test suite that demonstrates correctness, error handling, and behavior under flaky conditions.

## Test strategy
- Automated tests implemented with `pytest`.
- Unit-style tests for deterministic endpoints: `/health`, `/process`.
- Integration-style tests for `/unstable` which simulate flaky behavior by patching randomness.

## What is automated vs manual
- Automated:
  - All test files under `tests/` (unit and integration style).
- Manual:
  - Live exploratory testing with `curl` or `httpie`.
  - Observing logs for debugging when reproducing incidents.

## Sample automated test cases
- `test_health_status_and_uptime`
  - Input: GET /health
  - Expect: 200, `status` == `OK`, `uptime_seconds` integer

- `test_process_valid`
  - Input: POST /process {"value": 3}
  - Expect: 200, `result` == 6

- `test_process_invalid_type`
  - Input: POST /process {"value": "x"}
  - Expect: 422

- `test_unstable_*`
  - Use monkeypatch to force deterministic outcomes:
    - success -> 200
    - exception -> 500
    - delay -> 504

## Handling flaky behavior in tests
- Make flaky endpoint deterministic in tests by patching `random.choice`.
- Keep retries/timeouts short in test environment so tests run fast.

## Notes
- Tests intentionally avoid external dependencies and the network.