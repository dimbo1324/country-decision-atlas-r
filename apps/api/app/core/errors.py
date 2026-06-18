from fastapi import HTTPException
from typing import Any


def api_error(
    status_code: int,
    code: str,
    message: str,
    details: dict[str, Any] | list[Any] | None = None,
) -> HTTPException:
    return HTTPException(
        status_code=status_code,
        detail={
            "error": {
                "code": code,
                "message": message,
                "details": details if details is not None else {},
            }
        },
    )
