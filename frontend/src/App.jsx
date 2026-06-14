/**
 * App.jsx — Root application component
 *
 * Layout:
 * ┌───────────────────────────────────────────────┐
 * │  Toolbar (top bar — path input, layout modes) │
 * ├───────────────────────────┬───────────────────┤
 * │                           │                   │
 * │   GraphCanvas             │   SidePanel       │
 * │   (React Flow)            │   (AI insights)   │
 * │                           │                   │
 * └───────────────────────────┴───────────────────┘
 *
 * Implemented fully in Phase 2.
 */

// TODO (Phase 2): Implement full App layout

export default function App() {
  return (
    <div className="app-root">
      <p className="coming-soon">
        🔍 CodeLens — Initialising…
      </p>
    </div>
  )
}
