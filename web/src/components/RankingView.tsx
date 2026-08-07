import { useMemo, useState, type KeyboardEvent, type RefObject } from 'react'

import type {
  CatalogCriterionV2,
  CatalogV2,
  RankingContributionV3,
  OpportunityFilterCatalogV2,
  RankedCountryV2,
  RankingV2,
  TfcCatalogV2,
} from '../api/types'
import { compactDisplayName } from '../displayName'
import {
  LOCALITY_CONTENT,
  contributingLocalityNames,
  countryCode,
  localityContributions,
  localityName,
} from '../localityPresentation'
import {
  OPPORTUNITY_STATE_CONTENT,
  filterName,
} from '../opportunityPresentation'
import { formatScore } from '../preferences'
import { AssessmentSummary } from './AssessmentSummary'
import {
  CountryFeasibilitySummary,
  FeasibilitySummary,
} from './FeasibilitySummary'
import { CountrySearchAutocomplete } from './CountryAutocomplete'

const contributionFor = (
  country: RankedCountryV2,
  criterionId: string,
): RankingContributionV3 | undefined =>
  country.contributions.find((item) => item.criterion_id === criterionId)

function CriterionSymbols({ criterion }: { criterion: CatalogCriterionV2 }) {
  const isPartial = criterion.coverage.mode === 'CONDITIONAL_COMPLETE_CASE'
  const isLocality = criterion.scope.derivation === 'AGGREGATED_FROM_LOCALITIES'
  return (
    <span className="criterion-table-symbols">
      <span
        className="criterion-symbol"
        aria-label={isPartial ? 'Partial-coverage criterion' : 'Full-coverage criterion'}
        title={isPartial ? 'Partial-coverage criterion' : 'Full-coverage criterion'}
      >
        <span aria-hidden="true">{isPartial ? '◐' : '●'}</span>
      </span>
      {isLocality && (
        <span className="criterion-symbol" aria-label="Locality-derived criterion" title="Locality-derived criterion">
          <span aria-hidden="true">⌖</span>
        </span>
      )}
      {criterion.experimental && (
        <span className="criterion-symbol experimental-symbol" aria-label="Experimental criterion" title="Experimental criterion">
          <span aria-hidden="true">◇</span>
        </span>
      )}
    </span>
  )
}

