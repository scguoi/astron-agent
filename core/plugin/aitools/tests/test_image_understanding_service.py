"""
Unit tests for image understanding service.
"""

# pylint: disable=redefined-outer-name,unused-argument,line-too-long
import json
from typing import AsyncIterator, Iterator, Tuple
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import Request
from plugin.aitools.api.schemas.types import SuccessResponse
from plugin.aitools.common.exceptions.error.code_enums import CodeEnums
from plugin.aitools.common.exceptions.exceptions import ServiceException
from plugin.aitools.service.image_understanding.image_understanding_service import (
    ImageUnderstandingRequest,
    image_understanding_service,
)


def build_ws_message(
    *,
    code: int = 0,
    sid: str = "test-sid",
    message: str = "ok",
    content: str = "",
    status: int = 1,
) -> str:
    """Build a WebSocket message JSON string"""
    return json.dumps(
        {
            "header": {
                "code": code,
                "sid": sid,
                "message": message,
            },
            "payload": {
                "choices": {
                    "status": status,
                    "text": [{"content": content}],
                }
            },
        }
    )


async def async_gen(messages: list[str]) -> AsyncIterator[str]:
    """Async generator for websocket recv"""
    for msg in messages:
        yield msg


@pytest.fixture
def mock_request() -> MagicMock:
    """Mock request fixture"""
    request = MagicMock(spec=Request)
    request.state = MagicMock()
    request.state.sid = None
    return request


@pytest.fixture(autouse=True)
def mock_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mock environment variables"""
    monkeypatch.setenv("IMAGE_UNDERSTANDING_URL", "ws://fake-ws")
    monkeypatch.setenv("AI_APP_ID", "app-id")
    monkeypatch.setenv("AI_API_KEY", "api-key")
    monkeypatch.setenv("AI_API_SECRET", "api-secret")


@pytest.fixture
def mock_http_client() -> Iterator[Tuple[MagicMock | AsyncMock, AsyncMock]]:
    """Mock HttpClient used for downloading image."""
    with patch(
        "plugin.aitools.service.image_understanding.image_understanding_service.HttpClient"
    ) as http_cls:
        client = AsyncMock()
        client.request.return_value = MagicMock(data={"content": b"fake-image-bytes"})
        http_cls.return_value.start.return_value.__aenter__.return_value = client
        yield http_cls, client


@pytest.fixture
def mock_ws_client() -> Iterator[Tuple[MagicMock | AsyncMock, MagicMock]]:
    """Mock WebSocketClient used for communicating with image understanding service."""
    with patch(
        "plugin.aitools.service.image_understanding.image_understanding_service.WebSocketClient"
    ) as ws_cls:
        ws = MagicMock()

        ws.send = AsyncMock()
        ws.recv = MagicMock(return_value=async_gen([]))

        ws_cls.return_value.start.return_value.__aenter__.return_value = ws
        yield ws_cls, ws


class TestImageUnderstandingService:
    """Image Understanding Service tests"""

    @pytest.mark.asyncio
    async def test_image_understanding_success(
        self,
        mock_http_client: Tuple[MagicMock | AsyncMock, AsyncMock],
        mock_ws_client: Tuple[MagicMock | AsyncMock, MagicMock],
        mock_request: MagicMock,
    ) -> None:
        """Success: stream answer concatenated"""
        _, ws = mock_ws_client

        ws.recv.return_value = async_gen(
            [
                build_ws_message(content="Hello ", status=1),
                build_ws_message(content="World", status=2),
            ]
        )

        body = ImageUnderstandingRequest(
            question="What is in the image?",
            image_url="http://fake-image.jpg",
        )

        resp = await image_understanding_service(
            body=body,
            request=mock_request,
        )

        assert isinstance(resp, SuccessResponse)
        assert resp.data["content"] == "Hello World"
        assert mock_request.state.sid is None

    @pytest.mark.asyncio
    async def test_image_understanding_ws_error(
        self,
        mock_http_client: Tuple[MagicMock | AsyncMock, AsyncMock],
        mock_ws_client: Tuple[MagicMock | AsyncMock, MagicMock],
        mock_request: MagicMock,
    ) -> None:
        """WebSocket returns error code"""
        _, ws = mock_ws_client

        ws.recv.return_value = async_gen(
            [
                build_ws_message(
                    code=10001,
                    sid="err-sid",
                    message="bad request",
                )
            ]
        )

        body = ImageUnderstandingRequest(
            question="bad",
            image_url="http://fake-image.jpg",
        )

        with pytest.raises(ServiceException) as exc:
            await image_understanding_service(
                body=body,
                request=mock_request,
            )

        assert exc.value.code == CodeEnums.ServiceResponseError.code
        assert mock_request.state.sid is None

    @pytest.mark.asyncio
    async def test_image_understanding_empty_answer(
        self,
        mock_http_client: Tuple[MagicMock | AsyncMock, AsyncMock],
        mock_ws_client: Tuple[MagicMock | AsyncMock, AsyncMock],
        mock_request: MagicMock,
    ) -> None:
        """WebSocket returns empty answer"""
        _, ws = mock_ws_client

        ws.recv.return_value = async_gen(
            [
                build_ws_message(content="", status=2),
            ]
        )

        body = ImageUnderstandingRequest(
            question="empty",
            image_url="http://fake-image.jpg",
        )

        with pytest.raises(ServiceException) as exc:
            await image_understanding_service(
                body=body,
                request=mock_request,
            )

        assert exc.value.code == CodeEnums.ServiceResponseError.code
        assert "返回结果为空" in str(exc.value)
