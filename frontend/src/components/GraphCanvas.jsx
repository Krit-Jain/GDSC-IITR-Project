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
  const selectedNodeId = useGraphStore(state => state.selectedNode)
  const setSelectedNode = useGraphStore(state => state.setSelectedNode)
  const searchQuery = useGraphStore(state => state.searchQuery)
  const blastRadiusMode = useGraphStore(state => state.blastRadiusMode)

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

  // Compute active nodes for dimming effect
  const activeNodeIds = useMemo(() => {
    const activeIds = new Set()
    
    let hasFilter = false

    if (searchQuery) {
      hasFilter = true
      const q = searchQuery.toLowerCase()
      nodes.forEach(n => {
        if (n.data.label.toLowerCase().includes(q)) {
          activeIds.add(n.id)
        }
      })
    }

    if (blastRadiusMode && selectedNodeId) {
      hasFilter = true
      activeIds.add(selectedNodeId)
      const selectedNode = nodes.find(n => n.id === selectedNodeId)
      if (selectedNode?.data?.blastRadiusNodes) {
        selectedNode.data.blastRadiusNodes.forEach(id => activeIds.add(id))
      }
    }

    return hasFilter ? activeIds : null
  }, [nodes, searchQuery, blastRadiusMode, selectedNodeId])

  // Map nodes to use the 'custom' type and apply dimming class
  const flowNodes = useMemo(() => {
    return nodes.map(n => {
      const isDimmed = activeNodeIds !== null && !activeNodeIds.has(n.id)
      return { 
        ...n, 
        type: 'custom',
        className: isDimmed ? 'dimmed' : ''
      }
    })
  }, [nodes, activeNodeIds])

  // Apply dimming to edges
  const flowEdges = useMemo(() => {
    return edges.map(e => {
      const isDimmed = activeNodeIds !== null && (!activeNodeIds.has(e.source) || !activeNodeIds.has(e.target))
      return {
        ...e,
        className: isDimmed ? 'dimmed' : (e.animated ? 'animated' : '')
      }
    })
  }, [edges, activeNodeIds])

  return (
    <div style={{ width: '100%', height: '100%' }}>
      <ReactFlow
        nodes={flowNodes}
        edges={flowEdges}
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
