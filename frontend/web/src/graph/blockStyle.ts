// Colours and taglines for the framework's building blocks, following its reference diagram.

export const BLOCK_STYLE: Record<string, { color: string; tagline: string }> = {
  Presentation: { color: '#f5c518', tagline: 'Dashboards · CLI · ITSM · API · ChatOps' },
  Observability: { color: '#22c55e', tagline: 'Observed state and analytics' },
  Orchestrator: { color: '#06b6d4', tagline: 'Events · Workflows · Scheduling' },
  Intent: { color: '#f97316', tagline: 'Intended state and validation' },
  Collector: { color: '#f43f5e', tagline: 'Read from infrastructure' },
  Executor: { color: '#6366f1', tagline: 'Write to infrastructure' },
}

export const OTHER_BLOCK = { color: '#a3a3a3', tagline: '' }

export const blockStyle = (name: string) => BLOCK_STYLE[name] ?? OTHER_BLOCK

// Framework order, used wherever blocks are listed.
const ORDER = Object.keys(BLOCK_STYLE)
export const byFrameworkOrder = (a: string, b: string) =>
  (ORDER.indexOf(a) === -1 ? ORDER.length : ORDER.indexOf(a)) -
    (ORDER.indexOf(b) === -1 ? ORDER.length : ORDER.indexOf(b)) || a.localeCompare(b)
