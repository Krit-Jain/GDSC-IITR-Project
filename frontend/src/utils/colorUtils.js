/**
 * colorUtils.js — Complexity → Color Mapping
 * ============================================
 * Maps cyclomatic complexity scores to CSS colour values
 * used to drive the node heatmap visual.
 *
 * Bands:
 *   1–5   → LOW    → var(--color-complexity-low)    #22c55e
 *   6–10  → MEDIUM → var(--color-complexity-medium) #f59e0b
 *   11+   → HIGH   → var(--color-complexity-high)   #ef4444
 *
 * Implemented in Phase 4.
 */

// TODO (Phase 4): Implement color utility
export function complexityToColor(score) {
  if (score <= 5)  return '#22c55e'
  if (score <= 10) return '#f59e0b'
  return '#ef4444'
}

export function complexityLabel(score) {
  if (score <= 5)  return 'LOW'
  if (score <= 10) return 'MEDIUM'
  return 'HIGH'
}
