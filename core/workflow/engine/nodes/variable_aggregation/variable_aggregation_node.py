import json
from typing import Any, Dict

from pydantic import Field

from workflow.engine.entities.variable_pool import VariablePool
from workflow.engine.nodes.base_node import BaseNode
from workflow.engine.nodes.entities.node_run_result import (
    NodeRunResult,
    WorkflowNodeExecutionStatus,
)
from workflow.exception.e import CustomException
from workflow.exception.errors.err_code import CodeEnum
from workflow.extensions.otlp.log_trace.node_log import NodeLog
from workflow.extensions.otlp.trace.span import Span


class VariableAggregationNode(BaseNode):
    fallbackEnabled: bool = Field(default=False)
    fallbackValue: Any = Field(default="")

    @staticmethod
    def _is_empty(value: Any) -> bool:
        return value is None or value == "" or value == [] or value == {}

    @staticmethod
    def _default_value_from_schema(schema: Dict[str, Any]) -> Any:
        if "default" in schema:
            return schema["default"]

        schema_type = schema.get("type")
        if schema_type == "string":
            return ""
        if schema_type == "boolean":
            return False
        if schema_type == "integer":
            return 0
        if schema_type == "number":
            return 0.0
        if schema_type == "array":
            return []
        if schema_type == "object":
            return {}
        return None

    @staticmethod
    def _parse_fallback_value(value: Any, schema: Dict[str, Any]) -> Any:
        schema_type = schema.get("type")

        if schema_type == "string":
            if isinstance(value, str):
                return value
        elif schema_type == "boolean":
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                lowered = value.lower()
                if lowered == "true":
                    return True
                if lowered == "false":
                    return False
        elif schema_type == "integer":
            if isinstance(value, int) and not isinstance(value, bool):
                return value
            if isinstance(value, str):
                return int(value)
        elif schema_type == "number":
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                return value
            if isinstance(value, str):
                return float(value)
        elif schema_type == "array":
            if isinstance(value, list):
                return value
            if isinstance(value, str):
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    return parsed
        elif schema_type == "object":
            if isinstance(value, dict):
                return value
            if isinstance(value, str):
                parsed = json.loads(value)
                if isinstance(parsed, dict):
                    return parsed

        raise CustomException(
            CodeEnum.VARIABLE_NODE_EXECUTION_ERROR,
            err_msg="Variable aggregation fallback value type is invalid",
        )

    async def async_execute(
        self,
        variable_pool: VariablePool,
        span: Span,
        event_log_node_trace: NodeLog | None = None,
        **kwargs: Any,
    ) -> NodeRunResult:
        try:
            if not self.output_identifier:
                raise CustomException(
                    CodeEnum.ENG_NODE_PROTOCOL_VALIDATE_ERROR,
                    err_msg="Variable aggregation node requires one output",
                )

            output_name = self.output_identifier[0]
            output_schema = variable_pool.get_output_schema(self.node_id, output_name)
            inputs: Dict[str, Any] = {}

            for input_key in self.input_identifier:
                inputs[input_key] = variable_pool.get_variable(
                    node_id=self.node_id,
                    key_name=input_key,
                    span=span,
                )

            selected_value = next(
                (value for value in inputs.values() if not self._is_empty(value)),
                None,
            )

            if self._is_empty(selected_value):
                if self.fallbackEnabled:
                    selected_value = self._parse_fallback_value(
                        self.fallbackValue, output_schema
                    )
                else:
                    selected_value = self._default_value_from_schema(output_schema)

            outputs = {output_name: selected_value}
            variable_pool.do_validate(
                node_id=self.node_id,
                key_name_list=[output_name],
                outputs=outputs,
                span=span,
            )

            return NodeRunResult(
                status=WorkflowNodeExecutionStatus.SUCCEEDED,
                inputs=inputs,
                outputs=outputs,
                raw_output=json.dumps(outputs, ensure_ascii=False),
                node_id=self.node_id,
                alias_name=self.alias_name,
                node_type=self.node_type,
            )
        except CustomException as err:
            span.record_exception(err)
            return NodeRunResult(
                status=WorkflowNodeExecutionStatus.FAILED,
                error=err,
                node_id=self.node_id,
                alias_name=self.alias_name,
                node_type=self.node_type,
            )
        except Exception as err:
            span.record_exception(err)
            return NodeRunResult(
                status=WorkflowNodeExecutionStatus.FAILED,
                error=CustomException(
                    CodeEnum.VARIABLE_NODE_EXECUTION_ERROR,
                    cause_error=err,
                ),
                node_id=self.node_id,
                alias_name=self.alias_name,
                node_type=self.node_type,
            )
