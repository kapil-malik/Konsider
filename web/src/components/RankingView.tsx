import type { KeyboardEvent, RefObject } from 'react'

import type { CatalogCriterion, Contribution, RankedCountry, Ranking } from '../api/types'
import { formatScore } from '../preferences'

const contributionFor = (country: RankedCountry, criterionId: string): Contribution | undefined =>
  country.contributions.find((item) => item.criterion_id === criterionId)

type RankingViewProps = {
  ranking: Ranking
  criteria: CatalogCriterion[]
  detailed: boolean
  isUpdating: boolean
  isComparing: boolean
  selectedCountry: string | null
  comparisonCountries: string[]
  comparisonNotice: string
  scrollRef: RefObject<HTMLDivElement | null>
  compareButtonRef: RefObject<HTMLButtonElement | null>
  onDetailedChange: (value: boolean) => void
  onSelectCountry: (countryCode: string) => void
  onToggleComparison: (countryCode: string) => void
  onCompare: () => void
  onOpenSources: () => void
}

export function RankingView({
  ranking,
  criteria,
  detailed,
  isUpdating,
  isComparing,
  selectedCountry,
  comparisonCountries,
  comparisonNotice,
  scrollRef,
  compareButtonRef,
  onDetailedChange,
  onSelectCountry,
  onToggleComparison,
  onCompare,
  onOpenSources,
}: RankingViewProps) {
  const handleRowKey = (event: KeyboardEvent<HTMLTableRowElement>, countryCode: string) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault()
      onSelectCountry(countryCode)
    }
  }

  return (
    <section className="results-panel" aria-labelledby="rankings-heading" aria-busy={isUpdating}>
      <div className="results-heading-row">
        <div>
          <p className="eyebrow">Current match</p>
          <h2 id="rankings-heading">Country ranking</h2>
        </div>
        {isUpdating && (
          <span className="updating-state" role="status">
            Updating ranking…
          </span>
        )}
      </div>

      <div className="ranking-toolbar">
        <label className="toggle-control">
          <input
            type="checkbox"
            checked={detailed}
            onChange={(event) => onDetailedChange(event.currentTarget.checked)}
          />
          <span>Show detailed scores</span>
        </label>
        <button
          ref={compareButtonRef}
          className="button button-primary"
          disabled={comparisonCountries.length < 2 || isComparing}
          onClick={onCompare}
        >
          {isComparing ? 'Preparing comparison…' : `Compare selected (${comparisonCountries.length})`}
        </button>
      </div>
      <p id="comparison-limit" className="comparison-guidance" aria-live="polite">
        {comparisonNotice || 'Select 2–4 countries to compare.'}
      </p>

      {!ranking.rankings.length ? (
        <div className="empty-state" role="status">
          <h3>No ranking results</h3>
          <p>The API returned no eligible countries for the current data release.</p>
        </div>
      ) : (
        <>
          <div className="ranking-table-scroll" ref={scrollRef}>
            <table className="ranking-table">
              <thead>
                <tr>
                  <th scope="col" className="selection-column">
                    <span className="sr-only">Compare</span>
                  </th>
                  <th scope="col">Rank</th>
                  <th scope="col">Country</th>
                  <th scope="col">
                    <span title="Affinity Score reflects how well a country matches the selected priorities within the current country set. It is a comparative decision aid, not a probability or guarantee.">
                      Affinity score
                    </span>
                  </th>
                  {detailed &&
                    criteria.map((criterion) => (
                      <th scope="col" key={criterion.id} title={criterion.display_name}>
                        <span>{criterion.category}</span>
                        {criterion.experimental && <span className="table-badge">Experimental</span>}
                      </th>
                    ))}
                </tr>
              </thead>
              <tbody>
                {ranking.rankings.map((country) => {
                  const checked = comparisonCountries.includes(country.country_code)
                  const selected = selectedCountry === country.country_code
                  return (
                    <tr
                      key={country.country_code}
                      data-country-code={country.country_code}
                      className={selected ? 'selected-row' : undefined}
                      aria-selected={selected}
                      tabIndex={0}
                      onClick={() => onSelectCountry(country.country_code)}
                      onKeyDown={(event) => handleRowKey(event, country.country_code)}
                    >
                      <td>
                        <input
                          type="checkbox"
                          checked={checked}
                          aria-label={`Select ${country.country_name} for comparison`}
                          aria-describedby="comparison-limit"
                          onClick={(event) => event.stopPropagation()}
                          onChange={() => onToggleComparison(country.country_code)}
                        />
                      </td>
                      <td className="rank-cell">{country.rank}</td>
                      <td>
                        <strong>{country.country_name}</strong>
                        <span className="region-label">{country.region}</span>
                      </td>
                      <td className="score-cell">{formatScore(country.total_score)}</td>
                      {detailed &&
                        criteria.map((criterion) => (
                          <td key={criterion.id} className="criterion-score-cell">
                            {contributionFor(country, criterion.id)?.score.toFixed(1) ?? '—'}
                          </td>
                        ))}
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>

          <div className="ranking-cards" role="list" aria-label="Ranked countries">
            {ranking.rankings.map((country) => {
              const checked = comparisonCountries.includes(country.country_code)
              const selected = selectedCountry === country.country_code
              return (
                <article
                  className={`ranking-card${selected ? ' selected-card' : ''}`}
                  key={country.country_code}
                  data-country-code={country.country_code}
                  role="listitem"
                >
                  <div className="ranking-card-heading">
                    <input
                      type="checkbox"
                      checked={checked}
                      aria-label={`Select ${country.country_name} for comparison`}
                      aria-describedby="comparison-limit"
                      onChange={() => onToggleComparison(country.country_code)}
                    />
                    <span className="rank-pill" aria-label={`Rank ${country.rank}`}>
                      {country.rank}
                    </span>
                    <div>
                      <h3>{country.country_name}</h3>
                      <p>{country.region}</p>
                    </div>
                    <strong className="mobile-affinity">{formatScore(country.total_score)}</strong>
                  </div>
                  {detailed && (
                    <dl className="mobile-score-list">
                      {criteria.map((criterion) => (
                        <div key={criterion.id}>
                          <dt>
                            {criterion.display_name}
                            {criterion.experimental && (
                              <span className="badge badge-experimental">Experimental</span>
                            )}
                          </dt>
                          <dd>{contributionFor(country, criterion.id)?.score.toFixed(1) ?? '—'}</dd>
                        </div>
                      ))}
                    </dl>
                  )}
                  <button
                    className="text-button"
                    onClick={() => onSelectCountry(country.country_code)}
                  >
                    View country details
                  </button>
                </article>
              )
            })}
          </div>
        </>
      )}

      <footer className="ranking-footer">
        <span>
          Showing all {ranking.returned_result_count} ranked{' '}
          {ranking.returned_result_count === 1 ? 'country' : 'countries'}
        </span>
        <button className="release-link" onClick={onOpenSources}>
          Data release: {ranking.release_id}
        </button>
      </footer>
    </section>
  )
}
