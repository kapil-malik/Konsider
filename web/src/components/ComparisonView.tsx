import { useEffect, useRef } from 'react'

import type {
  CatalogCriterion,
  Comparison,
  ComparisonCell,
  ComparisonCountrySummary,
} from '../api/types'
import { formatScore } from '../preferences'

type ComparisonViewProps = {
  comparison: Comparison
  criteria: CatalogCriterion[]
  onBack: () => void
  onSelectCountry: (countryCode: string) => void
}

const readableCode = (value: string) =>
  value
    .toLocaleLowerCase()
    .replaceAll('_', ' ')
    .replace(/^\w/, (character) => character.toLocaleUpperCase())

function availabilityLabel(cell: ComparisonCell): string {
  if (cell.availability === 'AVAILABLE') return 'Available'
  return cell.availability === 'STALE' ? 'Data is stale' : 'Data not available'
}

function ComparisonValue({ cell }: { cell: ComparisonCell }) {
  if (cell.availability === 'AVAILABLE' && cell.normalized_score !== null) {
    return (
      <>
        <strong>{cell.normalized_score.toFixed(1)}</strong>
        {cell.raw_observation !== null && cell.raw_unit && (
          <span className="comparison-raw-value">
            {cell.raw_observation.toLocaleString()} {cell.raw_unit.replaceAll('_', ' ')}
          </span>
        )}
      </>
    )
  }

  const reasons = cell.reason_codes.map(readableCode).join(', ')
  return (
    <span
      className="unavailable-cell"
      title={reasons || readableCode(cell.availability)}
      aria-label={`${availabilityLabel(cell)}${reasons ? `: ${reasons}` : ''}`}
    >
      <span aria-hidden="true">—</span>
      <small>{availabilityLabel(cell)}</small>
    </span>
  )
}

function AggregateValue({ summary }: { summary: ComparisonCountrySummary }) {
  if (summary.total_score !== null && summary.rank !== null) {
    return (
      <>
        <strong>{formatScore(summary.total_score)}</strong>
        <span className="comparison-rank">Rank {summary.rank}</span>
      </>
    )
  }
  return (
    <span className="unavailable-cell" aria-label="No partial affinity score">
      <span aria-hidden="true">—</span>
      <small>
        {summary.ranking_status === 'FCC_BASELINE_ONLY'
          ? 'Full-coverage baseline only'
          : 'Not ranked for this profile'}
      </small>
    </span>
  )
}

export function ComparisonView({
  comparison,
  criteria,
  onBack,
  onSelectCountry,
}: ComparisonViewProps) {
  const headingRef = useRef<HTMLHeadingElement>(null)
  const criteriaById = new Map(criteria.map((criterion) => [criterion.id, criterion]))
  const summaries = comparison.country_summaries
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
            Available evidence is shown for every country. An em dash means the source data is
            unavailable; no partial affinity score is fabricated.
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

      {summaries.some((summary) => !summary.ranking_eligible) && (
        <div className="comparison-data-notice" role="status">
          <span aria-hidden="true">ⓘ</span>
          <p>
            Highlighted countries have unavailable data for an active criterion and are not ranked
            for this profile. Their available criterion evidence remains comparable.
          </p>
        </div>
      )}

      <div className="comparison-table-wrap">
        <table className="comparison-table">
          <thead>
            <tr>
              <th scope="col">Criterion</th>
              {summaries.map((summary) => (
                <th
                  scope="col"
                  key={summary.country_code}
                  className={summary.ranking_eligible ? undefined : 'unranked-country-column'}
                >
                  <button
                    className="country-column-button"
                    onClick={() => onSelectCountry(summary.country_code)}
                  >
                    {summary.country_name}
                  </button>
                  {!summary.ranking_eligible && (
                    <span className="column-status">Not ranked for this profile</span>
                  )}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            <tr>
              <th scope="row">Overall affinity</th>
              {summaries.map((summary) => (
                <td
                  key={summary.country_code}
                  className={summary.ranking_eligible ? undefined : 'unranked-country-column'}
                >
                  <AggregateValue summary={summary} />
                </td>
              ))}
            </tr>
            {comparison.criterion_rows.map((row) => {
              const criterion = criteriaById.get(row.criterion_id)
              return (
                <tr key={row.criterion_id}>
                  <th scope="row">
                    {row.criterion_name}
                    <span className="row-badges">
                      {row.coverage_mode === 'CONDITIONAL_COMPLETE_CASE' && (
                        <span className="badge badge-limited">Limited coverage</span>
                      )}
                      {(row.experimental || criterion?.experimental) && (
                        <span className="badge badge-experimental">Experimental</span>
                      )}
                    </span>
                  </th>
                  {summaries.map((summary) => {
                    const cell = row.cells.find(
                      (item) => item.country_code === summary.country_code,
                    )
                    return (
                      <td
                        key={summary.country_code}
                        className={summary.ranking_eligible ? undefined : 'unranked-country-column'}
                      >
                        {cell ? <ComparisonValue cell={cell} /> : <span aria-label="Data not available">—</span>}
                      </td>
                    )
                  })}
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      <div className="comparison-cards">
        <article className="comparison-card">
          <h3>Overall affinity</h3>
          <dl>
            {summaries.map((summary) => (
              <div key={summary.country_code}>
                <dt>
                  <button onClick={() => onSelectCountry(summary.country_code)}>
                    {summary.country_name}
                  </button>
                  {!summary.ranking_eligible && (
                    <span className="column-status">Not ranked</span>
                  )}
                </dt>
                <dd>
                  <AggregateValue summary={summary} />
                </dd>
              </div>
            ))}
          </dl>
        </article>
        {comparison.criterion_rows.map((row) => (
          <article className="comparison-card" key={row.criterion_id}>
            <h3>
              {row.criterion_name}
              <span className="row-badges">
                {row.coverage_mode === 'CONDITIONAL_COMPLETE_CASE' && (
                  <span className="badge badge-limited">Limited coverage</span>
                )}
                {row.experimental && (
                  <span className="badge badge-experimental">Experimental</span>
                )}
              </span>
            </h3>
            <dl>
              {summaries.map((summary) => {
                const cell = row.cells.find(
                  (item) => item.country_code === summary.country_code,
                )
                return (
                  <div key={summary.country_code}>
                    <dt>
                      <button onClick={() => onSelectCountry(summary.country_code)}>
                        {summary.country_name}
                      </button>
                    </dt>
                    <dd>{cell ? <ComparisonValue cell={cell} /> : '—'}</dd>
                  </div>
                )
              })}
            </dl>
          </article>
        ))}
      </div>

      <footer className="comparison-footer">Data release: {comparison.release_id}</footer>
    </section>
  )
}
