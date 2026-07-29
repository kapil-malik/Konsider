import { useQuery } from '@tanstack/react-query'
import { useEffect, useRef } from 'react'

import { fetchCountryDetails } from '../api/client'
import type {
  CountryDetailsV2,
  RankedCountryV2,
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
import { ErrorNotice } from './ErrorNotice'

type CountryDetailsProps = {
  countryCode: string
  selection: WeightSelectionV2
  rankingCountry: RankedCountryV2 | undefined
  countryName: string
  coverageExcluded: boolean
  onClose: () => void
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
  rankingCountry,
  countryName,
  coverageExcluded,
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
              Rank {rankingCountry.rank} · {formatScore(rankingCountry.total_score)} ·{' '}
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
