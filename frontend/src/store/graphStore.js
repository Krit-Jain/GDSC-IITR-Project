import { create } from 'zustand'
import { applyNodeChanges, applyEdgeChanges } from '@xyflow/react'

export const useGraphStore = create((set, get) => ({
  nodes: [],
  edges: [],
  selectedNode: null,
  layoutMode: 'hierarchical',
  blastRadiusMode: false,
  searchQuery: '',
  isLoading: false,
  repoPath: '',
  metrics: null,

  setNodes: (nodes) => set({ nodes }),
  setEdges: (edges) => set({ edges }),
  
  onNodesChange: (changes) => set({
    nodes: applyNodeChanges(changes, get().nodes),
  }),
  
  onEdgesChange: (changes) => set({
    edges: applyEdgeChanges(changes, get().edges),
  }),

  setSelectedNode: (nodeId) => set({ selectedNode: nodeId }),
  setLayoutMode: (mode) => set({ layoutMode: mode }),
  setBlastRadiusMode: (active) => set({ blastRadiusMode: active }),
  setSearchQuery: (query) => set({ searchQuery: query }),
  setIsLoading: (loading) => set({ isLoading: loading }),
  setRepoPath: (path) => set({ repoPath: path }),
  setMetrics: (metrics) => set({ metrics }),

  // Action to fetch from backend
  analyzeRepo: async (path) => {
    set({ isLoading: true, repoPath: path, error: null })
    try {
      const res = await fetch(`http://localhost:8000/api/analyze?path=${encodeURIComponent(path)}`)
      if (!res.ok) {
        const data = await res.json()
        throw new Error(data.detail || 'Analysis failed')
      }
      const data = await res.json()
      set({ 
        nodes: data.nodes, 
        edges: data.edges,
        metrics: data.metrics,
        isLoading: false 
      })
    } catch (err) {
      set({ isLoading: false, error: err.message, nodes: [], edges: [], metrics: null })
    }
  }
}))
