import type { CSSProperties, KeyboardEvent } from 'react'

import type { CatalogCriterionV2 } from '../api/types'
import { IMPORTANCE_STATES, importanceState } from '../preferences'

type ImportanceControlProps = {
  criterion: CatalogCriterionV2
  value: number
  disabled?: boolean
  onChange: (value: number) => void
}

export function ImportanceControl({
  criterion,
  value,
  disabled = false,
  onChange,
}: ImportanceControlProps) {
  const state = importanceState(value)
  const isPartial = criterion.coverage.mode === 'CONDITIONAL_COMPLETE_CASE'
  const isLocality = criterion.scope.derivation === 'AGGREGATED_FROM_LOCALITIES'
  const coverageThreshold = criterion.coverage.activation_threshold ?? null
  const localityThreshold =
    criterion.scope.locality_analysis_threshold ?? null
  const coverageActive =
    isPartial &&
    coverageThreshold !== null &&
    value >= coverageThreshold
  const localityAnalysisActive =
    isLocality &&
    localityThreshold !== null &&
    value >= localityThreshold
  const fillStyle = { '--importance-fill': `${value * 100}%` } as CSSProperties
  const handleKeyDown = (event: KeyboardEvent<HTMLInputElement>) => {
    const currentIndex = IMPORTANCE_STATES.findIndex((item) => item.value === state.value)
    let nextIndex = currentIndex
    if (event.key === 'ArrowRight' || event.key === 'ArrowUp') nextIndex += 1
    if (event.key === 'ArrowLeft' || event.key === 'ArrowDown') nextIndex -= 1
    if (event.key === 'Home') nextIndex = 0
    if (event.key === 'End') nextIndex = IMPORTANCE_STATES.length - 1
    nextIndex = Math.max(0, Math.min(IMPORTANCE_STATES.length - 1, nextIndex))
    if (nextIndex !== currentIndex) {
      event.preventDefault()
      onChange(IMPORTANCE_STATES[nextIndex].value)
    }
  }

  return (
    <div className="importance-control" data-criterion-id={criterion.id}>
      <div className="importance-heading">
        <label htmlFor={`importance-${criterion.id}`}>{criterion.display_name}</label>
        <span className="importance-value" aria-hidden="true">
          {state.label}
        </span>
      </div>
      <div className="criterion-status-row">
        <span className="coverage-count">
          {criterion.coverage.valid_country_count}/{criterion.coverage.stable_country_count}{' '}
          countries
        </span>
        <span className="badge badge-scope">
          {isLocality ? '⌖ Locality-derived' : '● National'}
        </span>
        {isPartial && <span className="badge badge-limited">! Limited coverage</span>}
        {criterion.experimental && (
          <span className="badge badge-experimental">◇ Experimental</span>
        )}
      </div>
      {isPartial && (
        <p
          className={`pcc-activation-state${coverageActive ? ' is-active' : ''}`}
          aria-live="polite"
        >
          <span aria-hidden="true">{coverageActive ? '✓' : '○'}</span>{' '}
          {coverageActive
              ? 'Limited-coverage ranking rules will apply.'
              : `Coverage activation begins at ${importanceState(
                coverageThreshold ?? 0,
              ).label}.`}
        </p>
      )}
      {isLocality && (
        <p
          className={`locality-activation-state${localityAnalysisActive ? ' is-active' : ''}`}
          aria-live="polite"
        >
          <span aria-hidden="true">{localityAnalysisActive ? '⌖' : '○'}</span>{' '}
          {localityAnalysisActive
              ? 'Locality compatibility will be assessed when applied.'
              : `Locality provenance remains available; prominent analysis begins at ${importanceState(
                localityThreshold ?? 0,
              ).label}.`}
        </p>
      )}
      <input
        className="importance-slider"
        id={`importance-${criterion.id}`}
        type="range"
        min="0"
        max="1"
        step="0.2"
        value={value}
        disabled={disabled}
        aria-valuetext={`${state.label}, ${state.value.toFixed(1)}`}
        onChange={(event) => onChange(Number(event.currentTarget.value))}
        onKeyDown={handleKeyDown}
        style={fillStyle}
      />
      <div className="importance-ticks" aria-hidden="true">
        {IMPORTANCE_STATES.map((item) => (
          <span key={item.value}>{item.shortLabel}</span>
        ))}
      </div>
      {(isPartial || isLocality) && (
        <details className="coverage-details">
          <summary>Coverage and scope details</summary>
          <p>
            Coverage: {criterion.coverage.mode.replaceAll('_', ' ').toLocaleLowerCase()} · Scope:{' '}
            {criterion.scope.evidence_level.toLocaleLowerCase()} evidence to country result.
          </p>
          {isLocality && (
            <p>
              Universe <code>{criterion.scope.locality_universe_id}</code> · Policy{' '}
              <code>{criterion.scope.aggregation_policy_id}</code>
            </p>
          )}
          {criterion.caveats[0] && <p>{criterion.caveats[0]}</p>}
        </details>
      )}
    </div>
  )
}
