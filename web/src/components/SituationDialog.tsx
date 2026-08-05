import { useEffect, useMemo, useRef, useState, type ChangeEvent } from 'react'

import type { TfcCatalogV2, TfcFieldDefinitionV2 } from '../api/types'
import {
  MAX_SCENARIOS,
  activeScenario,
  cloneSituation,
  createEmptySituation,
  createScenario,
  exportSituation,
  parseSituation,
  recommendedTfcs,
  situationSummary,
  validateSituation,
  type SituationDocument,
  type SituationScenario,
} from '../situation'

const STEPS = ['Purpose', 'Checks', 'Details', 'Review'] as const

type SituationDialogProps = {
  open: boolean
  situation: SituationDocument
  catalog: TfcCatalogV2
  remembered: boolean
  onClose: () => void
  onApply: (situation: SituationDocument, remember: boolean) => void
  onClearRemembered: () => void
}

const fieldMap = (catalog: TfcCatalogV2) =>
  new Map(catalog.field_registry.map((field) => [field.field_id, field]))

function FieldHelp({ field }: { field: TfcFieldDefinitionV2 | undefined }) {
  if (!field) return null
  return (
    <span className="field-help">
      {field.help_text} <span className="sensitivity-label">{field.sensitivity.replaceAll('_', ' ')}</span>
    </span>
  )
}

function purposeLabel(purpose: SituationScenario['purpose']) {
  return {
    WORK: 'Work',
    STUDY: 'Study',
    FAMILY: 'Family',
    EXPLORATION: 'Explore',
  }[purpose]
}

