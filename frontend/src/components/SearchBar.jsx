import { Search, X } from 'lucide-react'
import { useGraphStore } from '../store/graphStore'

export default function SearchBar() {
  const searchQuery = useGraphStore(state => state.searchQuery)
  const setSearchQuery = useGraphStore(state => state.setSearchQuery)

  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      background: 'rgba(0,0,0,0.4)',
      border: '1px solid var(--color-border-strong)',
      borderRadius: '20px',
      padding: '4px 12px',
      marginLeft: '16px',
      width: '200px'
    }}>
      <Search size={14} color="var(--color-text-secondary)" />
      <input
        type="text"
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        placeholder="Filter nodes..."
        style={{
          background: 'transparent',
          border: 'none',
          color: 'white',
          padding: '4px 8px',
          outline: 'none',
          width: '100%',
          fontSize: '13px',
          fontFamily: 'var(--font-sans)'
        }}
      />
      {searchQuery && (
        <button 
          onClick={() => setSearchQuery('')}
          style={{ background: 'transparent', border: 'none', color: 'var(--color-text-secondary)', cursor: 'pointer', display: 'flex' }}
        >
          <X size={14} />
        </button>
      )}
    </div>
  )
}
