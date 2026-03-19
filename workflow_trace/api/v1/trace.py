from fastapi import APIRouter, Query
from requests import RequestException

from workflow_trace.domain.entities.response import Resp
from workflow_trace.service.trace_service import TraceService

router = APIRouter(tags=["WorkflowTrace"])
trace_service = TraceService()


@router.get("/executions")
def query_executions(
    flow_id: str = Query(...),
    app_id: str | None = Query(default=None),
    chat_id: str | None = Query(default=None),
    start_time: int | None = Query(default=None),
    end_time: int | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
):
    try:
        data = trace_service.query_executions(
            flow_id=flow_id,
            app_id=app_id,
            chat_id=chat_id,
            start_time=start_time,
            end_time=end_time,
            page=page,
            page_size=page_size,
        )
        return Resp.success(data.model_dump(mode="json"))
    except RequestException as exc:
        return Resp.error(50001, f"trace query failed: {exc}")


@router.get("/executions/{sid}")
def get_execution_detail(
    sid: str,
    flow_id: str = Query(...),
    app_id: str | None = Query(default=None),
):
    try:
        data = trace_service.get_execution_detail(
            sid=sid,
            flow_id=flow_id,
            app_id=app_id,
        )
        return Resp.success(data.model_dump(mode="json"))
    except RequestException as exc:
        return Resp.error(50002, f"trace detail query failed: {exc}")
