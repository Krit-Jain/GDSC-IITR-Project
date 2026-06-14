import Toolbar from './components/Toolbar'
import GraphCanvas from './components/GraphCanvas'
import SidePanel from './components/SidePanel'

export default function App() {
  return (
    <div className="app-root" style={{ position: 'relative', width: '100vw', height: '100vh' }}>
      <Toolbar />
      
      {/* 
        The React Flow canvas takes up the full screen behind the transparent UI.
      */}
      <div style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0 }}>
        <GraphCanvas />
      </div>

      {/* 
        SidePanel sits on top of the canvas, anchored to the right side.
      */}
      <SidePanel />
    </div>
  )
}
