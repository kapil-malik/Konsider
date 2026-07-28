import { useQuery } from '@tanstack/react-query'
import { useEffect, useRef } from 'react'

import { fetchCountryMetric } from '../api/client'
import type { Catalog, ExcludedCountry, RankedCountry } from '../api/types'
import { formatObservation, formatScore, humanizeUnit } from '../preferences'
import { ErrorNotice } from './ErrorNotice'

type CountryDetailsProps = {
  countryCode: string
  rankingCountry: RankedCountry | undefined
  catalogCountry: Catalog['countries'][number] | undefined
  excludedCountry: ExcludedCountry | undefined
  onClose: () => void
}

function referencePeriod(start: string, end: string): string {
  return start === end ? start : `${start} to ${end}`
}

export function CountryDetails({
  countryCode,
  rankingCountry,
  catalogCountry,
  excludedCountry,
  onClose,
}: CountryDetailsProps) {
  const headingRef = useRef<HTMLHeadingElement>(null)
  const metricQuery = useQuery({
    queryKey: ['country-metrics', countryCode],
    queryFn: ({ signal }) => fetchCountryMetric(countryCode, signal),
  })

  useEffect(() => {
    if (metricQuery.data) headingRef.current?.focus()
  }, [metricQuery.data])

  return (
    <section className="country-details" aria-labelledby="country-details-heading">
      <div className="details-header">
        <div>
          <p className="eyebrow">Country details</p>
          <h2 id="country-details-heading" ref={headingRef} tabIndex={-1}>
            {rankingCountry?.country_name ?? catalogCountry?.display_name ?? countryCode}
          </h2>
          {rankingCountry && (
            <p>
              Rank {rankingCountry.rank} · {formatScore(rankingCountry.total_score)} ·{' '}
              {rankingCountry.region}
            </p>
          )}
          {!rankingCountry && catalogCountry && !excludedCountry && <p>{catalogCountry.region}</p>}
        </div>
        <button className="icon-button" aria-label="Close country details" onClick={onClose}>
          ×
        </button>
      </div>

      {excludedCountry && (
        <div className="unranked-country-notice" role="status">
          <strong>Not ranked for this profile</strong>
          <p>
            One or more active criteria do not have usable data for this country. Available
            full-coverage evidence is shown below without a partial affinity score.
          </p>
        </div>
      )}

      {metricQuery.isPending && (
        <div className="loading-block" role="status">
          Loading metric details…
        </div>
      )}
      {metricQuery.error && (
        <ErrorNotice error={metricQuery.error} onRetry={() => void metricQuery.refetch()} />
      )}
      {metricQuery.data && (
        <div className="metric-grid">
          {metricQuery.data.criteria.map((metric) => (
            <article className="metric-card" key={metric.criterion.id}>
              <div className="metric-card-heading">
                <div>
                  <p className="eyebrow">{metric.criterion.category}</p>
                  <h3>{metric.criterion.display_name}</h3>
                </div>
                <strong className="metric-score">{formatScore(metric.normalized_score)}</strong>
              </div>
              {metric.criterion.experimental && (
                <span className="badge badge-experimental">Experimental</span>
              )}
              <p>{metric.criterion.description}</p>
              <dl className="observation-list">
                {metric.observations.map((observation) => (
                  <div key={observation.observation_id}>
                    <dt>Observed value</dt>
                    <dd>
                      {formatObservation(observation.value)} {humanizeUnit(observation.unit)}
                    </dd>
                    <dt>Reference period</dt>
                    <dd>{referencePeriod(observation.reference_start, observation.reference_end)}</dd>
                    {observation.quality_flags.length > 0 && (
                      <>
                        <dt>Quality note</dt>
                        <dd>{observation.quality_flags.join(', ')}</dd>
                      </>
                    )}
                  </div>
                ))}
              </dl>
              <div className="metric-notes">
                {metric.criterion.caveats.map((item) => (
                  <p key={item}>
                    <strong>Caveat:</strong> {item}
                  </p>
                ))}
                {metric.criterion.quality_limitations.map((item) => (
                  <p key={item}>
                    <strong>Limitation:</strong> {item}
                  </p>
                ))}
              </div>
              <a
                className="source-link"
                href={metric.source.canonical_page_url}
                target="_blank"
                rel="noreferrer"
              >
                View {metric.source.publisher} source (opens in a new tab)
              </a>
              <details>
                <summary>How this metric was handled</summary>
                <p>{metric.criterion.interpretation}</p>
                <p>
                  Scoring method: <code>{metric.scoring_method_version}</code>
                </p>
                <p>{metric.source.attribution}</p>
              </details>
            </article>
          ))}
        </div>
      )}
    </section>
  )
}
