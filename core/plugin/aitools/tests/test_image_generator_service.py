"""
Unit tests for ase image generator service.
"""

# pylint: disable=line-too-long,redefined-outer-name
import base64
import uuid
from typing import Iterator, Tuple
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import Request
from plugin.aitools.api.schemas.types import SuccessResponse
from plugin.aitools.common.exceptions.error.code_enums import CodeEnums
from plugin.aitools.common.exceptions.exceptions import ServiceException
from plugin.aitools.service.ase_image_generator.req_ase_ability_image_generate_service import (
    IMAGE_GENERATE_MAX_PROMPT_LEN,
    ImageGenerate,
    req_ase_ability_image_generate_service,
)


def build_image_api_response(
    *,
    code: int = 0,
    message: str = "ok",
    sid: str = "test-sid",
    image_bytes: bytes = b"fake-image",
) -> MagicMock:
    """Build image API response"""
    content = {
        "header": {
            "code": code,
            "message": message,
            "sid": sid,
        }
    }

    if code == 0:
        content["payload"] = {
            "choices": {
                "text": [
                    {
                        "content": base64.b64encode(image_bytes).decode(),
                    }
                ]
            }
        }

    resp = MagicMock()
    resp.data = {"content": content}
    return resp


@pytest.fixture
def mock_uuid() -> Iterator[MagicMock | AsyncMock]:
    """Mock uuid fixture"""
    with patch(
        "plugin.aitools.service.ase_image_generator.req_ase_ability_image_generate_service.uuid.uuid4"
    ) as m:
        m.return_value = uuid.UUID("12345678123456781234567812345678")
        yield m


@pytest.fixture
def mock_request() -> MagicMock:
    """Mock request fixture"""
    request = MagicMock(spec=Request)
    request.state = MagicMock()
    request.state.sid = None
    return request


@pytest.fixture
def mock_upload_file() -> Iterator[AsyncMock]:
    """Mock upload file fixture"""
    with patch(
        "plugin.aitools.service.ase_image_generator.req_ase_ability_image_generate_service.upload_file",
        new_callable=AsyncMock,
    ) as m:
        m.return_value = "https://oss.fake/image.jpg"
        yield m


@pytest.fixture
def mock_http_client() -> Iterator[Tuple[MagicMock | AsyncMock, AsyncMock]]:
    """Mock http client fixture"""
    with patch(
        "plugin.aitools.service.ase_image_generator.req_ase_ability_image_generate_service.HttpClient"
    ) as http_cls:
        client = AsyncMock()
        http_cls.return_value.start.return_value.__aenter__.return_value = client
        yield http_cls, client


@pytest.fixture(autouse=True)
def mock_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mock environment variables"""
    monkeypatch.setenv("IMAGE_GENERATE_URL", "http://fake-image-api/image_generate")
    monkeypatch.setenv("AI_APP_ID", "app-id")
    monkeypatch.setenv("AI_API_KEY", "api-key")
    monkeypatch.setenv("AI_API_SECRET", "api-secret")


class TestImageGeneratorService:
    """Test cases for ASE image generator Service"""

    @pytest.mark.asyncio
    async def test_image_generate_success(
        self,
        mock_http_client: Tuple[MagicMock | AsyncMock, AsyncMock],
        mock_upload_file: AsyncMock,
        mock_request: MagicMock,
    ) -> None:
        """Test image generate success"""
        _, client = mock_http_client

        client.request.return_value = build_image_api_response()

        body = ImageGenerate(prompt="a cat")

        resp = await req_ase_ability_image_generate_service(
            body=body,
            request=mock_request,
        )

        assert isinstance(resp, SuccessResponse)
        assert resp.data["image_url"] == "https://oss.fake/image.jpg"
        assert resp.data["image_url_md"] == "![](https://oss.fake/image.jpg)"
        assert mock_request.state.sid is None

        mock_upload_file.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_image_generate_third_api_error(
        self,
        mock_http_client: Tuple[MagicMock | AsyncMock, AsyncMock],
        mock_request: MagicMock,
    ) -> None:
        """Test image generate third API error"""
        _, client = mock_http_client

        client.request.return_value = build_image_api_response(
            code=10001,
            message="invalid prompt",
            sid="err-sid",
        )

        body = ImageGenerate(prompt="bad")

        with pytest.raises(ServiceException) as exc:
            await req_ase_ability_image_generate_service(
                body=body,
                request=mock_request,
            )

        assert exc.value.code == CodeEnums.ServiceResponseError.code

    @pytest.mark.asyncio
    async def test_prompt_truncated(
        self,
        mock_http_client: Tuple[MagicMock | AsyncMock, AsyncMock],
        mock_upload_file: AsyncMock,  # pylint: disable=unused-argument
        mock_request: MagicMock,
    ) -> None:
        """Test prompt truncated"""
        http_cls, client = mock_http_client

        client.request.return_value = build_image_api_response()

        long_prompt = "a" * (IMAGE_GENERATE_MAX_PROMPT_LEN + 50)
        body = ImageGenerate(prompt=long_prompt)

        await req_ase_ability_image_generate_service(
            body=body,
            request=mock_request,
        )

        sent_json = http_cls.call_args.kwargs["json"]
        prompt_sent = sent_json["payload"]["message"]["text"][0]["content"]

        assert len(prompt_sent) == IMAGE_GENERATE_MAX_PROMPT_LEN
        assert prompt_sent == long_prompt[:IMAGE_GENERATE_MAX_PROMPT_LEN]
