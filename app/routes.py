# app/routes.py
import asyncio
import random
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, ValidationError
from starlette.responses import JSONResponse
from .logger import logger
from .utils import process_value, retry_async

router = APIRouter()


class ProcessRequest(BaseModel):
    value: float


from time import time
from fastapi import Request

@router.get("/health")
async def health(request: Request):
    # Defensive initialization for test environments
    if not hasattr(request.app.state, "start_time"):
        request.app.state.start_time = time()

    start_time = request.app.state.start_time
    uptime = int(time() - start_time)

    logger.info("health check", extra={"endpoint": "/health"})

    return {
        "status": "OK",
        "uptime_seconds": uptime
    }



@router.post("/process")
async def process_endpoint(payload: ProcessRequest, request: Request):
    """
    Process a number. Validates input via Pydantic.
    Logs request, validation failures, and success.
    """
    logger.info("request received", extra={"endpoint": "/process", "message": f"payload={payload.dict()}"})
    try:
        result = await process_value(payload.value)
        logger.info("success response", extra={"endpoint": "/process", "message": f"result={result}"})
        return JSONResponse(content=result)
    except ValidationError as ve:
        logger.warning("validation failure", extra={"endpoint": "/process", "error_reason": str(ve)})
        raise HTTPException(status_code=422, detail="Invalid input")


async def _unstable_operation() -> dict:
    """
    Internal operation that randomly:
    - succeeds
    - raises an exception
    - sleeps (simulates slowness)
    Keep the function small so we can easily reason and test retries/timeouts.
    """
    choice = random.choice(["success", "exception", "delay"])
    logger.info("unstable choice", extra={"endpoint": "/unstable", "message": f"choice={choice}"})
    if choice == "success":
        return {"status": "ok", "detail": "operation completed"}
    if choice == "exception":
        # Simulated transient error
        raise RuntimeError("simulated transient failure")
    # simulate slow operation (delay)
    await asyncio.sleep(5)  # long running operation that will likely time out
    return {"status": "ok", "detail": "delayed operation completed"}


@router.get("/unstable")
async def unstable(request: Request):
    """
    Endpoint that simulates flaky behavior:
    - Uses retry_async around a time-limited call (asyncio.wait_for) to simulate timeouts.
    - Logs every failure clearly.
    """
    logger.info("request received", extra={"endpoint": "/unstable"})
    # We'll wrap the unstable operation with asyncio.wait_for to simulate a timeout.
    async def timed_action():
        # small timeout so delay path will raise TimeoutError
        return await asyncio.wait_for(_unstable_operation(), timeout=1.0)

    try:
        result = await retry_async(timed_action, max_retries=2, backoff_seconds=0.2)
        logger.info("unstable success", extra={"endpoint": "/unstable", "message": str(result)})
        return JSONResponse(content=result)
    except asyncio.TimeoutError as te:
        logger.error("operation timed out", extra={"endpoint": "/unstable", "error_reason": str(te)})
        # 504 Gateway Timeout is a suitable signal for internal timeout
        raise HTTPException(status_code=504, detail="operation timed out")
    except Exception as exc:
        logger.error("operation failed", extra={"endpoint": "/unstable", "error_reason": str(exc)})
        raise HTTPException(status_code=500, detail="internal failure")