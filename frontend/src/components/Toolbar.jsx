import { useState } from 'react'
import { Play, Hexagon, LayoutTemplate, Network, Target } from 'lucide-react'
import { useGraphStore } from '../store/graphStore'
import SearchBar from './SearchBar'

export default function Toolbar() {
  const [inputPath, setInputPath] = useState('')
  const analyzeRepo = useGraphStore(state => state.analyzeRepo)
  const isLoading = useGraphStore(state => state.isLoading)
  const layoutMode = useGraphStore(state => state.layoutMode)
  const setLayoutMode = useGraphStore(state => state.setLayoutMode)

  const handleAnalyze = (e) => {
    e.preventDefault()
    if (inputPath.trim()) {
      analyzeRepo(inputPath.trim())
    }
  }

  return (
    <div style={{
      position: 'absolute',
      top: '24px',
      left: '50%',
      transform: 'translateX(-50%)',
      zIndex: 10,
      display: 'flex',
      gap: '16px',
      alignItems: 'center',
      padding: '12px 24px',
      borderRadius: 'var(--radius-full)',
    }} className="glass-panel">
      
      {/* Logo */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginRight: '16px' }}>
        <Hexagon color="var(--color-brand-primary)" fill="rgba(204, 255, 0, 0.2)" size={24} />
        <span style={{ fontWeight: 700, letterSpacing: '-0.02em', fontSize: '18px' }}>Nexvara</span>
      </div>

      {/* Input Form */}
      <form onSubmit={handleAnalyze} style={{ display: 'flex', gap: '8px' }}>
        <input
          type="text"
          value={inputPath}
          onChange={(e) => setInputPath(e.target.value)}
          placeholder="Enter local repo path..."
          style={{
            background: 'rgba(255, 255, 255, 0.03)',
            border: '1px solid var(--color-border-strong)',
            color: 'white',
            padding: '8px 16px',
            borderRadius: '20px',
            width: '300px',
            fontFamily: 'var(--font-mono)',
            fontSize: '13px',
            outline: 'none',
            transition: 'border-color 0.3s'
          }}
          onFocus={(e) => e.target.style.borderColor = 'var(--color-brand-primary)'}
          onBlur={(e) => e.target.style.borderColor = 'var(--color-border-strong)'}
        />
        <button 
          type="submit" 
          disabled={isLoading}
          style={{
            background: 'var(--color-brand-primary)',
            color: 'black',
            border: 'none',
            padding: '8px 20px',
            borderRadius: '20px',
            fontWeight: 600,
            cursor: isLoading ? 'wait' : 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            transition: 'transform 0.2s',
            opacity: isLoading ? 0.7 : 1
          }}
          onMouseOver={(e) => e.target.style.transform = 'scale(1.05)'}
          onMouseOut={(e) => e.target.style.transform = 'scale(1)'}
        >
          {isLoading ? 'ANALYSING...' : 'ANALYSE'}
          {!isLoading && <Play size={14} fill="black" />}
        </button>
      </form>

      <div style={{ width: '1px', height: '24px', background: 'var(--color-border-strong)', margin: '0 8px' }} />

      {/* Layout Toggles */}
      <div style={{ display: 'flex', gap: '4px', background: 'rgba(0,0,0,0.4)', padding: '4px', borderRadius: '20px' }}>
        <LayoutBtn icon={<LayoutTemplate size={16} />} mode="hierarchical" current={layoutMode} set={setLayoutMode} />
        <LayoutBtn icon={<Network size={16} />} mode="force" current={layoutMode} set={setLayoutMode} />
        <LayoutBtn icon={<Target size={16} />} mode="radial" current={layoutMode} set={setLayoutMode} />
      </div>

      <SearchBar />

    </div>
  )
}

function LayoutBtn({ icon, mode, current, set }) {
  const active = mode === current
  return (
    <button
      onClick={() => set(mode)}
      title={`${mode} layout`}
      style={{
        background: active ? 'var(--color-bg-elevated)' : 'transparent',
        color: active ? 'var(--color-brand-primary)' : 'var(--color-text-secondary)',
        border: active ? '1px solid var(--color-border-strong)' : '1px solid transparent',
        padding: '6px 12px',
        borderRadius: '16px',
        cursor: 'pointer',
        display: 'flex',
        alignItems: 'center',
        transition: 'all 0.2s'
      }}
    >
      {icon}
    </button>
  )
}
