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

const isStartNode = (node: WorkflowTraceNode): boolean =>
  (node.nodeId || '').startsWith('node-start::');

const extractModelName = (node: WorkflowTraceNode): string | undefined => {
  const inputModel =
    typeof node.input?.model === 'string' ? (node.input.model as string) : '';
  const outputModel =
    typeof node.output?.model === 'string' ? (node.output.model as string) : '';
  return inputModel || outputModel || undefined;
};

const shouldCreateModelChild = (
  traceNode: TraceTreeNode,
  node: WorkflowTraceNode
): boolean => {
  const modelName = extractModelName(node);
  if (!modelName || modelName === traceNode.name) {
    return false;
  }
  const source = `${traceNode.type} ${traceNode.name}`.toLowerCase();
  return (
    source.includes('llm') ||
    source.includes('模型') ||
    source.includes('大模型') ||
    Boolean(node.input?.model) ||
    Boolean(node.output?.model)
  );
};

const getUsage = (usage?: {
  questionTokens?: number;
  promptTokens?: number;
  completionTokens?: number;
  totalTokens?: number;
}) => ({
  questionTokens: usage?.questionTokens ?? 0,
  promptTokens: usage?.promptTokens ?? 0,
  completionTokens: usage?.completionTokens ?? 0,
  totalTokens: usage?.totalTokens ?? 0,
});

const toTraceNode = (
  execution: WorkflowTraceExecutionItem,
  node: WorkflowTraceNode
): TraceTreeNode => {
  const usage = getUsage(node.usage);
  return {
    id: node.id,
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

  const nodeMap = new Map<string, TraceTreeNode>();
  const childIds = new Set<string>();

  detail.nodes.forEach(node => {
    if (isStartNode(node)) {
      return;
    }
    nodeMap.set(node.id, { ...toTraceNode(detail.execution, node), children: [] });
  });

  detail.nodes.forEach(node => {
    const currentNode = nodeMap.get(node.id);
    if (!currentNode) {
      return;
    }
    (node.nextLogIds || []).forEach(nextLogId => {
      const childNode = nodeMap.get(nextLogId);
      if (childNode) {
        currentNode.children = currentNode.children || [];
        currentNode.children.push(childNode);
        childIds.add(childNode.id);
      }
    });

    if (shouldCreateModelChild(currentNode, node)) {
      currentNode.children = currentNode.children || [];
      currentNode.children.push({
        ...currentNode,
        id: `${currentNode.id}::model`,
        name: currentNode.modelName || '模型',
        kind: 'model',
        children: [],
      });
      childIds.add(`${currentNode.id}::model`);
    }
  });

  const roots = Array.from(nodeMap.values()).filter(node => !childIds.has(node.id));

  if (roots.length > 0) {
    return roots;
  }

  return Array.from(nodeMap.values());
};

export const flattenNodes = (
  nodes: TraceTreeNode[],
  depth = 0
): FlattenTraceNode[] =>
  nodes.flatMap(node => [
    { ...node, depth },
    ...(node.children ? flattenNodes(node.children, depth + 1) : []),
  ]);
