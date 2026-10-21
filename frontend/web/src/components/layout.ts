// Where each building block sits in the diagram, following the Network Automation Framework
// reference diagram. Blocks come from the catalog; a block missing here goes in an extra row.

export const BLOCK_LAYOUT: Record<string, { area: string; color: string; tagline: string }> = {
  Presentation: { area: 'presentation', color: 'var(--presentation)', tagline: 'Dashboards · CLI · ITSM · API · ChatOps' },
  Observability: { area: 'observability', color: 'var(--observability)', tagline: 'Observed state and analytics' },
  Orchestrator: { area: 'orchestrator', color: 'var(--orchestrator)', tagline: 'Events · Workflows · Scheduling' },
  Intent: { area: 'intent', color: 'var(--intent)', tagline: 'Intended state and validation' },
  Collector: { area: 'collector', color: 'var(--collector)', tagline: 'Read from infrastructure' },
  Executor: { area: 'executor', color: 'var(--executor)', tagline: 'Write to infrastructure' },
}
