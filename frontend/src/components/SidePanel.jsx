import { useState, useEffect, useRef } from 'react'
import { X, Sparkles, FileText, Zap, Box, ZapIcon } from 'lucide-react'
import { useGraphStore } from '../store/graphStore'

export default function SidePanel() {
  const selectedNodeId = useGraphStore(state => state.selectedNode)
  const setSelectedNode = useGraphStore(state => state.setSelectedNode)
  const nodes = useGraphStore(state => state.nodes)
  const repoPath = useGraphStore(state => state.repoPath)
  
  const [mode, setMode] = useState('summary')
  const [content, setContent] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)
  const [isCached, setIsCached] = useState(false)
  const [error, setError] = useState(null)
  
  const eventSourceRef = useRef(null)

  const selectedNode = nodes.find(n => n.id === selectedNodeId)

  // Reset and fetch when node or mode changes
  useEffect(() => {
    if (!selectedNodeId || !repoPath) {
      setContent('')
      return
    }

    setContent('')
    setIsStreaming(true)
    setIsCached(false)
    setError(null)

    if (eventSourceRef.current) {
      eventSourceRef.current.close()
    }

    const absPath = `${repoPath}/${selectedNodeId}`
    const url = `http://localhost:8000/api/ai/explain?path=${encodeURIComponent(absPath)}&mode=${mode}`
    
    const eventSource = new EventSource(url)
    eventSourceRef.current = eventSource

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (data.error) {
          setError(data.error)
          eventSource.close()
          setIsStreaming(false)
          return
        }
        
        setIsCached(data.cached)
        setContent(prev => prev + data.chunk)
      } catch (err) {
        console.error("Parse error:", err)
      }
    }

    eventSource.onerror = () => {
      eventSource.close()
      setIsStreaming(false)
    }

    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close()
      }
    }
  }, [selectedNodeId, mode, repoPath])

  if (!selectedNode) return null

  const { data } = selectedNode

  return (
    <div style={{
      position: 'absolute',
      right: '24px',
      top: '100px',
      width: '400px',
      maxHeight: 'calc(100vh - 124px)',
      display: 'flex',
      flexDirection: 'column',
      zIndex: 20,
      padding: '24px',
      borderRadius: '24px',
      overflow: 'hidden'
    }} className="glass-panel">
      
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
        <div>
          <h2 style={{ fontSize: '18px', fontWeight: 600, color: 'white', marginBottom: '8px', wordBreak: 'break-all' }}>
            {data.label}
          </h2>
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            <span className="metric-badge" style={{ color: 'var(--color-brand-secondary)' }}>LoC: {data.loc}</span>
            <span className="metric-badge" style={{ color: 'var(--color-complexity-medium)' }}>CC: {data.complexity}</span>
            <span className="metric-badge" style={{ color: 'var(--color-brand-accent)' }}>Blast: {data.blastRadius}</span>
          </div>
        </div>
        <button 
          onClick={() => setSelectedNode(null)}
          style={{ background: 'transparent', border: 'none', color: 'var(--color-text-secondary)', cursor: 'pointer' }}
        >
          <X size={20} />
        </button>
      </div>

      <div style={{ width: '100%', height: '1px', background: 'var(--color-border-strong)', marginBottom: '16px' }} />

      {/* Mode Selector */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '20px', background: 'rgba(0,0,0,0.4)', padding: '4px', borderRadius: '12px' }}>
        <ModeBtn active={mode === 'summary'} onClick={() => setMode('summary')} icon={<FileText size={14} />} label="Summary" />
        <ModeBtn active={mode === 'functions'} onClick={() => setMode('functions')} icon={<Box size={14} />} label="Functions" />
        <ModeBtn active={mode === 'rationale'} onClick={() => setMode('rationale')} icon={<Zap size={14} />} label="Rationale" />
      </div>

      {/* Content Area */}
      <div style={{ 
        flex: 1, 
        overflowY: 'auto', 
        fontSize: '14px', 
        lineHeight: 1.6, 
        color: 'var(--color-text-secondary)',
        paddingRight: '8px'
      }}>
        {error ? (
          <div style={{ color: 'var(--color-brand-accent)' }}>Error: {error}</div>
        ) : (
          <div style={{ whiteSpace: 'pre-wrap' }}>
            {content}
            {isStreaming && <span style={{ opacity: 0.5 }}>...</span>}
          </div>
        )}
      </div>

      {/* Footer / Status */}
      <div style={{ 
        marginTop: '16px', 
        display: 'flex', 
        justifyContent: 'space-between',
        alignItems: 'center',
        fontSize: '12px',
        color: 'var(--color-text-muted)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <Sparkles size={14} color={isStreaming ? 'var(--color-brand-primary)' : 'var(--color-text-muted)'} />
          <span>Gemini 1.5 Flash</span>
        </div>
        {isCached && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px', color: 'var(--color-brand-primary)' }}>
            <ZapIcon size={12} />
            <span>Cached</span>
          </div>
        )}
      </div>

    </div>
  )
}

function ModeBtn({ active, onClick, icon, label }) {
  return (
    <button
      onClick={onClick}
      style={{
        flex: 1,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '6px',
        background: active ? 'var(--color-bg-elevated)' : 'transparent',
        color: active ? 'white' : 'var(--color-text-secondary)',
        border: active ? '1px solid var(--color-border-strong)' : '1px solid transparent',
        padding: '8px',
        borderRadius: '8px',
        cursor: 'pointer',
        fontSize: '12px',
        fontWeight: 500,
        transition: 'all 0.2s'
      }}
    >
      {icon} {label}
    </button>
  )
}
