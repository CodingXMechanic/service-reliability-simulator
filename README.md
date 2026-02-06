# Service Reliability & Testing Simulator

A compact, interview-friendly backend that demonstrates reliability: structured logging, graceful error handling, retries, timeouts, and a test suite.

## What this project demonstrates
- Service reliability basics (timeouts, retries)
- Structured, readable logs for debugging
- Clear error handling and safe client responses
- Deterministic testing of flaky behavior

## Tech stack & constraints
- Python + FastAPI
- pytest for tests
- Python `logging` module (structured JSON-line format)
- No external databases, cloud services, Docker, or heavy dependencies

## Run locally

1. Create a venv and install:
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt