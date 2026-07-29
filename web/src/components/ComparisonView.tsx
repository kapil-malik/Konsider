import { useEffect, useRef } from 'react'

import type {
  ComparisonV2,
  ContributionV2,
} from '../api/types'
import {
  LOCALITY_CONTENT,
  countryCode,
  localityName,
  readableCode,
} from '../localityPresentation'
import { formatScore } from '../preferences'

type ComparisonViewProps = {
  comparison: ComparisonV2
  onBack: () => void
  onSelectCountry: (countryCode: string) => void
}

function ContributionValue({
  contribution,
  outcome,
  reasons,
}: {
  contribution: ContributionV2 | null
  outcome: string
  reasons: string[]
}) {
  if (!contribution) {
    const reasonText = reasons.map(readableCode).join(', ')
    return (
      <span
        className="unavailable-cell"
        aria-label={`Data not available: ${reasonText || readableCode(outcome)}`}
      >
        <span aria-hidden="true">—</span>
        <small>{readableCode(outcome)}</small>
        {reasonText && <small>{reasonText}</small>}
      </span>
    )
  }
  return (
    <div className="comparison-value">
      <strong>{contribution.score.toFixed(1)}</strong>
      {contribution.derivation === 'AGGREGATED_FROM_LOCALITIES' && (
        <>
          <span className="badge badge-scope">⌖ Locality-derived</span>
          <span className="comparison-localities">
            {contribution.contributing_localities
              .map(
                (item) =>
                  `${item.locality.display_name} ${item.input_score.toFixed(1)}`,
              )
              .join(', ')}
          </span>
        </>
      )}
    </div>
  )
}

