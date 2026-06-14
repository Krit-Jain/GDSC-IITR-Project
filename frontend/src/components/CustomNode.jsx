import { Handle, Position } from '@xyflow/react'
import { FileCode2, FileJson, FileType2, FileBox, ShieldAlert } from 'lucide-react'
import { useGraphStore } from '../store/graphStore'

// Helper to pick icons based on extension
function getFileIcon(ext) {
  switch (ext) {
    case '.py': return <FileCode2 size={16} color="var(--color-node-python)" />
    case '.js': return <FileJson size={16} color="var(--color-node-js)" />
    case '.ts': 
    case '.tsx': return <FileType2 size={16} color="var(--color-node-ts)" />
    case '.css': return <FileCode2 size={16} color="var(--color-node-css)" />
    default: return <FileBox size={16} color="var(--color-node-other)" />
  }
}

// Helper to determine node glow based on complexity
function getComplexityStyle(complexity) {
  if (complexity >= 11) return { borderColor: 'var(--color-complexity-high)', boxShadow: 'var(--shadow-glow-high)' }
  if (complexity >= 6) return { borderColor: 'var(--color-complexity-medium)', boxShadow: 'var(--shadow-glow-med)' }
  return { borderColor: 'var(--color-border-default)', boxShadow: 'none' } // Low complexity = no glow
}

export default function CustomNode({ id, data }) {
  const selectedNode = useGraphStore(state => state.selectedNode)
  const isSelected = selectedNode === id
  const { label, extension, loc, complexity, coupling } = data
  
  const complexityStyle = getComplexityStyle(complexity)
  const isHighRisk = complexity >= 11

  return (
    <div 
      className={`nexvara-node ${isSelected ? 'selected' : ''}`}
      style={isSelected ? {} : complexityStyle} // Selected glow overrides complexity glow
    >
      <Handle type="target" position={Position.Top} style={{ opacity: 0 }} />
      
      <div className="node-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {getFileIcon(extension)}
          <span className="node-filename">{label}</span>
        </div>
        {isHighRisk && <ShieldAlert size={14} color="var(--color-complexity-high)" />}
      </div>

      <div className="node-metrics">
        <span className="metric-badge">LoC: {loc}</span>
        <span className="metric-badge">CC: {complexity}</span>
        <span className="metric-badge">CPL: {coupling}</span>
      </div>

      <Handle type="source" position={Position.Bottom} style={{ opacity: 0 }} />
    </div>
  )
}
