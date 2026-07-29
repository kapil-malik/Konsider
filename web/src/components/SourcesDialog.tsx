import { useEffect, useRef } from 'react'

import type { CatalogV2, RankingV2 } from '../api/types'
import { readableCode } from '../localityPresentation'

type SourcesDialogProps = {
  catalog: CatalogV2
  ranking: RankingV2 | null
  onClose: () => void
}

const FOCUSABLE =
  'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'

export function SourcesDialog({ catalog, ranking, onClose }: SourcesDialogProps) {
  const dialogRef = useRef<HTMLDivElement>(null)
  const closeRef = useRef<HTMLButtonElement>(null)

  useEffect(() => {
    closeRef.current?.focus()
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        event.preventDefault()
        onClose()
        return
      }
      if (event.key !== 'Tab' || !dialogRef.current) return
      const items = [...dialogRef.current.querySelectorAll<HTMLElement>(FOCUSABLE)]
      if (!items.length) return
      const first = items[0]
      const last = items[items.length - 1]
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault()
        last.focus()
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault()
        first.focus()
      }
    }
    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [onClose])

  return (
    <div className="dialog-backdrop" role="presentation" onMouseDown={onClose}>
      <div
        className="sources-dialog"
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="sources-heading"
        onMouseDown={(event) => event.stopPropagation()}
      >
        <header className="dialog-header">
          <div>
            <p className="eyebrow">Method and provenance</p>
            <h2 id="sources-heading">Data &amp; Sources</h2>
          </div>
          <button
            ref={closeRef}
            className="icon-button"
            aria-label="Close Data and Sources"
            onClick={onClose}
          >
            ×
          </button>
        </header>

        <div className="dialog-content">
          <section aria-labelledby="how-heading">
            <h3 id="how-heading">How Konsider works</h3>
            <p className="lead-copy">
              The API supplies country scores, coverage decisions, locality derivation, and
              compatibility assessments. The browser presents that evidence without selecting
              localities, calculating overlap, or changing affinity scores.
            </p>
            <div className="how-grid">
              <article>
                <span className="step-number">1</span>
                <h4>Set priorities</h4>
                <p>Preference presets are editable starting points.</p>
              </article>
              <article>
                <span className="step-number">2</span>
                <h4>Review separate assessments</h4>
                <p>Coverage, locality, and applicant-profile context remain distinct.</p>
              </article>
              <article>
                <span className="step-number">3</span>
                <h4>Inspect evidence</h4>
                <p>Open country details for national and locality-derived provenance.</p>
              </article>
            </div>
            <div className="advice-note">
              Locality evidence describes options within a country; it is not immigration, tax,
              legal, employment, school, or personal financial advice.
            </div>
          </section>

          <section aria-labelledby="criteria-sources-heading">
            <div className="section-heading-row">
              <div>
                <p className="eyebrow">Current catalog</p>
                <h3 id="criteria-sources-heading">Criteria and source lineage</h3>
              </div>
              <span className="release-chip">Release {catalog.release_id}</span>
            </div>
            <div className="source-criteria-list">
              {catalog.criteria.map((criterion) => {
                const contribution = ranking?.rankings
                  .flatMap((country) => country.contributions)
                  .find((item) => item.criterion_id === criterion.id)
                return (
                  <article className="source-criterion" key={criterion.id}>
                    <div className="source-criterion-heading">
                      <div>
                        <p className="eyebrow">{criterion.category}</p>
                        <h4>{criterion.display_name}</h4>
                      </div>
                      <div className="badge-row">
                        {!criterion.ready && (
                          <span className="badge badge-unavailable">! Unavailable</span>
                        )}
                        {criterion.coverage.mode ===
                          'CONDITIONAL_COMPLETE_CASE' && (
                          <span className="badge badge-limited">! Limited coverage</span>
                        )}
                        <span className="badge badge-scope">
                          {criterion.scope.derivation ===
                          'AGGREGATED_FROM_LOCALITIES'
                            ? '⌖ Locality-derived'
                            : '● National'}
                        </span>
                        {criterion.experimental && (
                          <span className="badge badge-experimental">
                            ◇ Experimental
                          </span>
                        )}
                      </div>
                    </div>
                    <p>{criterion.description}</p>
                    {criterion.historical_names.length > 0 && (
                      <p className="historical-name">
                        Previously called: {criterion.historical_names.join(', ')}
                      </p>
                    )}
                    <dl className="source-metadata-grid">
                      <div>
                        <dt>Coverage</dt>
                        <dd>
                          {criterion.coverage.valid_country_count}/
                          {criterion.coverage.stable_country_count} countries ·{' '}
                          {readableCode(criterion.coverage.mode)}
                        </dd>
                      </div>
                      <div>
                        <dt>Scope</dt>
                        <dd>
                          {readableCode(criterion.scope.evidence_level)} evidence ·{' '}
                          {readableCode(criterion.scope.derivation)}
                        </dd>
                      </div>
                      <div>
                        <dt>Applicability</dt>
                        <dd>
                          {readableCode(criterion.applicability.mode)}
                          {criterion.applicability.dimensions.length
                            ? ` · ${criterion.applicability.dimensions
                                .map(readableCode)
                                .join(', ')}`
                            : ''}
                        </dd>
                      </div>
                      {criterion.scope.locality_universe_id && (
                        <div>
                          <dt>Locality universe</dt>
                          <dd>
                            <code>{criterion.scope.locality_universe_id}</code>
                          </dd>
                        </div>
                      )}
                      {criterion.scope.aggregation_policy_id && (
                        <div>
                          <dt>Aggregation</dt>
                          <dd>
                            {contribution?.aggregation_policy
                              ? `${readableCode(
                                  contribution.aggregation_policy.method,
                                )} · `
                              : 'Server policy · '}
                            <code>{criterion.scope.aggregation_policy_id}</code>
                          </dd>
                        </div>
                      )}
                    </dl>
                    {criterion.sources.map((source) => (
                      <div
                        className="source-record"
                        key={`${source.source_id}:${source.source_version}:${source.role}`}
                      >
                        <div>
                          <span>Source lineage</span>
                          <strong>{source.publisher ?? source.source_id}</strong>
                        </div>
                        <div>
                          <span>Version and role</span>
                          <strong>
                            {source.source_version}
                            {source.role ? ` · ${readableCode(source.role)}` : ''}
                          </strong>
                        </div>
                        {source.canonical_page_url && (
                          <a
                            href={source.canonical_page_url}
                            target="_blank"
                            rel="noreferrer"
                          >
                            Visit source website (opens in a new tab)
                          </a>
                        )}
                      </div>
                    ))}
                    <p className="transformation-note">
                      Scoring: <code>{criterion.scoring_method_version}</code>.{' '}
                      {criterion.caveats.join(' ')}
                    </p>
                  </article>
                )
              })}
            </div>
          </section>
        </div>
      </div>
    </div>
  )
}
