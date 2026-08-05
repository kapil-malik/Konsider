import { useQuery } from '@tanstack/react-query'
import { useEffect, useRef } from 'react'

import { fetchCountryDetails } from '../api/client'
import type {
  CountryDetailsV2,
  OpportunityFilterCatalogV2,
  RankedCountryV2,
  TfcCatalogV2,
  WeightSelectionV2,
} from '../api/types'
import {
  LOCALITY_CONTENT,
  localityName,
  readableCode,
} from '../localityPresentation'
import {
  formatObservation,
  formatScore,
  humanizeUnit,
} from '../preferences'
import {
  EDUCATION_SHARED_LIMITATION,
  OPPORTUNITY_STATE_CONTENT,
  filterName,
  opportunityExplanation,
  routeSummary,
} from '../opportunityPresentation'
import { ErrorNotice } from './ErrorNotice'
import {
  CrossFeatureExplanation,
  FeasibilityEvidence,
} from './FeasibilitySummary'

type CountryDetailsProps = {
  countryCode: string
  selection: WeightSelectionV2
  opportunityCatalog: OpportunityFilterCatalogV2
  tfcCatalog: TfcCatalogV2 | null
  rankingCountry: RankedCountryV2 | undefined
  countryName: string
  coverageExcluded: boolean
  opportunityExcluded: boolean
  opportunityBaseRank: number | null
  onClose: () => void
}

function OpportunityEvidence({
  details,
  catalog,
}: {
  details: CountryDetailsV2
  catalog: OpportunityFilterCatalogV2
}) {
  if (!details.opportunity_filters.length) return null
  const definitions = new Map(
    catalog.definitions.map((definition) => [definition.id, definition]),
  )
  return (
    <section className="country-opportunity-section" aria-labelledby="country-opportunity-heading">
      <div className="section-heading-row">
        <div>
          <p className="eyebrow">Selected destination evidence</p>
          <h3 id="country-opportunity-heading">Opportunity filters</h3>
        </div>
        <span className="badge badge-scope">No affinity-score impact</span>
      </div>
      <p>
        These states explain the selected filters. They do not estimate personal access to jobs,
        licences, visas, admissions, credentials, or programmes.
      </p>
      <div className="opportunity-evidence-grid">
        {details.opportunity_filters.map((evidence) => {
          const definition = definitions.get(evidence.filter_id)
          const content = OPPORTUNITY_STATE_CONTENT[evidence.state]
          const route = routeSummary(evidence)
          const sourceById = new Map(
            (definition?.source_vintage ?? []).map((source) => [source.source_id, source]),
          )
          const limitations = [
            ...(definition?.limitations ?? []),
            ...evidence.limitations,
            ...(definition?.category === 'EDUCATION'
              ? [EDUCATION_SHARED_LIMITATION]
              : []),
          ].filter((item, index, all) => all.indexOf(item) === index)
          return (
            <article
              className={`opportunity-evidence-card state-${content.className}`}
              key={evidence.filter_id}
            >
              <div className="opportunity-evidence-heading">
                <div>
                  <p className="eyebrow">
                    {definition?.category === 'EDUCATION'
                      ? 'Research-university ecosystem'
                      : 'Career ecosystem'}
                  </p>
                  <h4>{filterName(definition, evidence.filter_id)}</h4>
                </div>
                <span className={`opportunity-state-badge state-${content.className}`}>
                  <span aria-hidden="true">{content.icon}</span> {content.label}
                </span>
              </div>
              <p>{opportunityExplanation(evidence, definition)}</p>
              <dl className="opportunity-evidence-facts">
                <div>
                  <dt>Confidence</dt>
                  <dd>{evidence.confidence_band}</dd>
                </div>
                <div>
                  <dt>Evidence period</dt>
                  <dd>{evidence.reference_period ?? 'No comparable period available'}</dd>
                </div>
                <div>
                  <dt>Establishing route</dt>
                  <dd>{route || 'No establishing route'}</dd>
                </div>
              </dl>
              <div className="opportunity-source-list">
                <strong>Sources</strong>
                {evidence.source_ids.length ? (
                  <ul>
                    {evidence.source_ids.map((sourceId) => {
                      const source = sourceById.get(sourceId)
                      return (
                        <li key={sourceId}>
                          {source?.publisher ?? sourceId}
                          {source?.source_version ? ` · ${source.source_version}` : ''}
                          {source?.attribution ? ` · ${source.attribution}` : ''}
                        </li>
                      )
                    })}
                  </ul>
                ) : (
                  <p>No comparable source evidence is currently available.</p>
                )}
              </div>
              {limitations.length > 0 && (
                <details className="opportunity-limitations">
                  <summary>Limitations</summary>
                  <ul>
                    {limitations.map((limitation) => (
                      <li key={limitation}>{limitation}</li>
                    ))}
                  </ul>
                </details>
              )}
              <p className="methodology-reference">
                Methodology reference: <code>{evidence.documentation_ref}</code>
              </p>
            </article>
          )
        })}
      </div>
    </section>
  )
}

