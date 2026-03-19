import React, { memo, useEffect, useMemo, useState } from 'react';
import {
  AppstoreOutlined,
  CheckCircleFilled,
  CloseCircleFilled,
  EyeOutlined,
  FireOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import { Button, Drawer, Empty, Select, Space, Spin, Table, Tag, Typography } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { useTranslation } from 'react-i18next';
import useFlowsManager from '@/components/workflow/store/use-flows-manager';
import {
  getWorkflowTraceExecutionDetail,
  getWorkflowTraceExecutions,
} from '@/services/trace';
import { buildExecutionOptions, buildTraceTree, flattenNodes } from './adapter';
import type {
  FlattenTraceNode,
  TraceExecutionSummary,
  TraceStatus,
  TraceTreeNode,
  TraceView,
} from './types';
import styles from './index.module.scss';

const statusLabelMap: Record<TraceStatus, string> = {
  success: '成功',
  running: '运行中',
  failed: '失败',
};

const formatDuration = (duration: number): string => {
  if (duration === 0) {
    return '0ms';
  }
  if (duration < 1000) {
    return `${duration}ms`;
  }
  return `${(duration / 1000).toFixed(2)}s`;
};

const getTickList = (totalDuration: number): number[] => {
  const step = 1000;
  const count = Math.max(1, Math.ceil(totalDuration / step));
  return Array.from({ length: count }, (_, index) => (index + 1) * step);
};

const stringifyData = (value?: Record<string, unknown>): string => {
  if (!value || Object.keys(value).length === 0) {
    return '暂无数据';
  }
  try {
    return JSON.stringify(value, null, 2);
  } catch {
    return '数据格式无法展示';
  }
};

const renderTree = (
  nodes: TraceTreeNode[],
  selectedNodeId: string,
  onSelect: (node: TraceTreeNode) => void,
  level = 0
): React.ReactNode =>
  nodes.map(node => {
    const isSelected = selectedNodeId === node.id;

    return (
      <div key={node.id}>
        <div
          className={`${styles.treeRow} ${isSelected ? styles.treeRowActive : ''}`}
          style={{ paddingLeft: `${level * 22}px` }}
          onClick={() => onSelect(node)}
        >
          <div className={styles.treeLeft}>
            <span className={styles.treeConnector} />
            <span
              className={`${styles.nodeIcon} ${
                node.status === 'failed' ? styles.nodeIconFailed : ''
              }`}
            >
              {node.status === 'failed' ? (
                <CloseCircleFilled />
              ) : (
                <CheckCircleFilled />
              )}
            </span>
            <span className={styles.nodeName}>{node.name}</span>
          </div>
          <div className={styles.treeMeta}>
            <Tag
              color={
                node.status === 'failed'
                  ? 'error'
                  : node.status === 'running'
                    ? 'processing'
                    : 'success'
              }
              className={styles.durationTag}
            >
              {formatDuration(node.duration)}
            </Tag>
            <EyeOutlined className={styles.eyeIcon} />
          </div>
        </div>
        {node.children &&
          renderTree(node.children, selectedNodeId, onSelect, level + 1)}
      </div>
    );
  });

function WorkflowTracePanel(): React.ReactElement {
  const { t } = useTranslation();
  const workflowTracePanelOpen = useFlowsManager(
    state => state.workflowTracePanelOpen
  );
  const setWorkflowTracePanelOpen = useFlowsManager(
    state => state.setWorkflowTracePanelOpen
  );
  const currentFlow = useFlowsManager(state => state.currentFlow);

  const [executions, setExecutions] = useState<TraceExecutionSummary[]>([]);
  const [selectedExecutionId, setSelectedExecutionId] = useState('');
  const [viewMode, setViewMode] = useState<TraceView>('flame');
  const [traceTree, setTraceTree] = useState<TraceTreeNode[]>([]);
  const [selectedNodeId, setSelectedNodeId] = useState('');
  const [loadingExecutions, setLoadingExecutions] = useState(false);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [reloadSeq, setReloadSeq] = useState(0);

  const selectedExecution = useMemo(
    () => executions.find(execution => execution.id === selectedExecutionId),
    [executions, selectedExecutionId]
  );

  const flattenedNodes = useMemo(
    () => flattenNodes(traceTree),
    [traceTree]
  );

  const selectedNode = useMemo(
    () => flattenedNodes.find(node => node.id === selectedNodeId) || flattenedNodes[0],
    [flattenedNodes, selectedNodeId]
  );

  const flameTicks = useMemo(
    () => getTickList(selectedExecution?.totalDuration || 0),
    [selectedExecution?.totalDuration]
  );

  const listColumns = useMemo<ColumnsType<FlattenTraceNode>>(
    () => [
      {
        title: '节点',
        dataIndex: 'name',
        key: 'name',
        render: (_, record) => (
          <div style={{ paddingLeft: `${record.depth * 18}px` }}>
            {record.name}
          </div>
        ),
      },
      {
        title: '状态',
        dataIndex: 'status',
        key: 'status',
        width: 100,
        render: (value: TraceStatus) => (
          <Tag color={value === 'success' ? 'success' : value === 'failed' ? 'error' : 'processing'}>
            {statusLabelMap[value]}
          </Tag>
        ),
      },
      {
        title: '耗时',
        dataIndex: 'duration',
        key: 'duration',
        width: 120,
        render: (value: number) => formatDuration(value),
      },
      {
        title: '总 Token',
        dataIndex: 'totalTokens',
        key: 'totalTokens',
        width: 120,
      },
      {
        title: '开始偏移',
        dataIndex: 'offset',
        key: 'offset',
        width: 120,
        render: (value: number) => `${value}ms`,
      },
    ],
    []
  );

  useEffect(() => {
    if (!workflowTracePanelOpen || !currentFlow?.flowId) {
      return;
    }

    let cancelled = false;
    setLoadingExecutions(true);
    getWorkflowTraceExecutions(currentFlow.flowId, {
      appId: currentFlow.appId,
      page: 1,
      pageSize: 20,
    })
      .then(result => {
        if (cancelled) {
          return;
        }
        const options = buildExecutionOptions(result.list || []);
        setExecutions(options);
        setSelectedExecutionId(options[0]?.id || '');
      })
      .finally(() => {
        if (!cancelled) {
          setLoadingExecutions(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [workflowTracePanelOpen, currentFlow?.flowId, currentFlow?.appId, reloadSeq]);

  useEffect(() => {
    if (!workflowTracePanelOpen || !currentFlow?.flowId || !selectedExecutionId) {
      setTraceTree([]);
      setSelectedNodeId('');
      return;
    }

    let cancelled = false;
    setLoadingDetail(true);
    getWorkflowTraceExecutionDetail(currentFlow.flowId, selectedExecutionId, {
      appId: currentFlow.appId,
    })
      .then(result => {
        if (cancelled) {
          return;
        }
        const tree = buildTraceTree(result);
        setTraceTree(tree);
        setSelectedNodeId(tree[0]?.id || '');
      })
      .finally(() => {
        if (!cancelled) {
          setLoadingDetail(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [workflowTracePanelOpen, currentFlow?.flowId, currentFlow?.appId, selectedExecutionId]);

  const closePanel = () => {
    setWorkflowTracePanelOpen(false);
  };

  const hasExecution = executions.length > 0;
  const totalDuration = selectedExecution?.totalDuration || 0;

  return (
    <Drawer
      open={workflowTracePanelOpen}
      onClose={closePanel}
      placement="right"
      destroyOnClose
      rootClassName={styles.traceDrawer}
      title={null}
    >
      <div className={styles.panel}>
        <div className={styles.header}>
          <div>
            <Typography.Title level={4} className={styles.title}>
              {t('workflow.nodes.header.traceLogs')}
            </Typography.Title>
            <p className={styles.desc}>
              Workflow Trace 面板已切换到前端-Java-Python 服务链路。
            </p>
          </div>
          <Space>
            <Button
              icon={<ReloadOutlined />}
              onClick={() => {
                setSelectedExecutionId('');
                setExecutions([]);
                setTraceTree([]);
                setSelectedNodeId('');
                setReloadSeq(value => value + 1);
              }}
            >
              刷新
            </Button>
            <Button onClick={closePanel}>{t('common.cancel')}</Button>
          </Space>
        </div>

        <div className={styles.toolbar}>
          <div className={styles.toolbarLeft}>
            <span className={styles.toolbarLabel}>调试</span>
            <Select
              value={selectedExecutionId || undefined}
              className={styles.executionSelect}
              loading={loadingExecutions}
              placeholder="选择执行记录"
              options={executions.map(execution => ({
                label: execution.label,
                value: execution.id,
              }))}
              onChange={value => setSelectedExecutionId(value)}
            />
          </div>
          <div className={styles.summary}>
            <span>{selectedExecution?.workflowName || currentFlow?.name || '-'}</span>
            <span>{formatDuration(selectedExecution?.totalDuration || 0)}</span>
            <span>{selectedExecution?.totalTokens || 0} Tokens</span>
          </div>
        </div>

        <div className={styles.content}>
          <div className={styles.leftPane}>
            <div className={styles.sectionTitle}>节点树</div>
            <div className={styles.treePanel}>
              {loadingDetail ? (
                <Spin />
              ) : traceTree.length > 0 ? (
                renderTree(traceTree, selectedNodeId, node => setSelectedNodeId(node.id))
              ) : (
                <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="暂无 Trace 数据" />
              )}
            </div>
          </div>

          <div className={styles.rightPane}>
            <div className={styles.rightTop}>
              <div className={styles.sectionTitle}>详情</div>
              <Select
                value={viewMode}
                className={styles.viewSelect}
                onChange={value => setViewMode(value)}
                options={[
                  {
                    label: (
                      <span className={styles.optionLabel}>
                        <FireOutlined />
                        火焰图
                      </span>
                    ),
                    value: 'flame',
                  },
                  {
                    label: (
                      <span className={styles.optionLabel}>
                        <AppstoreOutlined />
                        列表
                      </span>
                    ),
                    value: 'list',
                  },
                ]}
              />
            </div>

            <div className={styles.chartCard}>
              {loadingDetail ? (
                <Spin />
              ) : !hasExecution ? (
                <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="暂无执行记录" />
              ) : viewMode === 'flame' ? (
                <>
                  <div className={styles.scrubber}>
                    <span className={styles.scrubberHandle} />
                    <div className={styles.scrubberTrack} />
                    <span className={styles.scrubberHandle} />
                  </div>
                  <div className={styles.tickRow}>
                    {flameTicks.map(tick => (
                      <span key={tick}>{tick}</span>
                    ))}
                  </div>
                  <div className={styles.flameArea}>
                    {flattenedNodes.map(node => {
                      const left = totalDuration > 0 ? (node.offset / totalDuration) * 100 : 0;
                      const width =
                        totalDuration > 0
                          ? Math.max((node.duration / totalDuration) * 100, node.duration === 0 ? 3.5 : 0.8)
                          : 100;

                      return (
                        <div
                          key={node.id}
                          className={`${styles.flameRow} ${
                            selectedNodeId === node.id ? styles.flameRowActive : ''
                          }`}
                          onClick={() => setSelectedNodeId(node.id)}
                        >
                          <div className={styles.flameGrid}>
                            {flameTicks.map(tick => (
                              <span key={tick} className={styles.gridLine} />
                            ))}
                          </div>
                          <div
                            className={styles.flameBar}
                            style={{
                              left: `${left}%`,
                              width: `${width}%`,
                              marginLeft: `${node.depth * 18}px`,
                            }}
                          >
                            {node.name}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </>
              ) : (
                <Table<FlattenTraceNode>
                  rowKey={record => record.id}
                  columns={listColumns}
                  dataSource={flattenedNodes}
                  pagination={false}
                  size="small"
                  onRow={record => ({
                    onClick: () => setSelectedNodeId(record.id),
                    style: { cursor: 'pointer' },
                  })}
                />
              )}
            </div>

            <div className={styles.ioGrid}>
              <div className={styles.ioCard}>
                <div className={styles.sectionTitle}>输入</div>
                <pre className={styles.ioContent}>
                  {stringifyData(selectedNode?.input)}
                </pre>
              </div>
              <div className={styles.ioCard}>
                <div className={styles.sectionTitle}>输出</div>
                <pre className={styles.ioContent}>
                  {stringifyData(selectedNode?.output)}
                </pre>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Drawer>
  );
}

export default memo(WorkflowTracePanel);
