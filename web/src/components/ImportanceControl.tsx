import type { CSSProperties, KeyboardEvent } from 'react'

import type { CatalogCriterionV2 } from '../api/types'
import { IMPORTANCE_STATES, importanceState } from '../preferences'

type ImportanceControlProps = {
  criterion: CatalogCriterionV2
  value: number
  disabled?: boolean
  onChange: (value: number) => void
  onOpenSources: () => void
}

export function ImportanceControl({
  criterion,
  value,
  disabled = false,
  onChange,
  onOpenSources,
}: ImportanceControlProps) {
  const state = importanceState(value)
  const isPartial = criterion.coverage.mode === 'CONDITIONAL_COMPLETE_CASE'
  const isLocality = criterion.scope.derivation === 'AGGREGATED_FROM_LOCALITIES'
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
        <button
          className="criterion-source-link"
          type="button"
          onClick={onOpenSources}
          aria-label={`Open criteria and sources for ${criterion.display_name}`}
          title="Open criteria and sources"
        >
          ↗
        </button>
      </div>
      <div className="criterion-status-row">
        <span
          className={`criterion-symbol coverage-symbol${isPartial ? ' is-partial' : ''}`}
          aria-label={isPartial ? 'Partial-coverage criterion' : 'Full-coverage criterion'}
          title={isPartial ? 'Partial-coverage criterion' : 'Full-coverage criterion'}
        >
          <span aria-hidden="true">{isPartial ? '◐' : '●'}</span>
        </span>
        <span className="coverage-count" aria-label={`${criterion.coverage.valid_country_count} of ${criterion.coverage.stable_country_count} countries covered`}>
          {criterion.coverage.valid_country_count}/{criterion.coverage.stable_country_count}{' '}
        </span>
        {isLocality && (
          <span className="criterion-symbol locality-symbol" aria-label="Locality-derived criterion" title="Locality-derived criterion">
            <span aria-hidden="true">⌖</span>
          </span>
        )}
        {criterion.experimental && (
          <span className="criterion-symbol experimental-symbol" aria-label="Experimental criterion" title="Experimental criterion">
            <span aria-hidden="true">◇</span>
          </span>
        )}
      </div>
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
    </div>
  )
}
