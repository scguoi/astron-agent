import json

from common.otlp.trace.span import SPAN_SIZE_LIMIT
from plugin.aitools.common.clients.adapters import ClientT, SpanLike


def add_info(span: SpanLike, key: str, value: str) -> None:
    if len(value) >= SPAN_SIZE_LIMIT:
        value = f"{value[:SPAN_SIZE_LIMIT // 2]}...{len(value) - SPAN_SIZE_LIMIT // 2}"
    span.add_info_events({key: value})


class WebSocketSpanHooks:
    def setup(self, client: ClientT, span: SpanLike) -> None:
        span.set_attributes(
            {
                "ws_url": client.url,
                "ws_params": json.dumps(client.ws_params, indent=2, ensure_ascii=False),
                "ws_kwargs": json.dumps(client.kwargs, indent=2, ensure_ascii=False),
            }
        )

    async def teardown(self, client: ClientT, span: SpanLike) -> None:
        if client.send_data_list:
            send_data = json.dumps(client.send_data_list, indent=2, ensure_ascii=False)
            add_info(span, "Send data", send_data)
        if client.recv_data_list:
            recv_data = json.dumps(client.recv_data_list, indent=2, ensure_ascii=False)
            add_info(span, "Recv data", recv_data)

        await client.close()


class HttpSpanHooks:
    def setup(self, client: ClientT, span: SpanLike) -> None:
        span.set_attributes(
            {"Request URL": client.url, "Request method": client.method}
        )

        kwargs_str = json.dumps(client.kwargs, indent=2, ensure_ascii=False)
        add_info(span, "Request kwargs", kwargs_str)

    async def teardown(self, client: ClientT, span: SpanLike) -> None:
        if isinstance(client.response.data["content"], bytes):
            response_str = (
                f"Binary data, length: {len(client.response.data['content'])}"
            )
        else:
            response_str = client.response.model_dump_json()
        add_info(span, "Response", response_str)