function LocalityAssessment({
  details,
  rankingCountry,
}: {
  details: CountryDetailsV2
  rankingCountry: RankedCountryV2 | undefined
}) {
  const excludedAssessment =
    details.assessments.coverage.excluded_countries.find(
      (item) => item.country.entity_id === details.country.entity_id,
    )?.locality_assessment
  const countryAssessment =
    rankingCountry?.assessments.locality ?? excludedAssessment
  const contributions = details.criteria
    .map((item) => item.evidence.contribution)
    .filter((item): item is NonNullable<typeof item> => item !== null)
  const bestCommon = localityName(
    countryAssessment?.best_common_locality_entity_id ?? null,
    contributions,
  )
  const status =
    countryAssessment?.status ??
    (details.assessments.locality.status === 'MIXED_COUNTRY_RESULTS'
      ? 'MIXED_COUNTRY_RESULTS'
      : details.assessments.locality.status)
  return (
    <div className="country-locality-assessment" role="status">
      <span className="assessment-icon" aria-hidden="true">
        ⌖
      </span>
      <div>
        <strong>{LOCALITY_CONTENT[status].label}</strong>
        <p>{LOCALITY_CONTENT[status].message}</p>
        {bestCommon && <p>Best common locality: {bestCommon}</p>}
        {countryAssessment?.reasons.length ? (
          <p>
            Server reasons:{' '}
            {countryAssessment.reasons
              .map((reason) => readableCode(reason.code))
              .join(', ')}
          </p>
        ) : null}
      </div>
    </div>
  )
}

