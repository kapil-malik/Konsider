import type { CatalogCriterion, Ranking } from '../api/types'

type UncertaintySummaryProps = {
  ranking: Ranking
  criteria: CatalogCriterion[]
  showingBaseline: boolean
  baselineAvailable: boolean
  baselineLoading: boolean
  onToggleBaseline: () => void
  onSelectCountry: (countryCode: string) => void
}

const STATUS_CONTENT: Record<
  Ranking['uncertainty_status'],
  { label: string; message: string; prominence: 'neutral' | 'mild' | 'caution' | 'strong' }
> = {
  NO_PARTIAL_CRITERIA_ACTIVE: {
    label: 'Full-coverage ranking',
    message: 'No limited-coverage criterion is active at the selected importance.',
    prominence: 'neutral',
  },
  FULL_COVERAGE: {
    label: 'Full coverage',
    message: 'Every country has data for all active criteria.',
    prominence: 'neutral',
  },
  ROBUST_TOP_K: {
    label: 'Robust top results',
    message:
      'Some countries were excluded because of unavailable data. Even with the best possible missing scores, none could enter the current top results.',
    prominence: 'mild',
  },
  POTENTIALLY_AFFECTED: {
    label: 'Recommendations may be affected',
    message:
      'One or more excluded countries could potentially enter the current top results. Treat these recommendations as incomplete.',
    prominence: 'caution',
  },
  BASELINE_TOP_K_EXCLUDED: {
    label: 'A baseline top country is excluded',
    message:
      'A country that appeared in the full-coverage top results is excluded because an important selected criterion lacks data.',
    prominence: 'strong',
  },
  COVERAGE_LIMIT_EXCEEDED: {
    label: 'Coverage limit reached',
    message:
      'The limited-coverage result was not generated because too many countries would be excluded. The table shows the full-coverage baseline.',
    prominence: 'strong',
  },
}

const readableCode = (value: string) =>
  value
    .toLocaleLowerCase()
    .replaceAll('_', ' ')
    .replace(/^\w/, (character) => character.toLocaleUpperCase())

export function UncertaintySummary({
  ranking,
  criteria,
  showingBaseline,
  baselineAvailable,
  baselineLoading,
  onToggleBaseline,
  onSelectCountry,
}: UncertaintySummaryProps) {
  const criterionNames = new Map(criteria.map((criterion) => [criterion.id, criterion.display_name]))
  const status = STATUS_CONTENT[ranking.uncertainty_status]
  const activePccNames = ranking.active_pcc_ids.map(
    (criterionId) => criterionNames.get(criterionId) ?? criterionId,
  )
  const canShowBaseline =
    ranking.active_pcc_ids.length > 0 &&
    ranking.uncertainty_status !== 'COVERAGE_LIMIT_EXCEEDED'
  const rankedCountryCount =
    ranking.uncertainty_status === 'COVERAGE_LIMIT_EXCEEDED'
      ? ranking.stable_universe_size
      : ranking.eligible_universe_size

  return (
    <div className="uncertainty-block">
      <div
        className={`uncertainty-notice uncertainty-${status.prominence}`}
        role="status"
        aria-live="polite"
        aria-label={`Ranking coverage status: ${status.label}`}
      >
        <span className="uncertainty-icon" aria-hidden="true">
          {status.prominence === 'strong'
            ? '!'
            : status.prominence === 'caution'
              ? '△'
              : 'ⓘ'}
        </span>
        <div>
          <strong>{status.label}</strong>
          <p>{status.message}</p>
        </div>
      </div>

      <dl className="ranking-summary-grid">
        <div>
          <dt>Countries ranked</dt>
          <dd>
            {rankedCountryCount} of {ranking.stable_universe_size}
          </dd>
        </div>
        <div>
          <dt>Limited criteria active</dt>
          <dd>{activePccNames.length ? activePccNames.join(', ') : 'None'}</dd>
        </div>
        <div>
          <dt>Countries excluded</dt>
          <dd>{ranking.excluded_country_count}</dd>
        </div>
        <div>
          <dt>Robustness check</dt>
          <dd>Top {ranking.robustness_k}</dd>
        </div>
      </dl>

      {canShowBaseline && (
        <div className="baseline-control">
          <button
            className="button button-secondary"
            aria-pressed={showingBaseline}
            disabled={baselineLoading}
            onClick={onToggleBaseline}
          >
            {baselineLoading
              ? 'Loading baseline…'
              : showingBaseline
                ? 'Return to conditional ranking'
                : 'View full-coverage baseline'}
          </button>
          <p>
            {showingBaseline
              ? `Showing all ${ranking.stable_universe_size} countries using global-core criteria only.`
              : 'The conditional result remains the primary recommendation.'}
          </p>
          {showingBaseline && !baselineAvailable && (
            <span className="sr-only">The baseline is loading.</span>
          )}
        </div>
      )}

      {ranking.excluded_countries.length > 0 && (
        <details className="excluded-country-details">
          <summary>
            Review {ranking.excluded_country_count} excluded{' '}
            {ranking.excluded_country_count === 1 ? 'country' : 'countries'}
          </summary>
          <div className="excluded-country-list">
            {ranking.excluded_countries.map((country) => (
              <article key={country.country_code} className="excluded-country-card">
                <div className="excluded-country-heading">
                  <div>
                    <button
                      className="text-button"
                      onClick={() => onSelectCountry(country.country_code)}
                    >
                      {country.country_name}
                    </button>
                    <span>Not ranked for this profile</span>
                  </div>
                  {country.baseline_top_k_member && (
                    <span className="badge badge-baseline">Baseline top {ranking.robustness_k}</span>
                  )}
                </div>
                <dl>
                  <div>
                    <dt>Full-coverage baseline</dt>
                    <dd>
                      Rank {country.r0_rank}, score {country.r0_score.toFixed(2)}
                    </dd>
                  </div>
                  <div>
                    <dt>Missing or stale data</dt>
                    <dd>
                      {country.non_ready_criteria
                        .map((item) => {
                          const name = criterionNames.get(item.criterion_id) ?? item.criterion_id
                          const reasons = item.reason_codes.map(readableCode).join(', ')
                          return `${name}: ${readableCode(item.outcome)}${reasons ? ` — ${reasons}` : ''}`
                        })
                        .join('; ')}
                    </dd>
                  </div>
                  <div>
                    <dt>Optimistic upper bound</dt>
                    <dd>
                      {country.optimistic_upper_bound === null
                        ? 'Not calculated'
                        : country.optimistic_upper_bound.toFixed(2)}
                    </dd>
                  </div>
                  <div>
                    <dt>Could enter top {ranking.robustness_k}</dt>
                    <dd>
                      {country.could_enter_top_k === null
                        ? 'Not assessed'
                        : country.could_enter_top_k
                          ? 'Yes'
                          : 'No'}
                    </dd>
                  </div>
                </dl>
              </article>
            ))}
          </div>
        </details>
      )}
    </div>
  )
}
