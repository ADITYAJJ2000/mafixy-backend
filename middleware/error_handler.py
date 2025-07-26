from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from typing import Callable, Any
import logging
import traceback

logger = logging.getLogger(__name__)

class ErrorHandlerMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, request: Request, call_next: Callable) -> Response:
        try:
            response = await call_next(request)
            return response
        except HTTPException as e:
            logger.error(f"HTTP Exception: {str(e)}")
            return JSONResponse(
                status_code=e.status_code,
                content={"detail": str(e)}
            )
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}\n{traceback.format_exc()}")
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "An unexpected error occurred. Please try again later.",
                    "error_type": str(type(e).__name__)
                }
            )

def setup_error_handling(app):
    """Setup error handling middleware for the FastAPI app."""
    app.middleware('http')(ErrorHandlerMiddleware(app))
    
    # Add custom exception handlers
    @app.exception_handler(Exception)
    async def exception_handler(request: Request, exc: Exception):
        logger.error(f"Exception in {request.url.path}: {str(exc)}")
        return JSONResponse(
            status_code=500,
            content={
                "detail": "An unexpected error occurred. Please try again later.",
                "error_type": str(type(exc).__name__)
            }
        )
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        logger.error(f"HTTP Exception in {request.url.path}: {str(exc)}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": str(exc.detail)}
        )
