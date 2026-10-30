// The building blocks as the framework diagram arranges them, as a list for narrow screens. On wider
// screens, src/graph/CatalogGraph.tsx shows the same diagram in the graph canvas.

import type { CSSProperties } from 'react'
import type { Catalog } from '../api'
import { countBlockProducts, type Filters } from '../filters'
import { blockStyle, byFrameworkOrder } from '../graph/blockStyle'
import { FRAMEWORK_DIAGRAM as DIAGRAM, INFRASTRUCTURE_ITEMS as INFRASTRUCTURE } from '../graph/framework'

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
    <div className="framework" aria-label="Network Automation Framework building blocks">
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
