import type { CSSProperties } from 'react'
import { STATUS_LABELS, type Catalog, type Extent, type Status } from '../api'
import { ALL_EXTENTS, ALL_STATUSES, DEFAULT_FILTERS, serializeFilters, type Filters } from '../filters'
import { blockStyle, byFrameworkOrder } from '../graph/blockStyle'

interface Props {
  catalog: Catalog
  filters: Filters
  onChange: (filters: Filters) => void
}

function toggle<T>(list: T[], item: T): T[] {
  const next = list.includes(item) ? list.filter((value) => value !== item) : [...list, item]
  return next.length ? next : list
}

export function FilterBar({ catalog, filters, onChange }: Props) {
  const withClaims = catalog.products.filter((product) => product.claims.length > 0)
  const statusCount = (status: Status) => withClaims.filter((product) => product.status === status).length
  const extentCount = (extent: Extent) =>
    withClaims.filter(
      (product) => filters.statuses.includes(product.status) && product.claims.some((claim) => claim.extent === extent),
    ).length
  const blockCount = (block: string) =>
    withClaims.filter(
      (product) =>
        filters.statuses.includes(product.status) &&
        product.claims.some((claim) => claim.block === block && filters.extents.includes(claim.extent)),
    ).length
  const isDefault = serializeFilters(filters) === serializeFilters(DEFAULT_FILTERS)

  return (
    <div className="filters" role="group" aria-label="Filters">
      <div className="filter-group">
        <span className="filter-label">Status</span>
        {ALL_STATUSES.map((status) => (
          <button
            key={status}
            type="button"
            className={`chip chip-status-${status}`}
            aria-pressed={filters.statuses.includes(status)}
            onClick={() => onChange({ ...filters, statuses: toggle(filters.statuses, status) })}
          >
            <span className="chip-dot" />
            {STATUS_LABELS[status]}
            <span className="chip-count">{statusCount(status)}</span>
          </button>
        ))}
      </div>

      <div className="filter-group">
        <span className="filter-label">Coverage</span>
        {ALL_EXTENTS.map((extent) => (
          <button
            key={extent}
            type="button"
            className="chip"
            aria-pressed={filters.extents.includes(extent)}
            onClick={() => onChange({ ...filters, extents: toggle(filters.extents, extent) })}
          >
            <svg className={`line-sample line-${extent}`} width="22" height="8" aria-hidden="true">
              <line x1="1" y1="4" x2="21" y2="4" />
            </svg>
            {extent === 'full' ? 'Full' : 'Partial'}
            <span className="chip-count">{extentCount(extent)}</span>
          </button>
        ))}
      </div>

      <div className="filter-group filter-blocks">
        <span className="filter-label">Building block</span>
        <button
          type="button"
          className="chip"
          aria-pressed={filters.block === null}
          onClick={() => onChange({ ...filters, block: null })}
        >
          All
        </button>
        {[...catalog.blocks].sort((a, b) => byFrameworkOrder(a.name, b.name)).map((block) => (
          <button
            key={block.name}
            type="button"
            className="chip chip-block"
            style={{ '--block-color': blockStyle(block.name).color } as CSSProperties}
            aria-pressed={filters.block === block.name}
            onClick={() => onChange({ ...filters, block: filters.block === block.name ? null : block.name })}
          >
            <span className="chip-dot" />
            {block.name}
            <span className="chip-count">{blockCount(block.name)}</span>
          </button>
        ))}
      </div>

      {!isDefault && (
        <button type="button" className="filter-reset" onClick={() => onChange(DEFAULT_FILTERS)}>
          Reset
        </button>
      )}
    </div>
  )
}
