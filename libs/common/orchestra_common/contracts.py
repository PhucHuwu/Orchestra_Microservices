from pydantic import BaseModel


class Envelope(BaseModel):
    success: bool
    data: dict | list | None = None
    error_code: str | None = None
    message: str | None = None
