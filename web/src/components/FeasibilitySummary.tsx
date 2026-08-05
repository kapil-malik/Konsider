import type {
  TfcAssessmentV2,
  TfcCatalogV2,
  TfcCountryAssessmentV2,
  TfcOutcomeV2,
} from '../api/types'
import { readableTfcCode, tfcName, tfcOutcomeContent } from '../tfcPresentation'

export function CountryFeasibilitySummary({
  assessment,
  catalog,
  detailed = false,
}: {
  assessment: TfcCountryAssessmentV2 | null | undefined
  catalog: TfcCatalogV2
  detailed?: boolean
}) {
  if (!assessment) return null
  const definitions = new Map(catalog.definitions.map((item) => [item.id, item]))
  return (
    <div className="country-feasibility-summary">
      {assessment.outcomes.map((outcome) => {
        const content = tfcOutcomeContent(outcome)
        return (
          <div className={`tfc-outcome-line tfc-tone-${content.tone}`} key={outcome.tfc_id}>
            <span aria-hidden="true">{content.icon}</span>
            <span>
              <strong>{content.label}</strong>
              {detailed && <small>{tfcName(definitions.get(outcome.tfc_id), outcome.tfc_id)}</small>}
            </span>
          </div>
        )
      })}
    </div>
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
  const evaluatedCount = assessment.status_counts.EVALUATED
  return (
    <section className="feasibility-result-summary" aria-labelledby="feasibility-summary-heading">
      <div className="feasibility-summary-heading">
        <div>
          <p className="eyebrow">Your declared scenario</p>
          <h3 id="feasibility-summary-heading">Feasibility checks</h3>
        </div>
        <span className="badge badge-scope">No affinity-score impact</span>
      </div>
      {assessment.execution_status === 'NOT_EXECUTED_NO_CONTEXT' ? (
        <p>Checks are selected, but no applicant or scenario context was supplied.</p>
      ) : (
        <p>
          {evaluatedCount} country-check results evaluated
          {inputCount > 0 ? ` · ${inputCount} need more information` : ''}. Results are bounded
          screenings, not immigration, admission, or employment decisions.
        </p>
      )}
      <div className="selected-tfc-list" aria-label="Selected feasibility checks">
        {selected.map((name) => <span key={name}>{name}</span>)}
      </div>
      {assessment.input_required_fields.length > 0 && (
        <div className="input-required-note" role="status">
          <strong>Additional inputs requested</strong>
          <span>{assessment.input_required_fields.map(readableTfcCode).join(', ')}</span>
        </div>
      )}
      <div className="feasibility-summary-footer">
        <span>
          {assessment.snapshot
            ? `Scenario date ${assessment.snapshot.evaluation_date} · Policy snapshot ${assessment.snapshot.tfc_release_id}`
            : 'No scenario snapshot created'}
        </span>
        <button type="button" className="text-button" disabled={isUpdating} onClick={onEditSituation}>
          Edit situation
        </button>
      </div>
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
