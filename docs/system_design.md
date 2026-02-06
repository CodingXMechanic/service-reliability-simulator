# System Design Notes

## Overview
Service is a small single-process FastAPI app that demonstrates:
- structured logging
- reliable error handling
- retry + timeout behavior
- test-driven validation of flaky endpoints

## Architecture
- `main.py` boots FastAPI and sets global start_time.
- `routes.py` contains endpoints and orchestrates retries/timeouts.
- `utils.py` contains small helpers: processing logic and the async retry helper.
- `logger.py` configures structured JSON logging into `logs/service.log`.

## Error handling approach
- Centralized global exception handler returns safe 500 responses and logs the error.
- Endpoints explicitly catch expected errors (e.g., timeouts) and map them to meaningful HTTP statuses (504 for timeout).
- Input validated by Pydantic, validation failures return 422.

## Observability
- Logs are JSON-lines with `timestamp`, `level`, `endpoint`, `message`, and `error_reason`.
- Every request logs an entry at minimum; failures and retries are logged with clear reasons.

## Reliability decisions
- Retries are implemented at the operation level using a small `retry_async`.
- Timeouts are applied using `asyncio.wait_for` so slow operations can be bounded.
- These choices are minimal but clearly show the techniques you’d explain in interviews.

## What to improve at scale (brief)
- Use centralized log aggregation (ELK/CloudWatch) instead of local file.
- Replace custom retry with a robust library or client-side retries for real downstream calls.
- Add circuit breaker pattern to avoid retry storms.
- Add health checks for downstream dependencies and readiness probes.
- Containerize and add CI/CD with testing and linting.