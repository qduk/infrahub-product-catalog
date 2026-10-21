import type { CSSProperties } from 'react'
import { STATUS_LABELS } from '../api'
import type { BlockView } from '../filters'
import { BLOCK_LAYOUT } from './layout'

interface Props {
  view: BlockView
  onSelectProduct: (productId: string) => void
  onShowOnly: (block: string) => void
  filtered: boolean
}

export function Block({ view, onSelectProduct, onShowOnly, filtered }: Props) {
  const layout = BLOCK_LAYOUT[view.block.name]
  const entries = [...view.entries].sort(
    (a, b) =>
      (a.claim.extent === b.claim.extent ? 0 : a.claim.extent === 'full' ? -1 : 1) ||
      a.product.full_name.localeCompare(b.product.full_name),
  )
  return (
    <section
      className="block"
      style={{ gridArea: layout?.area ?? 'auto', '--block-color': layout?.color ?? 'var(--other)' } as CSSProperties}
      aria-label={view.block.name}
    >
      <header className="block-header">
        <h2>
          <button type="button" className="block-title" onClick={() => onShowOnly(view.block.name)}>
            {view.block.name}
          </button>
        </h2>
        <span className="block-count">{entries.length}</span>
      </header>
      {layout && <p className="block-tagline">{layout.tagline}</p>}
      {entries.length === 0 ? (
        <p className="block-empty">{filtered ? 'No products match the filters.' : 'No products cover this block.'}</p>
      ) : (
        <ul className="product-list">
          {entries.map(({ product, claim }) => (
            <li key={product.id}>
              <button
                type="button"
                className={`product-chip extent-${claim.extent} status-${product.status}`}
                onClick={() => onSelectProduct(product.id)}
                title={`${product.full_name}: ${claim.extent} coverage`}
              >
                <span className="product-name">{product.full_name}</span>
                <span className="product-tags">
                  <span className="tag">{claim.extent === 'full' ? 'Full' : 'Partial'}</span>
                  {product.status !== 'active' && <span className="tag tag-status">{STATUS_LABELS[product.status]}</span>}
                </span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