export function CountryDetails({
  countryCode,
  selection,
  opportunityCatalog,
  tfcCatalog,
  rankingCountry,
  countryName,
  coverageExcluded,
  opportunityExcluded,
  opportunityBaseRank,
  onClose,
}: CountryDetailsProps) {
  const headingRef = useRef<HTMLHeadingElement>(null)
  const detailsQuery = useQuery({
    queryKey: ['country-details', countryCode, selection],
    queryFn: ({ signal }) => fetchCountryDetails(countryCode, selection, signal),
  })

  useEffect(() => {
    if (detailsQuery.data) headingRef.current?.focus()
  }, [detailsQuery.data])

  return (
    <section className="country-details" aria-labelledby="country-details-heading">
      <div className="details-header">
        <div>
          <p className="eyebrow">Country details</p>
          <h2 id="country-details-heading" ref={headingRef} tabIndex={-1}>
            {detailsQuery.data?.country.display_name ?? countryName}
          </h2>
          {rankingCountry && (
            <p>
              Rank {rankingCountry.rank}
              {rankingCountry.base_rank !== rankingCountry.rank
                ? ` · Base rank ${rankingCountry.base_rank}`
                : ''}{' '}
              · {formatScore(rankingCountry.total_score)} ·{' '}
              {rankingCountry.country.region ?? countryCode}
            </p>
          )}
        </div>
        <button className="icon-button" aria-label="Close country details" onClick={onClose}>
          ×
        </button>
      </div>

      {coverageExcluded && (
        <div className="unranked-country-notice" role="status">
          <strong>Coverage excluded · not ranked</strong>
          <p>
            One or more active criteria lack usable evidence. Available criterion evidence is
            shown without a partial affinity score.
          </p>
        </div>
      )}

      {opportunityExcluded && (
        <div className="opportunity-excluded-notice" role="status">
          <strong>Excluded by selected opportunity filters · not in filtered ranking</strong>
          <p>
            Canonical base rank {opportunityBaseRank ?? 'unavailable'} is retained. The affinity
            score and ordering evidence are unchanged; the selected filter evidence is shown
            below.
          </p>
        </div>
      )}

      {detailsQuery.isPending && (
        <div className="loading-block" role="status">
          Loading country evidence…
        </div>
      )}
      {detailsQuery.error && (
        <ErrorNotice error={detailsQuery.error} onRetry={() => void detailsQuery.refetch()} />
      )}
      {detailsQuery.data && (
        <>
          <LocalityAssessment
            details={detailsQuery.data}
            rankingCountry={rankingCountry}
          />
          <OpportunityEvidence
            details={detailsQuery.data}
            catalog={opportunityCatalog}
          />
          {tfcCatalog && (
            <>
              <CrossFeatureExplanation
                assessment={detailsQuery.data.feasibility}
                opportunityEvidence={detailsQuery.data.opportunity_filters}
                localityStatus={
                  rankingCountry?.assessments.locality.status ??
                  detailsQuery.data.assessments.coverage.excluded_countries.find(
                    (item) => item.country.entity_id === detailsQuery.data?.country.entity_id,
                  )?.locality_assessment.status ??
                  detailsQuery.data.assessments.locality.status
                }
                finalAggregate={rankingCountry?.total_score ?? null}
              />
              <FeasibilityEvidence
                assessment={detailsQuery.data.feasibility}
                catalog={tfcCatalog}
              />
            </>
          )}
          <div className="metric-grid">
            {detailsQuery.data.criteria.map(({ criterion, evidence }) => {
              const contribution = evidence.contribution
              const localityDerived =
                contribution?.derivation === 'AGGREGATED_FROM_LOCALITIES'
              return (
                <article
                  className={`metric-card${evidence.outcome !== 'valid' ? ' metric-unavailable' : ''}`}
                  key={criterion.id}
                >
                  <div className="metric-card-heading">
                    <div>
                      <p className="eyebrow">{criterion.category}</p>
                      <h3>{criterion.display_name}</h3>
                    </div>
                    {contribution ? (
                      <strong className="metric-score">
                        {formatScore(contribution.score)}
                      </strong>
                    ) : (
                      <span className="badge badge-unavailable">! {readableCode(evidence.outcome)}</span>
                    )}
                  </div>
                  <div className="badge-row">
                    <span className="badge badge-scope">
                      {localityDerived ? '⌖ Locality-derived' : '● National'}
                    </span>
                    {criterion.experimental && (
                      <span className="badge badge-experimental">◇ Experimental</span>
                    )}
                  </div>
                  <p>{criterion.description}</p>
                  {!contribution && (
                    <div className="unavailable-explanation">
                      <strong>Unavailable active criterion</strong>
                      <p>
                        {evidence.reason_codes.length
                          ? evidence.reason_codes.map(readableCode).join(', ')
                          : 'No usable result was supplied.'}
                      </p>
                    </div>
                  )}
                  {contribution && (
                    <>
                      <dl className="observation-list">
                        <div>
                          <dt>Derivation</dt>
                          <dd>
                            {localityDerived
                              ? 'Country score aggregated from locality evidence'
                              : 'Direct national result'}
                          </dd>
                          {localityDerived && (
                            <>
                              <dt>Contributing localities</dt>
                              <dd>
                                {contribution.contributing_localities
                                  .map(
                                    (item) =>
                                      `${item.locality.display_name}: ${item.input_score.toFixed(1)}`,
                                  )
                                  .join(', ')}
                              </dd>
                              <dt>Aggregation policy</dt>
                              <dd>
                                {contribution.aggregation_policy?.method.replaceAll('_', ' ')} ·{' '}
                                <code>{contribution.aggregation_policy?.policy_id}</code>
                              </dd>
                            </>
                          )}
                          {contribution.observations.map((observation) => (
                            <div key={observation.observation_id} className="observation-entry">
                              <dt>Observed value</dt>
                              <dd>
                                {formatObservation(observation.value)}{' '}
                                {humanizeUnit(observation.unit)}
                              </dd>
                              <dt>Reference period</dt>
                              <dd>
                                {observation.reference_start} to {observation.reference_end}
                              </dd>
                            </div>
                          ))}
                        </div>
                      </dl>
                      <div className="metric-notes">
                        {criterion.caveats.map((item) => (
                          <p key={item}>
                            <strong>Caveat:</strong> {item}
                          </p>
                        ))}
                        {criterion.quality_limitations.map((item) => (
                          <p key={item}>
                            <strong>Limitation:</strong> {item}
                          </p>
                        ))}
                      </div>
                      <div className="source-links">
                        {contribution.sources.map((source) =>
                          source.canonical_page_url ? (
                            <a
                              className="source-link"
                              href={source.canonical_page_url}
                              target="_blank"
                              rel="noreferrer"
                              key={`${source.source_id}:${source.source_version}`}
                            >
                              View {source.publisher ?? source.source_id} source (opens in a new
                              tab)
                            </a>
                          ) : (
                            <span key={`${source.source_id}:${source.source_version}`}>
                              Source lineage: {source.source_id} · {source.source_version}
                            </span>
                          ),
                        )}
                      </div>
                    </>
                  )}
                </article>
              )
            })}
          </div>
        </>
      )}
    </section>
  )
}
