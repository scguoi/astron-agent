from typing import Any, List

from pydantic import BaseModel, Field


class WorkflowTraceUsage(BaseModel):
    question_tokens: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class WorkflowTraceExecutionItem(BaseModel):
    sid: str
    flow_id: str
    flow_name: str = ""
    start_time: int = 0
    end_time: int = 0
    duration: int = 0
    status: str = "running"
    usage: WorkflowTraceUsage = Field(default_factory=WorkflowTraceUsage)


class WorkflowTraceNode(BaseModel):
    id: str
    node_id: str = ""
    node_name: str = ""
    node_type: str = ""
    next_log_ids: list[str] = Field(default_factory=list)
    start_time: int = 0
    end_time: int = 0
    duration: int = 0
    first_frame_duration: int = -1
    status: str = "running"
    usage: WorkflowTraceUsage = Field(default_factory=WorkflowTraceUsage)
    input: dict[str, Any] = Field(default_factory=dict)
    output: dict[str, Any] = Field(default_factory=dict)
    logs: list[str] = Field(default_factory=list)


class WorkflowTraceExecutionPage(BaseModel):
    list: List[WorkflowTraceExecutionItem] = Field(default_factory=list)
    total: int = 0


class WorkflowTraceExecutionDetail(BaseModel):
    execution: WorkflowTraceExecutionItem
    nodes: list[WorkflowTraceNode] = Field(default_factory=list)
