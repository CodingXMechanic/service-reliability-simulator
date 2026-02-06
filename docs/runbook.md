# Runbook

## Purpose
Guidance for support engineers to debug and recover the service quickly.

## Common failure scenarios
1. `/unstable` returning 500 frequently (transient exceptions)
2. `/unstable` returning 504 (timeout) repeatedly
3. Service not reachable or failing on startup

## Quick checks (first 2 minutes)
1. Confirm the process is running:
   - `ps aux | grep uvicorn` or check systemd service if deployed
2. Check logs: `tail -n 200 logs/service.log`
   - Look for JSON entries with `level: ERROR` and `endpoint` keys

## Step-by-step debugging
### 1. Frequent 500s on `/unstable`
- Check logs for "operation failed" with `error_reason`.
- If logs show "simulated transient failure", likely the transient exception path is frequent.
- Recovery options:
  - Investigate how often `random.choice` picks exception (test-only cause); in production the same code might wrap a real remote call.
  - If this was a real dependency, consider adding circuit breakers or increase retry/backoff.

### 2. 504 timeouts at `/unstable`
- Look for "operation timed out" in logs.
- Root cause may be slow downstream operations or a too-short timeout value.
- Recovery:
  - Increase timeout temporarily (if safe) or investigate downstream slowness.
  - For this demo service: reduce heavy work, or tune retry/backoff.

### 3. Service not starting
- Look at logs for startup messages.
- Ensure `logs/` directory is writable by the process.
- Permissions issues often surface as errors when the logger cannot open a file.

## Example incident + RCA (short)
- Symptom: `/unstable` 504s spike for 10 minutes.
- Investigation: logs show many "operation timed out". No other system events.
- Root cause: downstream dependency began responding slowly — for our demo this is simulated by `delay` path being hit often.
- Mitigation: increased timeout + improved retries; added a circuit breaker in planned improvements.