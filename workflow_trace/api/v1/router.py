from fastapi import APIRouter

from workflow_trace.api.v1.trace import router as trace_router

workflow_trace_router = APIRouter(prefix="/workflow-trace/v1")
workflow_trace_router.include_router(trace_router)
