import { useState, type CSSProperties } from 'react'
import type { Block, Level, Requirement } from '../api'
import { blockStyle } from '../graph/blockStyle'
import { LEVEL_LABELS } from './Requirements'

function RequirementItem({ requirement }: { requirement: Requirement }) {
  return (
    <li className="requirement">
      <div className="requirement-head">
        <span className={`level level-${requirement.level}`}>{LEVEL_LABELS[requirement.level]}</span>
        <span className="requirement-summary">{requirement.summary}</span>
      </div>
      <details className="requirement-statement">
        <summary>Framework text</summary>
        <p>{requirement.statement}</p>
      </details>
      <div className="requirement-links">
        <a className="requirement-ref" href={requirement.reference_url} target="_blank" rel="noopener noreferrer">
          Framework ↗
        </a>
      </div>
    </li>
  )
}

function LevelSection({ title, label, requirements }: { title: string; label: string; requirements: Requirement[] }) {
  return (
    <section className="details-section">
      <h3>
        {title} ({requirements.length})
      </h3>
      {requirements.length > 0 ? (
        <ul className="requirement-list" aria-label={label}>
          {requirements.map((requirement) => (
            <RequirementItem key={requirement.identifier} requirement={requirement} />
          ))}
        </ul>
      ) : (
        <p className="requirements-status">None.</p>
      )}
    </section>
  )
}

interface Props {
  block: Block
  requirements: Requirement[]
  productCount: number
  onShowProducts: () => void
  onClose: () => void
}

// A building block's MUST and SHOULD requirements, opened from the framework view.
export function BlockDetails({ block, requirements, productCount, onShowProducts, onClose }: Props) {
  const [showFrameworkWide, setShowFrameworkWide] = useState(false)
  const byPosition = (a: Requirement, b: Requirement) => a.position - b.position
  const atLevel = (level: Level, blockName: string | null) =>
    requirements.filter((requirement) => requirement.block === blockName && requirement.level === level).sort(byPosition)
  const frameworkWide = [...atLevel('must', null), ...atLevel('should', null)]

  return (
    <aside
      className="details block-details"
      aria-label={`Requirements of ${block.name}`}
      style={{ '--block-color': blockStyle(block.name).color } as CSSProperties}
    >
      <button type="button" className="details-close" onClick={onClose} aria-label="Close details">
        ×
      </button>
      <header className="details-header">
        <div className="details-title">
          <h2 className="block-details-name">{block.name}</h2>
          {block.definition_url && (
            <a className="requirement-ref" href={block.definition_url} target="_blank" rel="noopener noreferrer">
              Definition in the framework ↗
            </a>
          )}
        </div>
      </header>
      {block.description && <p className="details-description block-details-description">{block.description}</p>}
      <button type="button" className="button block-details-products" onClick={onShowProducts}>
        View the {productCount} {productCount === 1 ? 'product' : 'products'} that cover {block.name}
      </button>

      <LevelSection title="MUST requirements" label={`MUST requirements of ${block.name}`} requirements={atLevel('must', block.name)} />
      <LevelSection title="SHOULD requirements" label={`SHOULD requirements of ${block.name}`} requirements={atLevel('should', block.name)} />

      {frameworkWide.length > 0 && (
        <section className="details-section">
          <button
            type="button"
            className="requirements-toggle"
            onClick={() => setShowFrameworkWide((value) => !value)}
            aria-expanded={showFrameworkWide}
          >
            {showFrameworkWide ? 'Hide' : 'Show'} {frameworkWide.length} MUST and SHOULD requirements for every building block
          </button>
          {showFrameworkWide && (
            <ul className="requirement-list" aria-label="Requirements for every building block">
              {frameworkWide.map((requirement) => (
                <RequirementItem key={requirement.identifier} requirement={requirement} />
              ))}
            </ul>
          )}
        </section>
      )}
    </aside>
  )
}