export function ComparisonView({
  comparison,
  onBack,
  onSelectCountry,
}: ComparisonViewProps) {
  const headingRef = useRef<HTMLHeadingElement>(null)
  useEffect(() => headingRef.current?.focus(), [])

  return (
    <section className="comparison-panel" aria-labelledby="comparison-heading">
      <div className="comparison-header">
        <div>
          <button className="back-button" onClick={onBack}>
            ← Back to rankings
          </button>
          <p className="eyebrow">Side-by-side view</p>
          <h2 id="comparison-heading" ref={headingRef} tabIndex={-1}>
            Compare countries
          </h2>
          <p>
            Scores, locality provenance, and unavailable evidence come directly from the API. No
            partial aggregate is fabricated.
          </p>
        </div>
        <button
          className="icon-button"
          aria-label="Close comparison and return to rankings"
          onClick={onBack}
        >
          ×
        </button>
      </div>

      {comparison.countries.some((country) => country.coverage_excluded) && (
        <div className="comparison-data-notice" role="status">
          <span aria-hidden="true">!</span>
          <p>
            Coverage-excluded countries have no final aggregate. Their available criterion and
            locality evidence remains visible.
          </p>
        </div>
      )}

      <div className="comparison-table-wrap">
        <table className="comparison-table">
          <thead>
            <tr>
              <th scope="col">Criterion</th>
              {comparison.countries.map((country) => {
                const code = countryCode(country.country.entity_id)
                return (
                  <th
                    scope="col"
                    key={country.country.entity_id}
                    className={
                      country.coverage_excluded ? 'unranked-country-column' : undefined
                    }
                  >
                    <button
                      className="country-column-button"
                      onClick={() => onSelectCountry(code)}
                    >
                      {country.country.display_name}
                    </button>
                    {country.coverage_excluded && (
                      <span className="column-status">Coverage excluded</span>
                    )}
                  </th>
                )
              })}
            </tr>
          </thead>
          <tbody>
            <tr>
              <th scope="row">Overall affinity</th>
              {comparison.countries.map((country) => (
                <td
                  key={country.country.entity_id}
                  className={
                    country.coverage_excluded ? 'unranked-country-column' : undefined
                  }
                >
                  {country.final_aggregate !== null && country.rank !== null ? (
                    <>
                      <strong>{formatScore(country.final_aggregate)}</strong>
                      <span className="comparison-rank">Rank {country.rank}</span>
                    </>
                  ) : (
                    <span className="unavailable-cell" aria-label="No partial affinity score">
                      <span aria-hidden="true">—</span>
                      <small>Coverage excluded</small>
                    </span>
                  )}
                </td>
              ))}
            </tr>
            <tr>
              <th scope="row">Locality assessment</th>
              {comparison.countries.map((country) => {
                const locality = country.assessments.locality
                const contributions = comparison.criterion_rows.flatMap((row) =>
                  row.cells
                    .filter(
                      (cell) =>
                        cell.country.entity_id === country.country.entity_id &&
                        cell.contribution,
                    )
                    .map((cell) => cell.contribution as ContributionV2),
                )
                const bestCommon = localityName(
                  locality.best_common_locality_entity_id,
                  contributions,
                )
                return (
                  <td key={country.country.entity_id}>
                    <strong>{LOCALITY_CONTENT[locality.status].label}</strong>
                    {bestCommon && <span>Best common: {bestCommon}</span>}
                    {!bestCommon && locality.common_locality_entity_ids.length > 0 && (
                      <span>
                        Common evidence:{' '}
                        {locality.common_locality_entity_ids
                          .map((id) => localityName(id, contributions))
                          .join(', ')}
                      </span>
                    )}
                  </td>
                )
              })}
            </tr>
            {comparison.criterion_rows.map((row) => (
              <tr key={row.criterion_id}>
                <th scope="row">
                  {row.criterion_name}
                  <span className="row-badges">
                    {row.coverage.mode === 'CONDITIONAL_COMPLETE_CASE' && (
                      <span className="badge badge-limited">! Limited coverage</span>
                    )}
                    {row.scope.derivation === 'AGGREGATED_FROM_LOCALITIES' && (
                      <span className="badge badge-scope">⌖ Locality-derived</span>
                    )}
                  </span>
                </th>
                {comparison.countries.map((country) => {
                  const cell = row.cells.find(
                    (item) => item.country.entity_id === country.country.entity_id,
                  )
                  return (
                    <td
                      key={country.country.entity_id}
                      className={
                        country.coverage_excluded
                          ? 'unranked-country-column'
                          : undefined
                      }
                    >
                      {cell ? (
                        <ContributionValue
                          contribution={cell.contribution}
                          outcome={cell.outcome}
                          reasons={cell.reason_codes}
                        />
                      ) : (
                        <span aria-label="Data not available">—</span>
                      )}
                    </td>
                  )
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="comparison-cards">
        {comparison.countries.map((country) => {
          const code = countryCode(country.country.entity_id)
          return (
            <article className="comparison-card" key={country.country.entity_id}>
              <h3>
                <button onClick={() => onSelectCountry(code)}>
                  {country.country.display_name}
                </button>
              </h3>
              <p>
                {country.final_aggregate !== null
                  ? `${formatScore(country.final_aggregate)} · Rank ${country.rank}`
                  : 'Coverage excluded · no final aggregate'}
              </p>
              <p>
                <strong>Locality:</strong>{' '}
                {LOCALITY_CONTENT[country.assessments.locality.status].label}
              </p>
              <dl>
                {comparison.criterion_rows.map((row) => {
                  const cell = row.cells.find(
                    (item) => item.country.entity_id === country.country.entity_id,
                  )
                  return (
                    <div key={row.criterion_id}>
                      <dt>{row.criterion_name}</dt>
                      <dd>
                        {cell ? (
                          <ContributionValue
                            contribution={cell.contribution}
                            outcome={cell.outcome}
                            reasons={cell.reason_codes}
                          />
                        ) : (
                          '—'
                        )}
                      </dd>
                    </div>
                  )
                })}
              </dl>
            </article>
          )
        })}
      </div>

      <footer className="comparison-footer">Data release: {comparison.release_id}</footer>
    </section>
  )
}
