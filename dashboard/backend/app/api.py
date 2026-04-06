from __future__ import annotations

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class ApiError(Exception):
    def __init__(self, error_code: str, message: str, status_code: int) -> None:
        self.error_code = error_code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


def success_response(data: object) -> dict[str, object]:
    return {"success": True, "data": data}


def error_response(error_code: str, message: str) -> dict[str, object]:
    return {
        "success": False,
        "error_code": error_code,
        "message": message,
    }


async def api_error_handler(_: Request, exc: ApiError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(error_code=exc.error_code, message=exc.message),
    )


async def validation_error_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    first_error = exc.errors()[0] if exc.errors() else {}
    message = first_error.get("msg", "Invalid request")
    return JSONResponse(
        status_code=422,
        content=error_response(error_code="VALIDATION_ERROR", message=message),
    )
