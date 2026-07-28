import { useEffect, useRef } from 'react'

import type { Catalog } from '../api/types'

type SourcesDialogProps = {
  catalog: Catalog
  onClose: () => void
}

const FOCUSABLE =
  'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'

export function SourcesDialog({ catalog, onClose }: SourcesDialogProps) {
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
    return () => {
      document.removeEventListener('keydown', handleKeyDown)
    }
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
          <button ref={closeRef} className="icon-button" aria-label="Close Data and Sources" onClick={onClose}>
            ×
          </button>
        </header>

        <div className="dialog-content">
          <section aria-labelledby="how-heading">
            <h3 id="how-heading">How Konsider works</h3>
            <p className="lead-copy">
              Konsider uses selected public datasets from recognized sources. Source observations
              are transformed into comparable criterion scores using Konsider’s internal scoring
              rules. Recommendations reflect the priorities you select and should be treated as a
              decision aid, not definitive relocation advice.
            </p>
            <div className="how-grid">
              <article>
                <span className="step-number">1</span>
                <h4>Set priorities</h4>
                <p>Profiles are editable starting points. Changes affect results only after you apply them.</p>
              </article>
              <article>
                <span className="step-number">2</span>
                <h4>Review affinity</h4>
                <p>
                  Affinity is a score out of 10 relative to the current country set and data release,
                  not a probability or guarantee.
                </p>
              </article>
              <article>
                <span className="step-number">3</span>
                <h4>Inspect and compare</h4>
                <p>Open country details for observations and sources, or compare two to four countries.</p>
              </article>
            </div>
            <div className="advice-note">
              The indicators are national-level. Konsider does not provide immigration, tax, legal,
              employment, city-level, school, or personal financial advice.
            </div>
          </section>

          <section aria-labelledby="criteria-sources-heading">
            <div className="section-heading-row">
              <div>
                <p className="eyebrow">Current catalog</p>
                <h3 id="criteria-sources-heading">Criteria and public sources</h3>
              </div>
              <span className="release-chip">Release {catalog.release_id}</span>
            </div>
            <div className="source-criteria-list">
              {catalog.criteria.map((criterion) => (
                <article className="source-criterion" key={criterion.id}>
                  <div className="source-criterion-heading">
                    <div>
                      <p className="eyebrow">{criterion.category}</p>
                      <h4>{criterion.display_name}</h4>
                    </div>
                    <div className="badge-row">
                      {!criterion.ready && <span className="badge badge-unavailable">Unavailable</span>}
                      {criterion.coverage_mode === 'CONDITIONAL_COMPLETE_CASE' && (
                        <span className="badge badge-limited">Limited coverage</span>
                      )}
                      {criterion.experimental && (
                        <span className="badge badge-experimental">Experimental</span>
                      )}
                    </div>
                  </div>
                  <p>{criterion.description}</p>
                  <p className="source-coverage">
                    <strong>
                      Coverage: {criterion.valid_country_count}/{criterion.stable_country_count}{' '}
                      countries
                    </strong>
                    {criterion.coverage_mode === 'CONDITIONAL_COMPLETE_CASE' &&
                      ' · Affects ranking only at Medium or above.'}
                  </p>
                  {!criterion.ready && (
                    <p className="unavailable-explanation">
                      This criterion is not currently used in rankings because it does not meet the
                      active release’s freshness requirement.
                    </p>
                  )}
                  {criterion.sources.map((source) => (
                    <div className="source-record" key={source.source_id}>
                      <div>
                        <span>Public source</span>
                        <strong>{source.publisher}</strong>
                      </div>
                      <div>
                        <span>Reference period</span>
                        <strong>{source.reference_period}</strong>
                      </div>
                      <a href={source.canonical_page_url} target="_blank" rel="noreferrer">
                        Visit source website (opens in a new tab)
                      </a>
                    </div>
                  ))}
                  <p className="transformation-note">
                    Konsider internally transforms this public-source observation into a comparative
                    score. {criterion.caveats.join(' ')}
                  </p>
                  {criterion.quality_limitations.map((item) => (
                    <p className="quality-note" key={item}>
                      <strong>Major limitation:</strong> {item}
                    </p>
                  ))}
                </article>
              ))}
            </div>
          </section>
        </div>
      </div>
    </div>
  )
}
