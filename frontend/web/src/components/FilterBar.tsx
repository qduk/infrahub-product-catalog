import { STATUS_LABELS, type Extent, type Status } from '../api'
import { ALL_EXTENTS, ALL_STATUSES, type Filters } from '../filters'

interface Props {
  filters: Filters
  blocks: string[]
  onChange: (filters: Filters) => void
}

function toggle<T>(list: T[], item: T): T[] {
  const next = list.includes(item) ? list.filter((value) => value !== item) : [...list, item]
  return next.length ? next : list
}

export function FilterBar({ filters, blocks, onChange }: Props) {
  return (
    <div className="filters" role="group" aria-label="Filters">
      <fieldset>
        <legend>Status</legend>
        {ALL_STATUSES.map((status: Status) => (
          <label key={status} className="toggle">
            <input
              type="checkbox"
              checked={filters.statuses.includes(status)}
              onChange={() => onChange({ ...filters, statuses: toggle(filters.statuses, status) })}
            />
            {STATUS_LABELS[status]}
          </label>
        ))}
      </fieldset>
      <fieldset>
        <legend>Coverage</legend>
        {ALL_EXTENTS.map((extent: Extent) => (
          <label key={extent} className="toggle">
            <input
              type="checkbox"
              checked={filters.extents.includes(extent)}
              onChange={() => onChange({ ...filters, extents: toggle(filters.extents, extent) })}
            />
            {extent === 'full' ? 'Full' : 'Partial'}
          </label>
        ))}
      </fieldset>
      <label className="block-select">
        Building block
        <select value={filters.block ?? ''} onChange={(event) => onChange({ ...filters, block: event.target.value || null })}>
          <option value="">All building blocks</option>
          {blocks.map((block) => (
            <option key={block} value={block}>
              {block}
            </option>
          ))}
        </select>
      </label>
    </div>
  )
}