export function SituationDialog({
  open,
  situation,
  catalog,
  remembered,
  onClose,
  onApply,
  onClearRemembered,
}: SituationDialogProps) {
  const [draft, setDraft] = useState(() => cloneSituation(situation))
  const [step, setStep] = useState(0)
  const [remember, setRemember] = useState(remembered)
  const [errors, setErrors] = useState<string[]>([])
  const [importError, setImportError] = useState('')
  const [pendingImport, setPendingImport] = useState<SituationDocument | null>(null)
  const [confirmClear, setConfirmClear] = useState(false)
  const dialogRef = useRef<HTMLDivElement>(null)
  const headingRef = useRef<HTMLHeadingElement>(null)

  useEffect(() => {
    if (!open) return
    setDraft(cloneSituation(situation))
    setRemember(remembered)
    setStep(0)
    setErrors([])
    setImportError('')
    setPendingImport(null)
    setConfirmClear(false)
    window.requestAnimationFrame(() => headingRef.current?.focus())
  }, [open, remembered, situation])

  useEffect(() => {
    if (!open) return
    const handleKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        event.preventDefault()
        onClose()
      }
      if (event.key !== 'Tab') return
      const focusable = dialogRef.current?.querySelectorAll<HTMLElement>(
        'button:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex="0"]',
      )
      if (!focusable?.length) return
      const first = focusable[0]
      const last = focusable[focusable.length - 1]
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault()
        last.focus()
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault()
        first.focus()
      }
    }
    document.addEventListener('keydown', handleKey)
    return () => document.removeEventListener('keydown', handleKey)
  }, [onClose, open])

  const scenario = activeScenario(draft)
  const definitions = useMemo(
    () => new Map(catalog.definitions.map((definition) => [definition.id, definition])),
    [catalog.definitions],
  )
  const fields = useMemo(() => fieldMap(catalog), [catalog])
  const selectedDefinitions = scenario.selectedTfcIds
    .map((id) => definitions.get(id))
    .filter((value): value is NonNullable<typeof value> => Boolean(value))
  const requiredFieldIds = new Set(
    selectedDefinitions.flatMap((definition) =>
      definition.input_requirements
        .filter((requirement) => requirement.requirement === 'ALWAYS_REQUIRED')
        .map((requirement) => requirement.field_id),
    ),
  )
  const recommendations = recommendedTfcs(catalog, scenario.purpose)

  const updateScenario = (change: Partial<SituationScenario>) => {
    setDraft((current) => ({
      ...current,
      scenarios: current.scenarios.map((item) =>
        item.id === current.active_scenario_id ? { ...item, ...change } : item,
      ),
    }))
  }

  const addScenario = () => {
    if (draft.scenarios.length >= MAX_SCENARIOS) return
    const next = createScenario(`Scenario ${draft.scenarios.length + 1}`, scenario.purpose)
    setDraft((current) => ({
      ...current,
      scenarios: [...current.scenarios, next],
      active_scenario_id: next.id,
    }))
  }

  const duplicateScenario = () => {
    if (draft.scenarios.length >= MAX_SCENARIOS) return
    const next = {
      ...scenario,
      id: createScenario().id,
      name: `${scenario.name} copy`,
    }
    setDraft((current) => ({
      ...current,
      scenarios: [...current.scenarios, next],
      active_scenario_id: next.id,
    }))
  }

  const removeScenario = () => {
    if (draft.scenarios.length === 1) return
    setDraft((current) => {
      const scenarios = current.scenarios.filter(
        (item) => item.id !== current.active_scenario_id,
      )
      return { ...current, scenarios, active_scenario_id: scenarios[0].id }
    })
  }

  const nextStep = () => {
    setErrors([])
    setStep((current) => Math.min(current + 1, STEPS.length - 1))
  }

  const apply = () => {
    const validation = validateSituation(draft)
    if (validation.length) {
      setErrors(validation)
      return
    }
    onApply(cloneSituation(draft), remember)
  }

  const download = () => {
    const blob = new Blob([exportSituation(draft)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const anchor = document.createElement('a')
    anchor.href = url
    anchor.download = 'konsider-situation.json'
    anchor.click()
    URL.revokeObjectURL(url)
  }

  const readImport = async (event: ChangeEvent<HTMLInputElement>) => {
    const input = event.currentTarget
    const file = input.files?.[0]
    if (!file) return
    setImportError('')
    setPendingImport(null)
    try {
      setPendingImport(parseSituation(JSON.parse(await file.text())))
    } catch (error) {
      setImportError(error instanceof Error ? error.message : 'The file could not be imported.')
    }
    input.value = ''
  }

  if (!open) return null

  return (
    <div className="situation-backdrop" role="presentation">
      <div
        ref={dialogRef}
        className="situation-dialog"
        role="dialog"
        aria-modal="true"
        aria-labelledby="situation-heading"
        aria-describedby="situation-privacy-note"
      >
        <header className="situation-dialog-header">
          <div>
            <p className="eyebrow">Guest profile</p>
            <h2 id="situation-heading" ref={headingRef} tabIndex={-1}>
              Your situation
            </h2>
            <p id="situation-privacy-note">
              Add only what is useful now. Your answers stay in this browser unless you send them
              for an assessment.
            </p>
          </div>
          <button className="icon-button" aria-label="Close Your situation" onClick={onClose}>
            ×
          </button>
        </header>

        <nav className="situation-steps" aria-label="Situation setup progress">
          {STEPS.map((label, index) => (
            <button
              type="button"
              className={index === step ? 'is-current' : index < step ? 'is-complete' : ''}
              aria-current={index === step ? 'step' : undefined}
              onClick={() => setStep(index)}
              key={label}
            >
              <span>{index + 1}</span> {label}
            </button>
          ))}
        </nav>

        <div className="situation-dialog-body">
          <div className="scenario-toolbar" aria-label="Local scenarios">
            <label>
              <span>Active scenario</span>
              <select
                value={draft.active_scenario_id}
                onChange={(event) => {
                  const activeScenarioId = event.currentTarget.value
                  setDraft((current) => ({
                    ...current,
                    active_scenario_id: activeScenarioId,
                  }))
                }}
              >
                {draft.scenarios.map((item) => (
                  <option value={item.id} key={item.id}>
                    {item.name}
                  </option>
                ))}
              </select>
            </label>
            <button type="button" className="icon-text-button" onClick={addScenario} disabled={draft.scenarios.length >= MAX_SCENARIOS}>
              <span aria-hidden="true">＋</span> New
            </button>
            <button type="button" className="icon-text-button" onClick={duplicateScenario} disabled={draft.scenarios.length >= MAX_SCENARIOS}>
              <span aria-hidden="true">⧉</span> Duplicate
            </button>
            <button type="button" className="icon-text-button danger-text" onClick={removeScenario} disabled={draft.scenarios.length === 1}>
              <span aria-hidden="true">×</span> Remove
            </button>
          </div>

          {step === 0 && (
            <section className="situation-step" aria-labelledby="purpose-heading">
              <div className="step-heading">
                <p className="eyebrow">Scenario</p>
                <h3 id="purpose-heading">What are you exploring?</h3>
                <p>This sets the relevant check suggestions. Nothing is selected automatically.</p>
              </div>
              <label className="form-field compact-field">
                <span>Scenario name</span>
                <input
                  value={scenario.name}
                  maxLength={60}
                  onChange={(event) => updateScenario({ name: event.currentTarget.value })}
                />
              </label>
              <fieldset className="purpose-options">
                <legend>Exploration purpose</legend>
                {(['WORK', 'STUDY', 'FAMILY', 'EXPLORATION'] as const).map((purpose) => (
                  <label key={purpose}>
                    <input
                      type="radio"
                      name="purpose"
                      value={purpose}
                      checked={scenario.purpose === purpose}
                      onChange={() => updateScenario({ purpose })}
                    />
                    <span>{purposeLabel(purpose)}</span>
                  </label>
                ))}
              </fieldset>
              <div className="recommendation-note" role="note">
                <strong>{recommendations.length} relevant checks available</strong>
                <span>You will confirm exactly which checks run in the next step.</span>
              </div>
            </section>
          )}

          {step === 1 && (
            <section className="situation-step" aria-labelledby="checks-heading">
              <div className="step-heading">
                <p className="eyebrow">Explicit selection</p>
                <h3 id="checks-heading">Choose feasibility checks</h3>
                <p>Suggested checks appear first. Each check is separate from affinity and opportunity filters.</p>
              </div>
              <div className="tfc-selection-list">
                {[...catalog.definitions]
                  .sort((first, second) => {
                    const firstRecommended = first.applicable_purposes.includes(scenario.purpose)
                    const secondRecommended = second.applicable_purposes.includes(scenario.purpose)
                    return Number(secondRecommended) - Number(firstRecommended) || first.sort_order - second.sort_order
                  })
                  .map((definition) => {
                    const selected = scenario.selectedTfcIds.includes(definition.id)
                    const recommended = definition.applicable_purposes.includes(scenario.purpose)
                    return (
                      <label className={`tfc-selection-option${selected ? ' is-selected' : ''}`} key={definition.id}>
                        <input
                          type="checkbox"
                          checked={selected}
                          onChange={() =>
                            updateScenario({
                              selectedTfcIds: selected
                                ? scenario.selectedTfcIds.filter((id) => id !== definition.id)
                                : [...scenario.selectedTfcIds, definition.id],
                            })
                          }
                        />
                        <span>
                          <span className="option-heading">
                            <strong>{definition.display_name}</strong>
                            {recommended && <span className="recommendation-badge">Relevant to {purposeLabel(scenario.purpose)}</span>}
                          </span>
                          <small>{definition.user_question}</small>
                          <span className="tfc-meta-row">
                            {definition.input_requirements.filter((item) => item.requirement === 'ALWAYS_REQUIRED').length} required inputs · Assessment only · Effective {definition.effective_from}
                          </span>
                        </span>
                      </label>
                    )
                  })}
              </div>
              {!scenario.selectedTfcIds.length && (
                <div className="neutral-notice" role="status">
                  No checks selected. You can still rank and compare countries without profile context.
                </div>
              )}
            </section>
          )}

          {step === 2 && (
            <section className="situation-step" aria-labelledby="details-heading">
              <div className="step-heading">
                <p className="eyebrow">Relevant facts only</p>
                <h3 id="details-heading">Add details for the selected checks</h3>
                <p>Blank answers remain unknown. Required inputs can also be supplied later from a country result.</p>
              </div>
              {!scenario.selectedTfcIds.length ? (
                <div className="neutral-notice">Select a feasibility check to see its input fields.</div>
              ) : (
                <div className="situation-form-sections">
                  <fieldset>
                    <legend>Scenario assumptions</legend>
                    <label className="form-field">
                      <span>{fields.get('scenario.target_country_codes')?.prompt ?? 'Target destinations'} {requiredFieldIds.has('scenario.target_country_codes') && <em>Required</em>}</span>
                      <input
                        value={scenario.targetCountries}
                        placeholder="DEU, CAN"
                        onChange={(event) => updateScenario({ targetCountries: event.currentTarget.value })}
                      />
                      <FieldHelp field={fields.get('scenario.target_country_codes')} />
                    </label>
                    <label className="form-field">
                      <span>{fields.get('scenario.target_date')?.prompt ?? 'Target date'} {requiredFieldIds.has('scenario.target_date') && <em>Required</em>}</span>
                      <input type="date" value={scenario.targetDate} onChange={(event) => updateScenario({ targetDate: event.currentTarget.value })} />
                      <FieldHelp field={fields.get('scenario.target_date')} />
                    </label>
                  </fieldset>

                  {selectedDefinitions.some((definition) =>
                    definition.input_requirements.some(
                      (item) => item.field_id === 'applicant.occupation',
                    ),
                  ) && (
                    <fieldset>
                      <legend>Applicant</legend>
                      <label className="form-field">
                        <span>{fields.get('applicant.citizenships')?.prompt ?? 'Citizenship(s)'}</span>
                        <input value={draft.applicant.citizenships} placeholder="IND" onChange={(event) => {
                          const citizenships = event.currentTarget.value
                          setDraft((current) => ({ ...current, applicant: { ...current.applicant, citizenships } }))
                        }} />
                        <FieldHelp field={fields.get('applicant.citizenships')} />
                      </label>
                      <label className="form-field">
                        <span>{fields.get('applicant.occupation')?.prompt ?? 'Current occupation'} {requiredFieldIds.has('applicant.occupation') && <em>Required</em>}</span>
                        <input disabled={draft.applicant.occupationUnknown} value={draft.applicant.occupation} placeholder="Software engineer" onChange={(event) => {
                          const occupation = event.currentTarget.value
                          setDraft((current) => ({ ...current, applicant: { ...current.applicant, occupation } }))
                        }} />
                        <FieldHelp field={fields.get('applicant.occupation')} />
                      </label>
                      <label className="unknown-control">
                        <input type="checkbox" checked={draft.applicant.occupationUnknown} onChange={(event) => {
                          const occupationUnknown = event.currentTarget.checked
                          setDraft((current) => ({ ...current, applicant: { ...current.applicant, occupationUnknown } }))
                        }} />
                        I don’t know my occupation mapping
                      </label>
                      <label className="form-field">
                        <span>{fields.get('applicant.qualifications')?.prompt ?? 'Highest relevant qualification'} {requiredFieldIds.has('applicant.qualifications') && <em>Required</em>}</span>
                        <select value={draft.applicant.qualificationLevel} onChange={(event) => {
                          const qualificationLevel = event.currentTarget.value as SituationDocument['applicant']['qualificationLevel']
                          setDraft((current) => ({ ...current, applicant: { ...current.applicant, qualificationLevel } }))
                        }}>
                          <option value="UNKNOWN">I don’t know / prefer not to say</option>
                          <option value="SECONDARY">Secondary</option>
                          <option value="VOCATIONAL">Vocational</option>
                          <option value="BACHELORS">Bachelor’s</option>
                          <option value="MASTERS">Master’s</option>
                          <option value="DOCTORATE">Doctorate</option>
                          <option value="OTHER">Other</option>
                        </select>
                        <FieldHelp field={fields.get('applicant.qualifications')} />
                      </label>
                      <label className="form-field">
                        <span>{fields.get('scenario.job_offer')?.prompt ?? 'Job offer'} {requiredFieldIds.has('scenario.job_offer') && <em>Required</em>}</span>
                        <select value={scenario.jobOfferState} onChange={(event) => updateScenario({ jobOfferState: event.currentTarget.value as SituationScenario['jobOfferState'] })}>
                          <option value="UNKNOWN">I don’t know</option>
                          <option value="PRESENT">I have an offer</option>
                          <option value="ABSENT">I do not have an offer</option>
                        </select>
                        <FieldHelp field={fields.get('scenario.job_offer')} />
                      </label>
                    </fieldset>
                  )}

                  {requiredFieldIds.has('household.dependants') && (
                    <fieldset>
                      <legend>Household</legend>
                      <label className="form-field">
                        <span>{fields.get('household.partner_status')?.prompt ?? 'Partner status'} <em>Required</em></span>
                        <select value={draft.household.partnerStatus} onChange={(event) => {
                          const partnerStatus = event.currentTarget.value as SituationDocument['household']['partnerStatus']
                          setDraft((current) => ({ ...current, household: { ...current.household, partnerStatus } }))
                        }}>
                          <option value="UNKNOWN">I don’t know / prefer not to say</option>
                          <option value="NONE">No partner</option>
                          <option value="SPOUSE">Spouse</option>
                          <option value="CIVIL_PARTNER">Civil partner</option>
                          <option value="UNMARRIED_PARTNER">Unmarried partner</option>
                        </select>
                        <FieldHelp field={fields.get('household.partner_status')} />
                      </label>
                      <label className="unknown-control">
                        <input type="checkbox" checked={draft.household.dependantsKnown} onChange={(event) => {
                          const dependantsKnown = event.currentTarget.checked
                          setDraft((current) => ({ ...current, household: { ...current.household, dependantsKnown } }))
                        }} />
                        I know how many dependent children are relocating
                      </label>
                      {draft.household.dependantsKnown && (
                        <div className="inline-fields">
                          <label className="form-field">
                            <span>Dependent children</span>
                            <input type="number" min="0" max="19" value={draft.household.dependantCount} onChange={(event) => {
                              const dependantCount = Number(event.currentTarget.value)
                              setDraft((current) => ({ ...current, household: { ...current.household, dependantCount } }))
                            }} />
                          </label>
                          <label className="form-field">
                            <span>Age band</span>
                            <select value={draft.household.dependantAgeBand} onChange={(event) => {
                              const dependantAgeBand = event.currentTarget.value as SituationDocument['household']['dependantAgeBand']
                              setDraft((current) => ({ ...current, household: { ...current.household, dependantAgeBand } }))
                            }}>
                              <option value="UNKNOWN">Unknown</option>
                              <option value="UNDER_18">Under 18</option>
                              <option value="AGE_18_TO_20">18–20</option>
                              <option value="AGE_21_TO_22">21–22</option>
                              <option value="AGE_23_TO_25">23–25</option>
                              <option value="OVER_25">Over 25</option>
                            </select>
                          </label>
                        </div>
                      )}
                      <label className="form-field">
                        <span>{fields.get('scenario.primary_route_id')?.prompt ?? 'Primary route'} <em>Required</em></span>
                        <input value={scenario.primaryRouteId} placeholder="AU.SID.482" onChange={(event) => updateScenario({ primaryRouteId: event.currentTarget.value })} />
                        <FieldHelp field={fields.get('scenario.primary_route_id')} />
                      </label>
                      <label className="form-field">
                        <span>Who is relocating?</span>
                        <select value={scenario.relocationComposition} onChange={(event) => updateScenario({ relocationComposition: event.currentTarget.value as SituationScenario['relocationComposition'] })}>
                          <option value="UNKNOWN">I don’t know yet</option>
                          <option value="APPLICANT_ONLY">Applicant only</option>
                          <option value="WITH_PARTNER">With partner</option>
                          <option value="WITH_DEPENDANTS">With dependants</option>
                          <option value="WITH_PARTNER_AND_DEPENDANTS">With partner and dependants</option>
                        </select>
                      </label>
                    </fieldset>
                  )}

                  {requiredFieldIds.has('scenario.intended_study') && (
                    <fieldset>
                      <legend>Study scenario</legend>
                      <label className="form-field"><span>Institution <em>Required</em></span><input value={scenario.studyInstitution} onChange={(event) => updateScenario({ studyInstitution: event.currentTarget.value })} /></label>
                      <label className="form-field"><span>Field of study <em>Required</em></span><input value={scenario.studyField} onChange={(event) => updateScenario({ studyField: event.currentTarget.value })} /></label>
                      <div className="inline-fields">
                        <label className="form-field"><span>Qualification</span><select value={scenario.studyQualificationLevel} onChange={(event) => updateScenario({ studyQualificationLevel: event.currentTarget.value as SituationScenario['studyQualificationLevel'] })}><option value="UNKNOWN">Unknown</option><option value="VOCATIONAL">Vocational</option><option value="BACHELORS">Bachelor’s</option><option value="MASTERS">Master’s</option><option value="DOCTORATE">Doctorate</option><option value="OTHER">Other</option></select></label>
                        <label className="form-field"><span>Duration (months)</span><input type="number" min="1" max="120" value={scenario.studyDurationMonths} onChange={(event) => updateScenario({ studyDurationMonths: Number(event.currentTarget.value) })} /></label>
                      </div>
                      <div className="inline-fields">
                        <label className="form-field"><span>Study mode</span><select value={scenario.studyMode} onChange={(event) => updateScenario({ studyMode: event.currentTarget.value as SituationScenario['studyMode'] })}><option value="UNKNOWN">Unknown</option><option value="IN_PERSON">In person</option><option value="HYBRID">Hybrid</option><option value="ONLINE">Online</option></select></label>
                        <label className="form-field"><span>Completion date</span><input type="date" value={scenario.studyCompletionDate} onChange={(event) => updateScenario({ studyCompletionDate: event.currentTarget.value })} /></label>
                      </div>
                      <label className="form-field"><span>Completion state</span><select value={scenario.studyCompletionState} onChange={(event) => updateScenario({ studyCompletionState: event.currentTarget.value as SituationScenario['studyCompletionState'] })}><option value="PLANNED">Planned</option><option value="CURRENT">Current</option><option value="COMPLETED">Completed</option></select></label>
                      <FieldHelp field={fields.get('scenario.intended_study')} />
                    </fieldset>
                  )}
                </div>
              )}
            </section>
          )}

          {step === 3 && (
            <section className="situation-step" aria-labelledby="review-heading">
              <div className="step-heading">
                <p className="eyebrow">Assumptions and privacy</p>
                <h3 id="review-heading">Review before assessment</h3>
              </div>
              <dl className="situation-review">
                <div><dt>Active scenario</dt><dd>{situationSummary(draft)}</dd></div>
                <div><dt>Checks that will run</dt><dd>{selectedDefinitions.length ? selectedDefinitions.map((item) => item.display_name).join(', ') : 'None'}</dd></div>
                <div><dt>Unknown or incomplete</dt><dd>{[...requiredFieldIds].filter((id) => {
                  if (id === 'applicant.occupation') return !draft.applicant.occupation.trim() || draft.applicant.occupationUnknown
                  if (id === 'applicant.qualifications') return draft.applicant.qualificationLevel === 'UNKNOWN'
                  if (id === 'scenario.target_date') return !scenario.targetDate
                  if (id === 'scenario.target_country_codes') return !scenario.targetCountries.trim()
                  if (id === 'scenario.job_offer') return scenario.jobOfferState === 'UNKNOWN'
                  if (id === 'household.dependants') return !draft.household.dependantsKnown
                  if (id === 'scenario.primary_route_id') return !scenario.primaryRouteId.trim()
                  if (id === 'scenario.intended_study') return !scenario.studyInstitution.trim() || !scenario.studyField.trim() || !scenario.studyCompletionDate
                  return false
                }).map((id) => fields.get(id)?.prompt ?? id).join(', ') || 'None identified'}</dd></div>
              </dl>

              <div className="retention-panel">
                <div className="retention-heading"><span aria-hidden="true">▣</span><div><strong>Remember on this device</strong><p>Off by default. Stores this versioned situation in this browser for up to 30 days.</p></div></div>
                <label className="toggle-control"><input type="checkbox" checked={remember} onChange={(event) => setRemember(event.currentTarget.checked)} /><span>Remember my situation on this device</span></label>
                <p className="shared-device-warning">Avoid this on a shared device. Browser storage is not a secure account or cloud backup.</p>
              </div>

              <div className="data-actions" aria-label="Situation data actions">
                <button type="button" className="button button-secondary" onClick={download}><span aria-hidden="true">↓</span> Export JSON</button>
                <label className="button button-secondary import-button"><span aria-hidden="true">↑</span> Import JSON<input type="file" accept="application/json,.json" onChange={(event) => void readImport(event)} /></label>
                <button type="button" className="button button-secondary" onClick={onClearRemembered} disabled={!remembered}><span aria-hidden="true">×</span> Clear remembered data</button>
                {!confirmClear ? (
                  <button type="button" className="button button-danger" onClick={() => setConfirmClear(true)}>Clear current situation</button>
                ) : (
                  <button type="button" className="button button-danger" onClick={() => { const empty = createEmptySituation(); setDraft(empty); setConfirmClear(false); setRemember(false) }}>Confirm clear current situation</button>
                )}
              </div>
              <p className="export-privacy-note">
                Exports omit citizenship and household details. Assessment results are never included.
              </p>
              {importError && <div className="form-error" role="alert">{importError}</div>}
              {pendingImport && (
                <div className="import-preview" role="status">
                  <strong>Import preview</strong>
                  <p>{pendingImport.scenarios.length} scenario(s) · {situationSummary(pendingImport)}</p>
                  <button type="button" className="button button-secondary" onClick={() => { setDraft(cloneSituation(pendingImport)); setPendingImport(null) }}>Use imported situation</button>
                </div>
              )}
            </section>
          )}

          {errors.length > 0 && (
            <div className="form-error" role="alert" aria-live="assertive">
              <strong>Check these fields</strong>
              <ul>{errors.map((error) => <li key={error}>{error}</li>)}</ul>
            </div>
          )}
        </div>

        <footer className="situation-dialog-footer">
          <button type="button" className="button button-secondary" onClick={step === 0 ? onClose : () => setStep((current) => current - 1)}>
            {step === 0 ? 'Cancel' : 'Back'}
          </button>
          {step < STEPS.length - 1 ? (
            <button type="button" className="button button-primary" onClick={nextStep}>Continue</button>
          ) : (
            <button type="button" className="button button-primary" onClick={apply}>Save and assess</button>
          )}
        </footer>
      </div>
    </div>
  )
}
