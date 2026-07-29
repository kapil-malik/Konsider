import { useMemo, useState, type KeyboardEvent, type RefObject } from 'react'

import type {
  CatalogCriterionV2,
  ContributionV2,
  RankedCountryV2,
  RankingV2,
} from '../api/types'
import {
  LOCALITY_CONTENT,
  contributingLocalityNames,
  countryCode,
  localityContributions,
  localityName,
} from '../localityPresentation'
import { formatScore } from '../preferences'
import { AssessmentSummary } from './AssessmentSummary'

const contributionFor = (
  country: RankedCountryV2,
  criterionId: string,
): ContributionV2 | undefined =>
  country.contributions.find((item) => item.criterion_id === criterionId)

function DetailedContribution({
  contribution,
  criterion,
}: {
  contribution: ContributionV2
  criterion: CatalogCriterionV2
}) {
  const localityDerived =
    contribution.derivation === 'AGGREGATED_FROM_LOCALITIES'
  return (
    <details className="contribution-details">
      <summary>
        {contribution.score.toFixed(1)} ·{' '}
        {localityDerived ? 'Locality-derived' : 'National'}
      </summary>
      <dl>
        <div>
          <dt>Country score</dt>
          <dd>{formatScore(contribution.score)}</dd>
        </div>
        <div>
          <dt>Derivation</dt>
          <dd>{localityDerived ? 'Aggregated from localities' : 'Direct national evidence'}</dd>
        </div>
        {localityDerived && (
          <>
            <div>
              <dt>Contributing localities</dt>
              <dd>
                {contribution.contributing_localities
                  .map(
                    (item) =>
                      `${item.locality.display_name} (${item.input_score.toFixed(1)})`,
                  )
                  .join(', ')}
              </dd>
            </div>
            <div>
              <dt>Aggregation policy</dt>
              <dd>
                {contribution.aggregation_policy?.method.replaceAll('_', ' ')} ·{' '}
                <code>{contribution.aggregation_policy?.policy_id}</code>
              </dd>
            </div>
          </>
        )}
        <div>
          <dt>Source and period</dt>
          <dd>
            {contribution.sources
              .map((source) => source.publisher ?? source.source_id)
              .join(', ')}
            {contribution.observations[0]
              ? ` · ${contribution.observations[0].reference_start} to ${contribution.observations[0].reference_end}`
              : ''}
          </dd>
        </div>
      </dl>
      {criterion.caveats.map((caveat) => (
        <p key={caveat}>
          <strong>Caveat:</strong> {caveat}
        </p>
      ))}
    </details>
  )
}

function CountryLocalitySummary({ country }: { country: RankedCountryV2 }) {
  const assessment = country.assessments.locality
  if (assessment.status === 'NO_ACTIVE_LOCALITY_CRITERIA') return <span>National evidence</span>
  const contributions = localityContributions(country)
  const names = contributingLocalityNames(country)
  const bestCommon = localityName(
    assessment.best_common_locality_entity_id,
    contributions,
  )
  return (
    <div className={`country-locality locality-${assessment.status.toLocaleLowerCase()}`}>
      <strong>
        <span aria-hidden="true">
          {assessment.status === 'COMMON_LOCALITY_AVAILABLE' ? '✓ ' : '⌖ '}
        </span>
        {LOCALITY_CONTENT[assessment.status].label}
      </strong>
      {bestCommon && <span>Best common: {bestCommon}</span>}
      {!bestCommon && names.length > 0 && (
        <span>
          Evidence: {names.slice(0, 3).join(', ')}
          {names.length > 3 ? ` +${names.length - 3}` : ''}
        </span>
      )}
      {assessment.status === 'NO_COMMON_LOCALITY' && (
        <span className="locality-advisory">
          Strong criteria are supported by different localities; the affinity score is unchanged.
        </span>
      )}
    </div>
  )
}

