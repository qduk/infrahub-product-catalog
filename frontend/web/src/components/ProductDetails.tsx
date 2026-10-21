import { LICENSE_LABELS, STATUS_LABELS, type Product, type Source } from '../api'

function SourceLinks({ sources }: { sources: Source[] }) {
  if (!sources.length) return null
  return (
    <span className="sources">
      {sources.map((source) => (
        <a key={source.url} href={source.url} target="_blank" rel="noopener noreferrer nofollow">
          {source.title}
        </a>
      ))}
    </span>
  )
}

interface Props {
  product: Product
  onClose: () => void
}

export function ProductDetails({ product, onClose }: Props) {
  return (
    <aside className="details" aria-label={`Details for ${product.full_name}`}>
      <button type="button" className="details-close" onClick={onClose} aria-label="Close details">
        ×
      </button>
      <h2>{product.full_name}</h2>
      <dl>
        <dt>Publisher</dt>
        <dd>
          {product.publisher} <SourceLinks sources={product.sources.publisher} />
        </dd>
        <dt>Description</dt>
        <dd>
          {product.description} <SourceLinks sources={product.sources.description} />
        </dd>
        <dt>Home page</dt>
        <dd>
          <a href={product.homepage_url} target="_blank" rel="noopener noreferrer nofollow">
            {product.homepage_url}
          </a>
        </dd>
        <dt>License model</dt>
        <dd>
          {product.license_model ? LICENSE_LABELS[product.license_model] : 'Not stated by any source'}{' '}
          <SourceLinks sources={product.sources.license_model} />
        </dd>
        <dt>Status</dt>
        <dd>
          {STATUS_LABELS[product.status]}
          {product.status_date && ` since ${product.status_date.slice(0, 10)}`} <SourceLinks sources={product.sources.status} />
        </dd>
      </dl>
      <h3>Coverage</h3>
      <ul className="claims">
        {product.claims.map((claim) => (
          <li key={claim.block}>
            <strong>{claim.block}</strong>: {claim.extent === 'full' ? 'full' : 'partial'}
            {claim.note && <p className="claim-note">{claim.note}</p>}
            <SourceLinks sources={claim.sources} />
          </li>
        ))}
      </ul>
    </aside>
  )
}
