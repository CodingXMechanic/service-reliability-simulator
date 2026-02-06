# app/main.py
import time
import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from .routes import router
from .logger import logger

app = FastAPI(title="Service Reliability & Testing Simulator")

# record start_time using event loop time for monotonicity
@app.on_event("startup")
async def startup_event():
    # store a monotonic start time (using event loop)
    app.state.start_time = asyncio.get_event_loop().time()
    logger.info("service startup", extra={"endpoint": "startup"})


app.include_router(router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Catches all unhandled exceptions, logs them, and returns a safe message.
    Avoid returning raw traceback to clients.
    """
    logger.error("unhandled exception", extra={"endpoint": request.url.path, "error_reason": str(exc)})
    # Provide a safe, non-sensitive message
    return JSONResponse(status_code=500, content={"detail": "internal server error"})