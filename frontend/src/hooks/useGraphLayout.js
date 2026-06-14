import { useEffect } from 'react'
import { getLayoutedElements } from '../utils/layoutUtils'
import { useGraphStore } from '../store/graphStore'

export function useGraphLayout() {
  const nodes = useGraphStore(state => state.nodes)
  const edges = useGraphStore(state => state.edges)
  const layoutMode = useGraphStore(state => state.layoutMode)
  const setNodes = useGraphStore(state => state.setNodes)
  const setEdges = useGraphStore(state => state.setEdges)

  useEffect(() => {
    // Only run layout if nodes exist and haven't been laid out yet 
    // (position x and y both exactly 0 is our initial state)
    const needsLayout = nodes.length > 0 && nodes.some(n => n.position.x === 0 && n.position.y === 0)
    
    if (needsLayout) {
      getLayoutedElements(nodes, edges, layoutMode).then(({ nodes: layoutedNodes, edges: layoutedEdges }) => {
        setNodes(layoutedNodes)
        setEdges(layoutedEdges)
      })
    }
  }, [nodes, edges, layoutMode, setNodes, setEdges])
}
