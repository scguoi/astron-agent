"""
ApiService module for registering API services.
"""

from typing import Callable, Literal, Optional

from plugin.aitools.api.decorators.api_meta import ApiMeta, BodyT, QueryT, RespT
from plugin.aitools.common.exceptions.error.code_enums import CodeEnums
from plugin.aitools.common.exceptions.exceptions import ServiceException


def api_service(
    *,
    method: str,
    path: str,
    query: Optional[QueryT] = None,
    body: Optional[BodyT] = None,
    response: Optional[RespT] = None,
    summary: Optional[str] = None,
    description: Optional[str] = None,
    tags: Optional[
        Literal["public_cn", "public_global", "local", "intranet", "unclassified"]
    ] = "unclassified",
    deprecated: bool = False,
) -> Callable:
    """
    Declare an API service.
    """

    method = method.upper()

    if method not in {"GET", "POST", "PUT", "DELETE", "PATCH"}:
        raise ServiceException(f"Unsupported HTTP method: {method}")

    if not path.startswith("/"):
        raise ServiceException("API path must start with '/'")

    def decorator(func: Callable) -> Callable:
        # GET method does not support body
        if method == "GET" and body is not None:
            raise ServiceException.from_error_code(CodeEnums.RouteGetMethodParamsError)

        meta = ApiMeta(
            method=method,
            path=path,
            query=query,
            body=body,
            response=response,
            summary=summary,
            description=description,
            tags=tags,
            deprecated=deprecated,
        )

        # Bounding the meta to the function
        setattr(func, "__api_meta__", meta)

        return func

    return decorator
