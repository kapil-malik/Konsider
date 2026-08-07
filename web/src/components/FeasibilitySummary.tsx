import type {
  OpportunityFilterEvidenceV2,
  TfcAssessmentV2,
  TfcCatalogV2,
  TfcCountryAssessmentV2,
  TfcOutcomeV2,
} from '../api/types'
import { crossFeatureExplanations } from '../crossFeaturePresentation'
import { readableTfcCode, tfcName, tfcOutcomeContent } from '../tfcPresentation'

export function CountryFeasibilitySummary({
  assessment,
  catalog,
  detailed = false,
  showEvidence = false,
}: {
  assessment: TfcCountryAssessmentV2 | null | undefined
  catalog: TfcCatalogV2
  detailed?: boolean
  showEvidence?: boolean
}) {
  if (!assessment) return null
  const definitions = new Map(catalog.definitions.map((item) => [item.id, item]))
  return (
    <div className="country-feasibility-summary">
      {assessment.outcomes.map((outcome) => {
        const content = tfcOutcomeContent(outcome)
        const definition = definitions.get(outcome.tfc_id)
        return (
          <div className={`tfc-outcome-line tfc-tone-${content.tone}`} key={outcome.tfc_id}>
            <span aria-hidden="true">{content.icon}</span>
            <span>
              <strong>{content.label}</strong>
              {detailed && <small>{tfcName(definition, outcome.tfc_id)}</small>}
              {showEvidence && <OutcomeEvidenceSummary outcome={outcome} />}
              {showEvidence && definition && (
                <small>
                  Check evidence effective {definition.effective_from} · review by{' '}
                  {definition.stale_after}
                </small>
              )}
            </span>
          </div>
        )
      })}
    </div>
  )
}

export function OutcomeEvidenceSummary({ outcome }: { outcome: TfcOutcomeV2 }) {
  const result = outcome.result
  if (!result) return null
  if ('routes' in result) {
    return (
      <span className="tfc-comparison-evidence">
        {result.routes.map((route) => (
          <small key={`${route.route_id}:${route.jurisdiction_id}`}>
            {route.route_name} · effective {route.effective_from} · sources{' '}
            {route.source_ids.join(', ')}
          </small>
        ))}
      </span>
    )
  }
  return (
    <span className="tfc-comparison-evidence">
      <small>
        {result.value ?? `${result.minimum}–${result.maximum}`}{' '}
        {result.currency ?? result.unit} · {result.period.toLocaleLowerCase()} · effective{' '}
        {result.effective_from}
      </small>
    </span>
  )
}

export function CrossFeatureExplanation({
  assessment,
  opportunityEvidence,
  localityStatus,
  finalAggregate,
}: {
  assessment: TfcCountryAssessmentV2 | null | undefined
  opportunityEvidence: OpportunityFilterEvidenceV2[]
  localityStatus:
    | 'NO_ACTIVE_LOCALITY_CRITERIA'
    | 'BELOW_ANALYSIS_THRESHOLD'
    | 'ONE_ACTIVE_LOCALITY_CRITERION'
    | 'COMMON_LOCALITY_AVAILABLE'
    | 'PARTIAL_OVERLAP'
    | 'NO_COMMON_LOCALITY'
    | 'INSUFFICIENT_LOCALITY_EVIDENCE'
    | 'MIXED_COUNTRY_RESULTS'
  finalAggregate: number | null
}) {
  if (!assessment) return null
  const explanations = crossFeatureExplanations({
    assessment,
    opportunityEvidence,
    localityStatus,
    finalAggregate,
  })
  if (!explanations.length) return null
  return (
    <aside className="cross-feature-explanation" aria-label="How these results relate">
      {explanations.map((explanation) => (
        <p key={explanation}>{explanation}</p>
      ))}
    </aside>
  )
}

export function FeasibilitySummary({
  assessment,
  catalog,
  isUpdating,
  onEditSituation,
}: {
  assessment: TfcAssessmentV2
  catalog: TfcCatalogV2
  isUpdating: boolean
  onEditSituation: () => void
}) {
  const definitions = new Map(catalog.definitions.map((item) => [item.id, item]))
  const selected = assessment.selected_tfc_ids.map((id) =>
    tfcName(definitions.get(id), id),
  )
  const inputCount = assessment.status_counts.INPUT_REQUIRED
  return (
    <section className="scenario-context" aria-label="Declared scenario">
      <strong>Scenario:</strong>
      <div className="selected-tfc-list" aria-label="Selected feasibility checks">
        {selected.map((name) => <span key={name}>{name}</span>)}
      </div>
      {inputCount > 0 && <span className="scenario-input-note">{inputCount} need more information</span>}
      <span
        className="context-help"
        title="Feasibility checks are bounded screenings and do not change affinity scores."
        aria-label="About feasibility checks"
      >
        ⓘ
      </span>
      <button type="button" className="text-button" disabled={isUpdating} onClick={onEditSituation}>
        Edit
      </button>
    </section>
  )
}