type RankingViewProps = {
  ranking: RankingV2
  criteria: CatalogCriterionV2[]
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
  const [searchTerm, setSearchTerm] = useState('')
  const [region, setRegion] = useState('')
  const regions = useMemo(
    () =>
      [
        ...new Set(
          ranking.rankings
            .map((country) => country.country.region)
            .filter((value): value is string => Boolean(value)),
        ),
      ].sort(),
    [ranking.rankings],
  )
  const visibleRankings = useMemo(() => {
    const query = searchTerm.trim().toLocaleLowerCase()
    return ranking.rankings.filter(
      (country) =>
        (!region || country.country.region === region) &&
        (!query ||
          country.country.display_name.toLocaleLowerCase().includes(query) ||
          countryCode(country.country.entity_id)
            .toLocaleLowerCase()
            .includes(query)),
    )
  }, [ranking.rankings, region, searchTerm])

  const handleRowKey = (
    event: KeyboardEvent<HTMLTableRowElement>,
    code: string,
  ) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault()
      onSelectCountry(code)
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

      <AssessmentSummary
        ranking={ranking}
        criteria={criteria}
        onSelectCountry={onSelectCountry}
      />

      <div className="rank-scope">
        <strong>Server-ranked countries for the applied priorities</strong>
        <span>
          Locality compatibility is advisory and does not alter the affinity score.
        </span>
      </div>

      <div className="ranking-filters" role="search" aria-label="Filter country ranking">
        <label>
          <span>Search countries</span>
          <input
            type="search"
            value={searchTerm}
            placeholder="Country name or code"
            onChange={(event) => setSearchTerm(event.currentTarget.value)}
          />
        </label>
        <label>
          <span>Region</span>
          <select value={region} onChange={(event) => setRegion(event.currentTarget.value)}>
            <option value="">All regions</option>
            {regions.map((item) => (
              <option value={item} key={item}>
                {item}
              </option>
            ))}
          </select>
        </label>
      </div>

      <div className="ranking-toolbar">
        <label className="toggle-control">
          <input
            type="checkbox"
            checked={detailed}
            onChange={(event) => onDetailedChange(event.currentTarget.checked)}
          />
          <span>Show detailed evidence</span>
        </label>
        <button
          ref={compareButtonRef}
          className="button button-primary"
          disabled={comparisonCountries.length < 2 || isComparing}
          onClick={onCompare}
        >
          {isComparing
            ? 'Preparing comparison…'
            : `Compare selected (${comparisonCountries.length})`}
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
      ) : !visibleRankings.length ? (
        <div className="empty-state filter-empty-state" role="status">
          <h3>No countries match these filters</h3>
          <p>Try another country name, code, or region.</p>
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
                  <th scope="col">Affinity score</th>
                  <th scope="col">Locality context</th>
                  {detailed &&
                    criteria.map((criterion) => (
                      <th scope="col" key={criterion.id} title={criterion.display_name}>
                        <span>{criterion.category}</span>
                        {criterion.scope.derivation ===
                          'AGGREGATED_FROM_LOCALITIES' && (
                          <span className="table-badge">⌖ Locality</span>
                        )}
                      </th>
                    ))}
                </tr>
              </thead>
              <tbody>
                {visibleRankings.map((country) => {
                  const code = countryCode(country.country.entity_id)
                  const checked = comparisonCountries.includes(code)
                  const selected = selectedCountry === code
                  return (
                    <tr
                      key={country.country.entity_id}
                      data-country-code={code}
                      className={selected ? 'selected-row' : undefined}
                      aria-selected={selected}
                      tabIndex={0}
                      onClick={() => onSelectCountry(code)}
                      onKeyDown={(event) => handleRowKey(event, code)}
                    >
                      <td>
                        <input
                          type="checkbox"
                          checked={checked}
                          aria-label={`Select ${country.country.display_name} for comparison`}
                          aria-describedby="comparison-limit"
                          onClick={(event) => event.stopPropagation()}
                          onChange={() => onToggleComparison(code)}
                        />
                      </td>
                      <td className="rank-cell">{country.rank}</td>
                      <td>
                        <strong>{country.country.display_name}</strong>
                        <span className="region-label">
                          {country.country.region ?? code}
                        </span>
                      </td>
                      <td className="score-cell">{formatScore(country.total_score)}</td>
                      <td>
                        <CountryLocalitySummary country={country} />
                      </td>
                      {detailed &&
                        criteria.map((criterion) => {
                          const contribution = contributionFor(country, criterion.id)
                          return (
                            <td key={criterion.id} className="criterion-score-cell">
                              {contribution ? (
                                <DetailedContribution
                                  contribution={contribution}
                                  criterion={criterion}
                                />
                              ) : (
                                '—'
                              )}
                            </td>
                          )
                        })}
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>

          <div className="ranking-cards" role="list" aria-label="Ranked countries">
            {visibleRankings.map((country) => {
              const code = countryCode(country.country.entity_id)
              const checked = comparisonCountries.includes(code)
              const selected = selectedCountry === code
              return (
                <article
                  className={`ranking-card${selected ? ' selected-card' : ''}`}
                  key={country.country.entity_id}
                  data-country-code={code}
                  role="listitem"
                >
                  <div className="ranking-card-heading">
                    <input
                      type="checkbox"
                      checked={checked}
                      aria-label={`Select ${country.country.display_name} for comparison`}
                      aria-describedby="comparison-limit"
                      onChange={() => onToggleComparison(code)}
                    />
                    <span className="rank-pill" aria-label={`Rank ${country.rank}`}>
                      {country.rank}
                    </span>
                    <div>
                      <h3>{country.country.display_name}</h3>
                      <p>{country.country.region ?? code}</p>
                    </div>
                    <strong className="mobile-affinity">
                      {formatScore(country.total_score)}
                    </strong>
                  </div>
                  <CountryLocalitySummary country={country} />
                  {detailed && (
                    <div className="mobile-score-list">
                      {criteria.map((criterion) => {
                        const contribution = contributionFor(country, criterion.id)
                        return (
                          <div key={criterion.id}>
                            <strong>{criterion.display_name}</strong>
                            {contribution ? (
                              <DetailedContribution
                                contribution={contribution}
                                criterion={criterion}
                              />
                            ) : (
                              <span>—</span>
                            )}
                          </div>
                        )
                      })}
                    </div>
                  )}
                  <button className="text-button" onClick={() => onSelectCountry(code)}>
                    View country details
                  </button>
                </article>
              )
            })}
          </div>
        </>
      )}

      <footer className="ranking-footer">
        <span aria-live="polite">
          Showing {visibleRankings.length} of {ranking.rankings.length} returned{' '}
          {ranking.rankings.length === 1 ? 'country' : 'countries'} ·{' '}
          {ranking.assessments.coverage.excluded_countries.length} coverage excluded
        </span>
        <button className="release-link" onClick={onOpenSources}>
          Data release: {ranking.release_id}
        </button>
      </footer>
    </section>
  )
}
