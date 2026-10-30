// The building blocks laid out as in the framework's reference diagram, without products.
// Diagram: https://reference.networkautomation.forum/Framework/images/naf-automation-framework-v1-dark.png
// The items inside each block are copied from that diagram.

import type { CSSProperties } from 'react'
import type { Catalog } from '../api'
import { countBlockProducts, type Filters } from '../filters'
import { blockStyle, byFrameworkOrder } from '../graph/blockStyle'

const DIAGRAM: Record<string, { row: 'top' | 'middle' | 'bottom'; items: string[] }> = {
  Presentation: { row: 'top', items: ['Dashboards · CLI · ITSM Integration · API Gateway · ChatOps'] },
  Observability: { row: 'middle', items: ['Observed State · Data Normalization', 'Observed Logic & Analytics'] },
  Orchestrator: { row: 'middle', items: ['Events', 'Workflows', 'Rollback', 'Scheduling'] },
  Intent: { row: 'middle', items: ['Intended State (SoT)', 'Intended Logic & Validation'] },
  Collector: { row: 'bottom', items: ['Read Operations', '▲ Read from infrastructure'] },
  Executor: { row: 'bottom', items: ['Write Operations · Idempotent · Dry-Run', '▼ Write to infrastructure'] },
}

const INFRASTRUCTURE = 'Routers · Switches · Firewalls · Load Balancers · SD-WAN · Cloud Fabric · Compute · DPU'

interface Props {
  catalog: Catalog
  filters: Filters
  selectedBlock: string | null
  onSelectBlock: (name: string) => void
}

export function FrameworkView({ catalog, filters, selectedBlock, onSelectBlock }: Props) {
  const names = catalog.blocks.map((block) => block.name).sort(byFrameworkOrder)
  const row = (name: 'top' | 'middle' | 'bottom') => names.filter((block) => DIAGRAM[block]?.row === name)
  const others = names.filter((block) => !DIAGRAM[block])

  const tile = (name: string) => {
    const count = countBlockProducts(catalog, filters, name)
    const items = DIAGRAM[name]?.items ?? []
    return (
      <button
        key={name}
        type="button"
        className={`framework-block${DIAGRAM[name]?.row === 'top' ? ' framework-block-wide' : ''}`}
        style={{ '--block-color': blockStyle(name).color } as CSSProperties}
        aria-pressed={selectedBlock === name}
        onClick={() => onSelectBlock(name)}
      >
        <span className="framework-block-name">{name}</span>
        {items.length > 0 && (
          <span className={`framework-items${items.length === 4 ? ' framework-items-grid' : ''}`}>
            {items.map((item) => (
              <span key={item} className="framework-item">
                {item}
              </span>
            ))}
          </span>
        )}
        <span className="framework-count">
          {count} {count === 1 ? 'product' : 'products'}
        </span>
      </button>
    )
  }

  return (
    <div className={`framework${selectedBlock ? ' framework-with-panel' : ''}`} aria-label="Network Automation Framework building blocks">
      <div className="framework-row framework-row-top">{row('top').map(tile)}</div>
      <div className="framework-row framework-row-middle">{row('middle').map(tile)}</div>
      <div className="framework-row framework-row-bottom">{row('bottom').map(tile)}</div>
      {others.length > 0 && <div className="framework-row framework-row-other">{others.map(tile)}</div>}
      <div className="framework-infrastructure">
        <span className="framework-block-name">Infrastructure</span>
        <span className="framework-infrastructure-items">{INFRASTRUCTURE}</span>
      </div>
    </div>
  )
}
