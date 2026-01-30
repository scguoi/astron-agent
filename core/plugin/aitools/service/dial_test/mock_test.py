"""
Test the mock service.
"""

# pylint: disable=unused-argument
import requests
from fastapi import Request
from plugin.aitools.api.decorators.api_service import api_service
from plugin.aitools.api.schemas.types import BaseResponse, SuccessResponse
from plugin.aitools.common.clients.aiohttp_client import HttpClient


@api_service(
    method="GET",
    path="/mock_async_test",
    summary="Async Mock test service",
    description="Health checks and service availability monitoring.",
    tags=["unclassified"],
    deprecated=True,
)
async def async_mock_test_service(
    request: Request,
) -> BaseResponse:
    """Async Mock test service"""
    client = HttpClient(method="GET", url="http://localhost:8086/ping")
    response = await client.request()
    # file_name = "test.txt"
    # file_bytes = response.data["content"].encode("utf-8")
    # url = await upload_file(file_name, file_bytes)
    return SuccessResponse(data={"content": response.data["content"]})


@api_service(
    method="GET",
    path="/mock_sync_test",
    summary="Sync Mock test service",
    description="Health checks and service availability monitoring.",
    tags=["unclassified"],
    deprecated=True,
)
def sync_mock_test_service(
    request: Request,
) -> BaseResponse:
    """Sync Mock test service"""
    response = requests.get("http://localhost:8086/ping", timeout=10)
    # file_name = "test.txt"
    # file_bytes = response.content
    # oss_service = get_oss_service()
    # url = oss_service.upload_file(file_name, file_bytes)
    return SuccessResponse(data={"content": response.content.decode("utf-8")})
