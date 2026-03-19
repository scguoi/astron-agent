import type {
  FlattenTraceNode,
  TraceExecutionSummary,
  TraceStatus,
  TraceTreeNode,
  WorkflowTraceExecutionDetail,
  WorkflowTraceExecutionItem,
  WorkflowTraceNode,
} from './types';

const statusMap: Record<string, TraceStatus> = {
  success: 'success',
  running: 'running',
  failed: 'failed',
};

const isErrorText = (value: string): boolean => {
  const normalized = value.toLowerCase();
  return (
    normalized.includes('error') ||
    normalized.includes('failed') ||
    normalized.includes('failure') ||
    normalized.includes('exception')
  );
};

const normalizeStatus = (status?: unknown): TraceStatus => {
  if (typeof status === 'string') {
    const normalized = status.trim().toLowerCase();
    if (statusMap[normalized]) {
      return statusMap[normalized];
    }
    if (isErrorText(normalized)) {
      return 'failed';
    }
  }

  if (status && typeof status === 'object') {
    const code = Number((status as { code?: unknown }).code ?? 0);
    if (Number.isFinite(code)) {
      if (code === 0 || code === 200) {
        return 'success';
      }
      if (code > 0) {
        return 'failed';
      }
    }

    const message = String((status as { message?: unknown }).message ?? '');
    if (message && isErrorText(message)) {
      return 'failed';
    }
  }

  return 'running';
};

const extractModelName = (node: WorkflowTraceNode): string | undefined => {
  const inputModel =
    typeof node.input?.model === 'string' ? (node.input.model as string) : '';
  const outputModel =
    typeof node.output?.model === 'string' ? (node.output.model as string) : '';
  const config = node.config || {};
  const configModelName =
    typeof config.model_name === 'string' ? config.model_name : '';
  const configModel = typeof config.model === 'string' ? config.model : '';
  const configDomain = typeof config.domain === 'string' ? config.domain : '';

  return (
    inputModel ||
    outputModel ||
    configModelName ||
    configModel ||
    configDomain ||
    undefined
  );
};

const shouldCreateModelChild = (
  traceNode: TraceTreeNode,
  node: WorkflowTraceNode
): boolean => {
  const modelName = extractModelName(node);
  const source = `${traceNode.type} ${traceNode.name}`.toLowerCase();
  return (
    source.includes('llm') ||
    source.includes('模型') ||
    source.includes('大模型') ||
    Boolean(modelName) ||
    Boolean(node.input?.model) ||
    Boolean(node.output?.model) ||
    Boolean(node.config)
  );
};

const getUsage = (usage?: {
  questionTokens?: number;
  promptTokens?: number;
  completionTokens?: number;
  totalTokens?: number;
}): {
  questionTokens: number;
  promptTokens: number;
  completionTokens: number;
  totalTokens: number;
} => ({
  questionTokens: usage?.questionTokens ?? 0,
  promptTokens: usage?.promptTokens ?? 0,
  completionTokens: usage?.completionTokens ?? 0,
  totalTokens: usage?.totalTokens ?? 0,
});

const HIDDEN_MODEL_CONFIG_KEYS = new Set([
  'url',
  'base_url',
  'apikey',
  'appId',
  'source',
  'node_id',
]);

const sanitizeModelConfig = (
  value: unknown
): Record<string, unknown> | undefined => {
  if (!value || typeof value !== 'object' || Array.isArray(value)) {
    return undefined;
  }

  return Object.fromEntries(
    Object.entries(value).filter(([key]) => !HIDDEN_MODEL_CONFIG_KEYS.has(key))
  );
};

const buildModelChildOutput = (
  node: WorkflowTraceNode
): Record<string, unknown> => ({
  usage: getUsage(node.usage),
  output: node.output || {},
});

const toTraceNode = (
  execution: WorkflowTraceExecutionItem,
  node: WorkflowTraceNode,
  displayId: string
): TraceTreeNode => {
  const usage = getUsage(node.usage);
  return {
    id: displayId,
    name: node.nodeName || node.nodeId || 'Unnamed Node',
    type: node.nodeType || 'unknown',
    kind: 'node',
    status: normalizeStatus(node.status),
    duration: node.duration || 0,
    offset: Math.max((node.startTime || 0) - (execution.startTime || 0), 0),
    totalTokens: usage.totalTokens,
    promptTokens: usage.promptTokens,
    completionTokens: usage.completionTokens,
    questionTokens: usage.questionTokens,
    firstFrameDuration: node.firstFrameDuration,
    input: node.input,
    config: node.config,
    output: node.output,
    logs: node.logs,
    modelName: extractModelName(node),
  };
};

export const buildExecutionOptions = (
  executions: WorkflowTraceExecutionItem[]
): TraceExecutionSummary[] =>
  executions.map(execution => ({
    id: execution.sid,
    label: new Date(execution.startTime || 0).toLocaleString(),
    workflowName: execution.flowName || execution.flowId,
    totalDuration: execution.duration || 0,
    totalTokens: execution.usage?.totalTokens ?? 0,
    status: normalizeStatus(execution.status),
  }));

export const buildTraceTree = (
  detail?: WorkflowTraceExecutionDetail | null
): TraceTreeNode[] => {
  if (!detail) {
    return [];
  }

  return detail.nodes.map((node, index) => {
    const displayId = `${node.id}::${index}`;
    const traceNode: TraceTreeNode = {
      ...toTraceNode(detail.execution, node, displayId),
      children: [],
    };

    if (shouldCreateModelChild(traceNode, node)) {
      traceNode.children = [
        {
          ...traceNode,
          id: `${displayId}::model`,
          name: 'model_name',
          kind: 'model',
          input: sanitizeModelConfig(node.config) || {},
          output: buildModelChildOutput(node),
          children: [],
        },
      ];
    }

    return traceNode;
  });
};

export const flattenNodes = (
  nodes: TraceTreeNode[],
  depth = 0
): FlattenTraceNode[] =>
  nodes.flatMap(node => [
    { ...node, depth },
    ...(node.children ? flattenNodes(node.children, depth + 1) : []),
  ]);