function RouteResult({ outcome }: { outcome: TfcOutcomeV2 }) {
  const result = outcome.result
  if (!result || !('routes' in result)) return null
  return (
    <div className="route-result-details">
      <strong>Routes evaluated</strong>
      <ul>
        {result.routes.map((route) => (
          <li key={`${route.route_id}:${route.jurisdiction_id}`}>
            <div>
              <strong>{route.route_name}</strong>
              <span>{readableTfcCode(route.classification)} · effective {route.effective_from}</span>
            </div>
            <details>
              <summary>Conditions and sources</summary>
              <ul>
                {route.conditions.map((condition) => (
                  <li key={condition.condition_id}>
                    {readableTfcCode(condition.condition_id)}: {readableTfcCode(condition.status)}
                  </li>
                ))}
              </ul>
              <p>Sources: {route.source_ids.join(', ')}</p>
            </details>
          </li>
        ))}
      </ul>
      <p className="legal-disclaimer">{result.legal_impossibility_disclaimer}</p>
    </div>
  )
}

function MetricResult({ outcome }: { outcome: TfcOutcomeV2 }) {
  const result = outcome.result
  if (!result || !('metric_id' in result)) return null
  return (
    <dl className="tfc-metric-result">
      <div><dt>Estimate</dt><dd>{result.value ?? `${result.minimum}–${result.maximum}`} {result.currency ?? result.unit} · {result.period.toLocaleLowerCase()}</dd></div>
      <div><dt>Effective from</dt><dd>{result.effective_from}</dd></div>
      <div><dt>Assumptions</dt><dd>{result.assumptions.join(', ') || 'None listed'}</dd></div>
    </dl>
  )
}

export function FeasibilityEvidence({
  assessment,
  catalog,
}: {
  assessment: TfcCountryAssessmentV2 | null | undefined
  catalog: TfcCatalogV2
}) {
  if (!assessment) return null
  const definitions = new Map(catalog.definitions.map((item) => [item.id, item]))
  return (
    <section className="country-feasibility-section" aria-labelledby="country-feasibility-heading">
      <div className="section-heading-row">
        <div>
          <p className="eyebrow">Your situation</p>
          <h3 id="country-feasibility-heading">Feasibility checks</h3>
        </div>
        <span className="badge badge-scope">Base rank {assessment.base_rank}</span>
      </div>
      <p>These results use the same declared scenario as the ranking and do not change affinity.</p>
      <div className="tfc-evidence-grid">
        {assessment.outcomes.map((outcome) => {
          const definition = definitions.get(outcome.tfc_id)
          const content = tfcOutcomeContent(outcome)
          return (
            <article className={`tfc-evidence-card tfc-tone-${content.tone}`} key={outcome.tfc_id}>
              <div className="tfc-evidence-heading">
                <div><p className="eyebrow">{definition?.check_kind.replaceAll('_', ' ')}</p><h4>{tfcName(definition, outcome.tfc_id)}</h4></div>
                <span className="tfc-status-badge"><span aria-hidden="true">{content.icon}</span> {content.label}</span>
              </div>
              {outcome.input_required_fields.length > 0 && (
                <div className="input-required-note"><strong>More information requested</strong><span>{outcome.input_required_fields.map(readableTfcCode).join(', ')}</span></div>
              )}
              <RouteResult outcome={outcome} />
              <MetricResult outcome={outcome} />
              {definition && (
                <details className="tfc-limitations"><summary>Sources and limitations</summary><p>Evidence effective {definition.effective_from}; review by {definition.stale_after}.</p><ul>{definition.source_summary.map((source) => <li key={source.source_id}>{source.publisher} · verified {source.verified_at}</li>)}</ul><ul>{definition.limitations.map((item) => <li key={item}>{item}</li>)}</ul></details>
              )}
            </article>
          )
        })}
      </div>
    </section>
  )
}
