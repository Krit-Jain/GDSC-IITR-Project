import { useCallback, useMemo } from 'react'
import { ReactFlow, Background, Controls, MiniMap, BackgroundVariant } from '@xyflow/react'
import '@xyflow/react/dist/style.css'

import CustomNode from './CustomNode'
import { useGraphStore } from '../store/graphStore'
import { useGraphLayout } from '../hooks/useGraphLayout'

export default function GraphCanvas() {
  const nodes = useGraphStore(state => state.nodes)
  const edges = useGraphStore(state => state.edges)
  const onNodesChange = useGraphStore(state => state.onNodesChange)
  const onEdgesChange = useGraphStore(state => state.onEdgesChange)
  const setSelectedNode = useGraphStore(state => state.setSelectedNode)

  // Register custom node types
  const nodeTypes = useMemo(() => ({ custom: CustomNode }), [])

  // Auto-layout nodes when loaded
  useGraphLayout()

  const onNodeClick = useCallback((_, node) => {
    setSelectedNode(node.id)
  }, [setSelectedNode])

  const onPaneClick = useCallback(() => {
    setSelectedNode(null)
  }, [setSelectedNode])

  // Map nodes to use the 'custom' type
  const flowNodes = useMemo(() => {
    return nodes.map(n => ({ ...n, type: 'custom' }))
  }, [nodes])

  return (
    <div style={{ width: '100%', height: '100%' }}>
      <ReactFlow
        nodes={flowNodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={onNodeClick}
        onPaneClick={onPaneClick}
        nodeTypes={nodeTypes}
        fitView
        attributionPosition="bottom-right"
        minZoom={0.1}
      >
        <Background 
          variant={BackgroundVariant.Dots} 
          gap={24} 
          size={2} 
          color="var(--color-border-default)" 
        />
        <Controls 
          style={{ 
            backgroundColor: 'var(--color-bg-surface)', 
            borderColor: 'var(--color-border-default)',
            fill: 'var(--color-text-primary)'
          }} 
        />
        <MiniMap 
          nodeColor={(node) => {
            if (node.data?.complexity >= 11) return 'var(--color-complexity-high)'
            if (node.data?.complexity >= 6) return 'var(--color-complexity-medium)'
            return 'var(--color-brand-primary)'
          }}
          maskColor="var(--color-bg-overlay)"
          style={{ backgroundColor: 'var(--color-bg-base)' }}
        />
      </ReactFlow>
    </div>
  )
}
