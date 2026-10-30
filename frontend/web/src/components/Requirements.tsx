import { useState } from 'react'
import type { Claim, Requirement, Source, Verdict, VerdictValue } from '../api'

export const VERDICT_LABELS: Record<VerdictValue, string> = {
  met: 'Met',
  partly_met: 'Partly met',
  not_met: 'Not met',
  not_shown: 'Not shown',
}

const VERDICT_TITLES: Partial<Record<VerdictValue, string>> = { not_shown: 'Not shown by any source' }

export const LEVEL_LABELS = { must: 'MUST', should: 'SHOULD', may: 'MAY' }

interface Row {
  requirement: Requirement
  verdict: Verdict | undefined
}

function hostOf(url: string): string {
  try {
    return new URL(url).hostname.replace(/^www\./, '')
  } catch {
    return url
  }
}

function Sources({ sources }: { sources: Source[] }) {
  if (!sources.length) return null
  return (
    <span className="source-pills">
      {sources.map((source) => (
        <a key={source.url} className="source-pill" href={source.url} target="_blank" rel="noopener noreferrer nofollow" title={source.title}>
          {hostOf(source.url)}
        </a>
      ))}
    </span>
  )
}

function RequirementRow({ row }: { row: Row }) {
  const value = row.verdict?.verdict ?? 'not_shown'
  return (
    <li className={`requirement requirement-${value}`}>
      <div className="requirement-head">
        <span className={`level level-${row.requirement.level}`}>{LEVEL_LABELS[row.requirement.level]}</span>
        <span className="requirement-summary" title={row.requirement.statement}>
          {row.requirement.summary}
        </span>
        <span className={`verdict verdict-${value}`} title={VERDICT_TITLES[value]}>
          {VERDICT_LABELS[value]}
        </span>
      </div>
      {row.verdict?.note && <p className="requirement-note">{row.verdict.note}</p>}
      <div className="requirement-links">
        <Sources sources={row.verdict?.sources ?? []} />
        <a className="requirement-ref" href={row.requirement.reference_url} target="_blank" rel="noopener noreferrer">
          Framework ↗
        </a>
      </div>
    </li>
  )
}

// The framework requirements that apply to one coverage claim, with their verdicts. The block's MUST
// and SHOULD requirements that keep the claim from full coverage come first. Framework-wide
// requirements are listed with the rest but do not count toward full (user decision, 2026-10-27).
export function Requirements({ claim, requirements }: { claim: Claim; requirements: Requirement[] }) {
  const [showAll, setShowAll] = useState(false)
  const byRequirement = new Map(claim.verdicts.map((verdict) => [verdict.requirement, verdict]))
  const rows: Row[] = requirements
    .filter((requirement) => requirement.block === null || requirement.block === claim.block)
    .map((requirement) => ({ requirement, verdict: byRequirement.get(requirement.identifier) }))
  const required = rows.filter((row) => row.requirement.level !== 'may' && row.requirement.block !== null)
  const shortfalls = required.filter((row) => row.verdict?.verdict !== 'met')
  const met = required.filter((row) => row.verdict?.verdict === 'met')
  const optional = rows.filter((row) => row.requirement.level === 'may')
  const frameworkWide = rows.filter((row) => row.requirement.block === null)
  const missesMust = shortfalls.some(
    (row) => row.requirement.level === 'must' && (row.verdict?.verdict === 'not_met' || row.verdict?.verdict === 'partly_met'),
  )

  if (!claim.assessed) {
    return (
      <p className="requirements-status">
        Not assessed yet against the framework's requirements. A maintainer adds the verdicts during review.
      </p>
    )
  }
  return (
    <div className="requirements">
      <p className="requirements-status">
        Meets {met.length} of {required.length} MUST and SHOULD requirements of {claim.block}.
        {missesMust && <strong className="requirements-warning"> Does not fully meet a MUST requirement of this block.</strong>}
      </p>
      {shortfalls.length > 0 && (
        <ul className="requirement-list" aria-label={`Requirements ${claim.block} falls short on`}>
          {shortfalls.map((row) => (
            <RequirementRow key={row.requirement.identifier} row={row} />
          ))}
        </ul>
      )}
      {met.length + optional.length + frameworkWide.length > 0 && (
        <button type="button" className="requirements-toggle" onClick={() => setShowAll((value) => !value)} aria-expanded={showAll}>
          {showAll ? 'Hide' : 'Show'} {met.length} met, {optional.length} MAY and {frameworkWide.length} framework-wide
          requirements
        </button>
      )}
      {showAll && (
        <>
          <ul className="requirement-list">
            {[...met, ...optional].map((row) => (
              <RequirementRow key={row.requirement.identifier} row={row} />
            ))}
          </ul>
          {frameworkWide.length > 0 && (
            <>
              <p className="requirements-status">For every building block. Shown, but not counted toward full coverage:</p>
              <ul className="requirement-list" aria-label="Framework-wide requirements">
                {frameworkWide.map((row) => (
                  <RequirementRow key={row.requirement.identifier} row={row} />
                ))}
              </ul>
            </>
          )}
        </>
      )}
    </div>
  )
}
