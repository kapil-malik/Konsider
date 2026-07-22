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
      {criterion.experimental && <span className="badge badge-experimental">Experimental</span>}
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
