import type { CSSProperties, KeyboardEvent } from 'react'

import type { CatalogCriterion } from '../api/types'
import { IMPORTANCE_STATES, importanceState } from '../preferences'

type ImportanceControlProps = {
  criterion: CatalogCriterion
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
  const isPartial = criterion.coverage_mode === 'CONDITIONAL_COMPLETE_CASE'
  const activationThreshold = criterion.pcc_activation_threshold
  const isActive =
    isPartial && activationThreshold !== null && value >= activationThreshold
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
          {criterion.valid_country_count}/{criterion.stable_country_count} countries
        </span>
        {isPartial && <span className="badge badge-limited">Limited coverage</span>}
        {criterion.experimental && <span className="badge badge-experimental">Experimental</span>}
      </div>
      {isPartial && (
        <p
          className={`pcc-activation-state${isActive ? ' is-active' : ''}`}
          aria-live="polite"
        >
          <span aria-hidden="true">{isActive ? '✓' : '○'}</span>{' '}
          {isActive
            ? 'Active in the ranking when applied.'
            : 'Not active in the ranking at this setting.'}
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
      {isPartial && (
        <details className="coverage-details">
          <summary>Coverage details</summary>
          <p>
            This criterion affects ranking only at Medium or above. Data is unavailable for{' '}
            {criterion.missing_country_count}{' '}
            {criterion.missing_country_count === 1 ? 'country' : 'countries'}.
          </p>
          {criterion.concise_caveat && <p>{criterion.concise_caveat}</p>}
        </details>
      )}
    </div>
  )
}
