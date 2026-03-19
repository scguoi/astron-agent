from __future__ import annotations

from typing import Any

from workflow_trace.configs import settings
from workflow_trace.extensions.middleware.search.factory import get_search_manager


class TraceDao:
    def __init__(self) -> None:
        self.search_manager = get_search_manager()
        self.index = settings.es_index

    def query_executions(
        self,
        flow_id: str,
        app_id: str | None,
        chat_id: str | None,
        start_time: int | None,
        end_time: int | None,
        page: int,
        page_size: int,
    ) -> dict[str, Any]:
        must: list[dict[str, Any]] = [
            {"term": {"flow_id.keyword": flow_id}},
            {"term": {"sub.keyword": "workflow"}},
        ]
        must_not: list[dict[str, Any]] = [
            {"term": {"log_caller.keyword": "build"}},
        ]
        if app_id:
            must.append({"term": {"app_id.keyword": app_id}})
        if chat_id:
            must.append({"term": {"chat_id.keyword": chat_id}})
        if start_time is not None or end_time is not None:
            range_query: dict[str, Any] = {}
            if start_time is not None:
                range_query["gte"] = start_time
            if end_time is not None:
                range_query["lte"] = end_time
            must.append({"range": {"start_time": range_query}})

        body = {
            "from": max(page - 1, 0) * page_size,
            "size": page_size,
            "sort": [{"start_time": {"order": "desc"}}],
            "query": {"bool": {"must": must, "must_not": must_not}},
            "_source": [
                "sid",
                "flow_id",
                "app_id",
                "chat_id",
                "start_time",
                "end_time",
                "duration",
                "usage",
                "status",
                "srv.workflow_name",
                "srv.workflow_version",
            ],
        }
        return self.search_manager.search(self.index, body)

    def get_execution_detail(
        self,
        sid: str,
        flow_id: str,
        app_id: str | None,
    ) -> dict[str, Any]:
        must: list[dict[str, Any]] = [
            {"term": {"sid.keyword": sid}},
            {"term": {"flow_id.keyword": flow_id}},
            {"term": {"sub.keyword": "workflow"}},
        ]
        must_not: list[dict[str, Any]] = [
            {"term": {"log_caller.keyword": "build"}},
        ]
        if app_id:
            must.append({"term": {"app_id.keyword": app_id}})

        body = {
            "size": 1,
            "query": {"bool": {"must": must, "must_not": must_not}},
        }
        return self.search_manager.search(self.index, body)
