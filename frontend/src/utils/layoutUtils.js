import ELK from 'elkjs/lib/elk.bundled.js'

const elk = new ELK()

/**
 * Computes node positions using ELK.js layout engine.
 * Modes:
 * - 'hierarchical': standard top-down layered tree
 * - 'force': force-directed clustering (stress layout)
 * - 'radial': nodes in circles
 */
export async function getLayoutedElements(nodes, edges, mode = 'hierarchical') {
  if (nodes.length === 0) return { nodes, edges }

  const layoutOptions = {
    'hierarchical': {
      'elk.algorithm': 'layered',
      'elk.direction': 'DOWN',
      'elk.spacing.nodeNode': '60',
      'elk.layered.spacing.nodeNodeBetweenLayers': '100',
    },
    'force': {
      'elk.algorithm': 'stress',
    },
    'radial': {
      'elk.algorithm': 'radial',
    }
  }

  const graph = {
    id: 'root',
    layoutOptions: layoutOptions[mode] || layoutOptions['hierarchical'],
    children: nodes.map((node) => ({
      ...node,
      // Default dimensions for our custom node
      width: 250,
      height: 80,
    })),
    edges: edges.map((edge) => ({
      id: edge.id,
      sources: [edge.source],
      targets: [edge.target],
    })),
  }

  try {
    const layoutedGraph = await elk.layout(graph)
    
    const layoutedNodes = nodes.map((node) => {
      const layoutedNode = layoutedGraph.children.find((n) => n.id === node.id)
      return {
        ...node,
        position: {
          x: layoutedNode.x,
          y: layoutedNode.y,
        },
      }
    })

    return { nodes: layoutedNodes, edges }
  } catch (error) {
    console.error('ELK Layout Error:', error)
    return { nodes, edges }
  }
}
