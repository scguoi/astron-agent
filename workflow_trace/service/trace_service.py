from __future__ import annotations

import json
from typing import Any

from workflow_trace.domain.entities.trace import (
    WorkflowTraceExecutionDetail,
    WorkflowTraceExecutionItem,
    WorkflowTraceExecutionPage,
    WorkflowTraceNode,
    WorkflowTraceUsage,
)
from workflow_trace.repository.trace_dao import TraceDao


class TraceService:
    def __init__(self, trace_dao: TraceDao | None = None) -> None:
        self.trace_dao = trace_dao or TraceDao()

    def query_executions(
        self,
        flow_id: str,
        app_id: str | None,
        chat_id: str | None,
        start_time: int | None,
        end_time: int | None,
        page: int,
        page_size: int,
    ) -> WorkflowTraceExecutionPage:
        result = self.trace_dao.query_executions(
            flow_id=flow_id,
            app_id=app_id,
            chat_id=chat_id,
            start_time=start_time,
            end_time=end_time,
            page=page,
            page_size=page_size,
        )
        hits = result.get("hits", {})
        documents = hits.get("hits", [])
        return WorkflowTraceExecutionPage(
            list=[self._build_execution_item(doc.get("_source", {})) for doc in documents],
            total=self._extract_total(hits.get("total", 0)),
        )

    def get_execution_detail(
        self,
        sid: str,
        flow_id: str,
        app_id: str | None,
    ) -> WorkflowTraceExecutionDetail:
        result = self.trace_dao.get_execution_detail(
            sid=sid,
            flow_id=flow_id,
            app_id=app_id,
        )
        hits = result.get("hits", {}).get("hits", [])
        source = hits[0].get("_source", {}) if hits else {}
        execution = self._build_execution_item(source)
        nodes = [self._build_node(node) for node in source.get("trace", [])]
        return WorkflowTraceExecutionDetail(execution=execution, nodes=nodes)

    def _build_execution_item(self, source: dict[str, Any]) -> WorkflowTraceExecutionItem:
        srv = source.get("srv") or {}
        return WorkflowTraceExecutionItem(
            sid=str(source.get("sid") or ""),
            flow_id=str(source.get("flow_id") or ""),
            flow_name=str(
                srv.get("workflow_name")
                or source.get("flow_name")
                or source.get("flow_id")
                or ""
            ),
            start_time=int(source.get("start_time") or 0),
            end_time=int(source.get("end_time") or 0),
            duration=int(source.get("duration") or 0),
            status=self._normalize_execution_status(source),
            usage=self._build_usage(source.get("usage")),
        )

    def _build_node(self, raw_node: dict[str, Any]) -> WorkflowTraceNode:
        data = raw_node.get("data") or {}
        config = self._ensure_dict(data.get("config"))
        return WorkflowTraceNode(
            id=str(raw_node.get("id") or ""),
            node_id=str(raw_node.get("node_id") or raw_node.get("func_id") or ""),
            node_name=str(raw_node.get("node_name") or raw_node.get("func_name") or ""),
            node_type=str(raw_node.get("node_type") or raw_node.get("func_type") or ""),
            next_log_ids=[str(item) for item in (raw_node.get("next_log_ids") or [])],
            start_time=int(raw_node.get("start_time") or 0),
            end_time=int(raw_node.get("end_time") or 0),
            duration=int(raw_node.get("duration") or 0),
            first_frame_duration=int(raw_node.get("first_frame_duration") or -1),
            status=self._normalize_node_status(raw_node),
            usage=self._build_usage(data.get("usage")),
            input=self._build_node_input(data, config),
            output=self._build_node_output(data, config),
            logs=[str(item) for item in (raw_node.get("logs") or [])],
        )

    def _build_usage(self, raw_usage: Any) -> WorkflowTraceUsage:
        usage = raw_usage or {}
        return WorkflowTraceUsage(
            question_tokens=int(usage.get("question_tokens") or usage.get("questionTokens") or 0),
            prompt_tokens=int(usage.get("prompt_tokens") or usage.get("promptTokens") or 0),
            completion_tokens=int(
                usage.get("completion_tokens") or usage.get("completionTokens") or 0
            ),
            total_tokens=int(usage.get("total_tokens") or usage.get("totalTokens") or 0),
        )

    def _normalize_execution_status(self, source: dict[str, Any]) -> str:
        status = source.get("status")
        if isinstance(status, str):
            normalized = status.lower()
            if normalized in {"success", "running", "failed"}:
                return normalized
        if isinstance(status, dict):
            code = int(status.get("code") or 0)
            if code == 0:
                return "success"
            return "failed"
        end_time = int(source.get("end_time") or 0)
        return "success" if end_time > 0 else "running"

    def _normalize_node_status(self, raw_node: dict[str, Any]) -> str:
        if "status" in raw_node and isinstance(raw_node.get("status"), str):
            normalized = str(raw_node.get("status")).lower()
            if normalized in {"success", "running", "failed"}:
                return normalized
        if "status" in raw_node and isinstance(raw_node.get("status"), dict):
            return self._normalize_status_payload(raw_node.get("status") or {})
        if raw_node.get("running_status") is False and not self._is_end_node(raw_node):
            return "failed"
        end_time = int(raw_node.get("end_time") or 0)
        if end_time > 0:
            if self._has_error_logs(raw_node.get("logs")):
                return "failed"
            return "success"
        if raw_node.get("running_status") is False:
            return "failed"
        return "running"

    def _is_end_node(self, raw_node: dict[str, Any]) -> bool:
        node_id = str(raw_node.get("node_id") or raw_node.get("func_id") or "")
        node_type = str(raw_node.get("node_type") or raw_node.get("func_type") or "")
        normalized = f"{node_id} {node_type}".lower()
        return "node-end::" in normalized or "结束" in normalized or normalized.endswith(" end")

    def _normalize_status_payload(self, status: dict[str, Any]) -> str:
        code = int(status.get("code") or 0)
        if code in {0, 200}:
            return "success"
        if code > 0:
            return "failed"
        message = str(status.get("message") or "").lower()
        if "error" in message or "failed" in message:
            return "failed"
        return "running"

    def _ensure_dict(self, value: Any) -> dict[str, Any]:
        return value if isinstance(value, dict) else {}

    def _build_node_input(
        self,
        data: dict[str, Any],
        config: dict[str, Any],
    ) -> dict[str, Any]:
        node_input = self._ensure_dict(data.get("input"))
        if node_input:
            return node_input

        request_body = self._parse_structured_value(config.get("req_body"))
        if isinstance(request_body, dict):
            return request_body
        if isinstance(request_body, list):
            return {"requestBody": request_body}

        fallback_input: dict[str, Any] = {}
        request_headers = self._parse_structured_value(config.get("req_headers"))
        if request_body not in (None, "", {}):
            fallback_input["requestBody"] = request_body
        if request_headers not in (None, "", {}):
            fallback_input["requestHeaders"] = request_headers
        message = self._parse_structured_value(config.get("message"))
        if message not in (None, "", {}):
            fallback_input["message"] = message
        return fallback_input

    def _build_node_output(
        self,
        data: dict[str, Any],
        config: dict[str, Any],
    ) -> dict[str, Any]:
        node_output = self._ensure_dict(data.get("output"))
        if node_output:
            return node_output

        response_format = self._parse_structured_value(config.get("respFormat"))
        if response_format not in (None, "", {}):
            return {"responseFormat": response_format}
        return {}

    def _parse_structured_value(self, value: Any) -> Any:
        if value is None:
            return None
        if isinstance(value, (dict, list, int, float, bool)):
            return value
        if not isinstance(value, str):
            return value
        raw = value.strip()
        if not raw:
            return None
        if raw[0] not in {'{', '[', '"'}:
            return value
        try:
            return json.loads(raw)
        except (TypeError, ValueError, json.JSONDecodeError):
            return value

    def _extract_total(self, total: Any) -> int:
        if isinstance(total, dict):
            return int(total.get("value") or 0)
        return int(total or 0)

    def _has_error_logs(self, logs: Any) -> bool:
        if not isinstance(logs, list):
            return False
        for log in logs:
            if isinstance(log, str) and '"level":"ERROR"' in log:
                return True
        return False