function CountryLocalitySummary({ country }: { country: RankedCountryV2 }) {
  const assessment = country.assessments.locality
  if (assessment.status === 'NO_ACTIVE_LOCALITY_CRITERIA') return <span>-</span>
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

function CountryOpportunitySummary({
  country,
  catalog,
  detailed,
}: {
  country: RankedCountryV2
  catalog: OpportunityFilterCatalogV2
  detailed: boolean
}) {
  const definitions = new Map(
    catalog.definitions.map((definition) => [definition.id, definition]),
  )
  const evidence = country.assessments.opportunity.filter_evidence
  if (!country.assessments.opportunity.evaluated || !evidence.length) return null
  return (
    <div className="country-opportunity-summary">
      <span className="opportunity-match-badge">
        <span aria-hidden="true">✓</span> Matches {evidence.length}{' '}
        {evidence.length === 1 ? 'filter' : 'filters'}
      </span>
      {detailed && (
        <ul>
          {evidence.map((item) => {
            const content = OPPORTUNITY_STATE_CONTENT[item.state]
            return (
              <li key={item.filter_id}>
                <span aria-hidden="true">{content.icon}</span>{' '}
                {filterName(definitions.get(item.filter_id), item.filter_id, true)}:{' '}
                {content.label}
              </li>
            )
          })}
        </ul>
      )}
      {detailed && country.base_rank !== country.rank && (
        <small>Canonical base rank: {country.base_rank}</small>
      )}
    </div>
  )
}

type RankingViewProps = {
  ranking: RankingV2
  criteria: CatalogCriterionV2[]
  countries: CatalogV2['countries']
  opportunityCatalog: OpportunityFilterCatalogV2
  tfcCatalog: TfcCatalogV2 | null
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
  onClearComparison: () => void
  onCompare: () => void
  onOpenSources: () => void
  onRemoveOpportunityFilter: (filterId: string) => void
  onClearOpportunityFilters: () => void
  onEditSituation: () => void
}

export function RankingView({
  ranking,
  criteria,
  countries,
  opportunityCatalog,
  tfcCatalog,
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
  onClearComparison,
  onCompare,
  onOpenSources,
  onRemoveOpportunityFilter,
  onClearOpportunityFilters,
  onEditSituation,
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
          country.country.display_name.toLocaleLowerCase().startsWith(query) ||
          countryCode(country.country.entity_id)
            .toLocaleLowerCase()
            .startsWith(query)),
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
          <div className="ranking-title-line">
            <h2 id="rankings-heading">Country ranking</h2>
            <span>{ranking.rankings.length} {ranking.rankings.length === 1 ? 'country' : 'countries'}</span>
          </div>
          <p className="ranking-subtitle">
            Ranked by affinity score for your applied priorities{' '}
            <span
              className="context-help"
              title="Locality compatibility is advisory. Opportunity filters restrict results; neither changes the affinity score."
              aria-label="About ranking scope"
            >
              ⓘ
            </span>
          </p>
        </div>
        {isUpdating && (
          <span className="updating-state" role="status">
            Updating ranking…
          </span>
        )}
      </div>

      {ranking.assessments.opportunity.active_filter_ids.length > 0 && (
        <section className="opportunity-context" aria-label="Active opportunity filters">
          <strong>Opportunity filters:</strong>
          <div className="active-filter-chips">
            {ranking.assessments.opportunity.active_filter_ids.map((filterId) => {
              const definition = opportunityCatalog.definitions.find((item) => item.id === filterId)
              const name = filterName(definition, filterId, true)
              return (
                <button
                  type="button"
                  className="active-filter-chip"
                  disabled={isUpdating}
                  title={name}
                  aria-label={`Remove ${name} opportunity filter`}
                  onClick={() => onRemoveOpportunityFilter(filterId)}
                  key={filterId}
                >
                  {name} <span aria-hidden="true">×</span>
                </button>
              )
            })}
          </div>
          <span className="context-result-count">
            {ranking.assessments.opportunity.passing_country_count} matching
          </span>
          <span
            className="context-help"
            title="Selected filters require a verified strong signal and restrict which countries are shown."
            aria-label="About opportunity filters"
          >
            ⓘ
          </span>
          <button
            type="button"
            className="text-button"
            disabled={isUpdating}
            onClick={onClearOpportunityFilters}
          >
            Clear all
          </button>
        </section>
      )}

      {ranking.assessments.feasibility && tfcCatalog && (
        <FeasibilitySummary
          assessment={ranking.assessments.feasibility}
          catalog={tfcCatalog}
          isUpdating={isUpdating}
          onEditSituation={onEditSituation}
        />
      )}

      <div className="ranking-controls" role="search" aria-label="Filter and compare country ranking">
        <label>
          <span>Search countries</span>
          <CountrySearchAutocomplete
            countries={countries}
            value={searchTerm}
            placeholder="Country name or code"
            onChange={setSearchTerm}
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
        <label className="toggle-control">
          <input
            type="checkbox"
            checked={detailed}
            onChange={(event) => onDetailedChange(event.currentTarget.checked)}
          />
          <span>Show detailed evidence</span>
        </label>
        <div className="comparison-actions">
          {comparisonCountries.length > 0 && (
            <button
              type="button"
              className="button button-secondary clear-selection-button"
              disabled={isComparing}
              onClick={onClearComparison}
            >
              Clear selection
            </button>
          )}
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
      </div>
      <p id="comparison-limit" className="comparison-guidance" aria-live="polite">
        {comparisonNotice || 'Select 2–4 countries to compare.'}
      </p>

      {!ranking.rankings.length ? (
        <div className="empty-state opportunity-empty-state" role="status" aria-live="assertive">
          <h3>
            {ranking.assessments.opportunity.status === 'NO_COUNTRIES_MATCH'
              ? 'No country matches every selected opportunity filter'
              : 'No ranking results'}
          </h3>
          <p>
            {ranking.assessments.opportunity.status === 'NO_COUNTRIES_MATCH'
              ? 'This does not mean these opportunities are absent everywhere; some countries may have insufficient comparable evidence. Remove one filter to broaden the result.'
              : 'The API returned no eligible countries for the current data release.'}
          </p>
          {ranking.assessments.opportunity.status === 'NO_COUNTRIES_MATCH' && (
            <div className="empty-state-actions">
              {ranking.assessments.opportunity.active_filter_ids.map((filterId) => {
                const definition = opportunityCatalog.definitions.find(
                  (item) => item.id === filterId,
                )
                return (
                  <button
                    type="button"
                    className="button button-secondary"
                    disabled={isUpdating}
                    onClick={() => onRemoveOpportunityFilter(filterId)}
                    key={filterId}
                  >
                    Remove {filterName(definition, filterId, true)}
                  </button>
                )
              })}
            </div>
          )}
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
                  {ranking.assessments.opportunity.active_filter_ids.length > 0 && (
                    <th scope="col">Opportunity filters</th>
                  )}
                  {ranking.assessments.feasibility && tfcCatalog && (
                    <th scope="col">Feasibility checks</th>
                  )}
                  {detailed &&
                    criteria.map((criterion) => (
                      <th scope="col" key={criterion.id} title={compactDisplayName(criterion)}>
                        <span>{compactDisplayName(criterion)}</span>
                        <CriterionSymbols criterion={criterion} />
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
                      {ranking.assessments.opportunity.active_filter_ids.length > 0 && (
                        <td>
                          <CountryOpportunitySummary
                            country={country}
                            catalog={opportunityCatalog}
                            detailed={detailed}
                          />
                        </td>
                      )}
                      {ranking.assessments.feasibility && tfcCatalog && (
                        <td>
                          <CountryFeasibilitySummary
                            assessment={country.assessments.feasibility}
                            catalog={tfcCatalog}
                            detailed={detailed}
                          />
                        </td>
                      )}
                      {detailed &&
                        criteria.map((criterion) => {
                          const contribution = contributionFor(country, criterion.id)
                          return (
                            <td key={criterion.id} className="criterion-score-cell">
                              {contribution ? (
                                contribution.score.toFixed(1)
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
                  <CountryOpportunitySummary
                    country={country}
                    catalog={opportunityCatalog}
                    detailed={detailed}
                  />
                  {ranking.assessments.feasibility && tfcCatalog && (
                    <CountryFeasibilitySummary
                      assessment={country.assessments.feasibility}
                      catalog={tfcCatalog}
                      detailed
                    />
                  )}
                  {detailed && (
                    <div className="mobile-score-list">
                      {criteria.map((criterion) => {
                        const contribution = contributionFor(country, criterion.id)
                        return (
                          <div key={criterion.id}>
                            <strong>
                              {compactDisplayName(criterion)}
                              <CriterionSymbols criterion={criterion} />
                            </strong>
                            {contribution ? (
                              <span>{contribution.score.toFixed(1)}</span>
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
          Showing {visibleRankings.length} of {ranking.rankings.length} ranked{' '}
          {ranking.rankings.length === 1 ? 'country' : 'countries'} ·{' '}
          {ranking.assessments.coverage.excluded_countries.length} coverage excluded
          {ranking.assessments.opportunity.active_filter_ids.length > 0 && (
            <> · {ranking.assessments.opportunity.excluded_country_count} opportunity-filter excluded</>
          )}
        </span>
        <button className="release-link" onClick={onOpenSources}>
          Data release: {ranking.release_id}
        </button>
      </footer>

      <AssessmentSummary
        ranking={ranking}
        criteria={criteria}
        countries={countries}
        opportunityCatalog={opportunityCatalog}
        isUpdating={isUpdating}
        onSelectCountry={onSelectCountry}
        onClearOpportunityFilters={onClearOpportunityFilters}
      />
    </section>
  )
}
