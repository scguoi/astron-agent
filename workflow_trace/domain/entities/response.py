from typing import Any

from fastapi.responses import JSONResponse


class Resp:
    @staticmethod
    def success(data: Any = None) -> JSONResponse:
        payload = {"code": 0, "message": "success"}
        if data is not None:
            payload["data"] = data
        return JSONResponse(content=payload)

    @staticmethod
    def error(code: int, message: str) -> JSONResponse:
        return JSONResponse(content={"code": code, "message": message})
