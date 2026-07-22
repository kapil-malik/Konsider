import { useEffect, useRef } from 'react'

import type { CatalogCriterion, Comparison, RankedCountry } from '../api/types'
import { formatScore } from '../preferences'

const criterionScore = (country: RankedCountry, criterionId: string) =>
  country.contributions.find((item) => item.criterion_id === criterionId)?.score

type ComparisonViewProps = {
  comparison: Comparison
  criteria: CatalogCriterion[]
  onBack: () => void
  onSelectCountry: (countryCode: string) => void
}

export function ComparisonView({
  comparison,
  criteria,
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
          <p>Scores use the same applied priorities as the ranking.</p>
        </div>
        <button className="icon-button" aria-label="Close comparison and return to rankings" onClick={onBack}>
          ×
        </button>
      </div>

      <div className="comparison-table-wrap">
        <table className="comparison-table">
          <thead>
            <tr>
              <th scope="col">Criterion</th>
              {comparison.countries.map((country) => (
                <th scope="col" key={country.country_code}>
                  <button
                    className="country-column-button"
                    onClick={() => onSelectCountry(country.country_code)}
                  >
                    {country.country_name}
                  </button>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            <tr>
              <th scope="row">Overall affinity</th>
              {comparison.countries.map((country) => (
                <td key={country.country_code}>{formatScore(country.total_score)}</td>
              ))}
            </tr>
            {criteria.map((criterion) => (
              <tr key={criterion.id}>
                <th scope="row">
                  {criterion.display_name}
                  {criterion.experimental && (
                    <span className="badge badge-experimental">Experimental</span>
                  )}
                </th>
                {comparison.countries.map((country) => (
                  <td key={country.country_code}>
                    {criterionScore(country, criterion.id)?.toFixed(1) ?? '—'}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="comparison-cards">
        <article className="comparison-card">
          <h3>Overall affinity</h3>
          <dl>
            {comparison.countries.map((country) => (
              <div key={country.country_code}>
                <dt>
                  <button onClick={() => onSelectCountry(country.country_code)}>
                    {country.country_name}
                  </button>
                </dt>
                <dd>{formatScore(country.total_score)}</dd>
              </div>
            ))}
          </dl>
        </article>
        {criteria.map((criterion) => (
          <article className="comparison-card" key={criterion.id}>
            <h3>
              {criterion.display_name}
              {criterion.experimental && (
                <span className="badge badge-experimental">Experimental</span>
              )}
            </h3>
            <dl>
              {comparison.countries.map((country) => (
                <div key={country.country_code}>
                  <dt>
                    <button onClick={() => onSelectCountry(country.country_code)}>
                      {country.country_name}
                    </button>
                  </dt>
                  <dd>{criterionScore(country, criterion.id)?.toFixed(1) ?? '—'}</dd>
                </div>
              ))}
            </dl>
          </article>
        ))}
      </div>

      <footer className="comparison-footer">Data release: {comparison.release_id}</footer>
    </section>
  )
}
