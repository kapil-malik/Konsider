import { useEffect, useRef, useState, type KeyboardEvent } from 'react'

import type { CatalogCriterionV2 } from '../api/types'
import { boundedCompactDisplayName, compactDisplayName } from '../displayName'
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
  const [open, setOpen] = useState(false)
  const controlRef = useRef<HTMLDivElement>(null)
  const state = importanceState(value)
  const isPartial = criterion.coverage.mode === 'CONDITIONAL_COMPLETE_CASE'
  const isLocality = criterion.scope.derivation === 'AGGREGATED_FROM_LOCALITIES'
  const name = compactDisplayName(criterion)
  const boundedName = boundedCompactDisplayName(criterion)
  const menuId = `importance-options-${criterion.id}`
  const coverageLabel = isPartial
    ? `Partial-coverage criterion: ${criterion.coverage.valid_country_count} of ${criterion.coverage.stable_country_count} countries covered`
    : 'Full-coverage criterion'

  useEffect(() => {
    if (!open) return
    const closeOnOutsideClick = (event: PointerEvent) => {
      if (!controlRef.current?.contains(event.target as Node)) setOpen(false)
    }
    document.addEventListener('pointerdown', closeOnOutsideClick)
    return () => document.removeEventListener('pointerdown', closeOnOutsideClick)
  }, [open])

  const handleKeyDown = (event: KeyboardEvent<HTMLButtonElement>) => {
    if (event.key === 'Escape') {
      event.preventDefault()
      setOpen(false)
    }
    if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
      event.preventDefault()
      setOpen(true)
    }
  }

  return (
    <div className="importance-control" data-criterion-id={criterion.id} ref={controlRef}>
      <div className="importance-summary-row">
        <div className="importance-heading">
          <span className="importance-name" title={criterion.displayName}>{boundedName}</span>
          <span
            className={`criterion-symbol coverage-symbol${isPartial ? ' is-partial' : ''}`}
            aria-label={coverageLabel}
            title={coverageLabel}
          >
            <span aria-hidden="true">{isPartial ? '◐' : '●'}</span>
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
          <button
            className="criterion-source-link"
            type="button"
            onClick={onOpenSources}
            aria-label={`Open criteria and sources for ${name}`}
            title="Open criteria and sources"
          >
            ↗
          </button>
        </div>
        <div className="importance-picker">
          <button
            className="importance-trigger"
            type="button"
            disabled={disabled}
            aria-label={`${name} importance: ${state.label}`}
            aria-haspopup="listbox"
            aria-expanded={open}
            aria-controls={menuId}
            onClick={() => setOpen((current) => !current)}
            onKeyDown={handleKeyDown}
          >
            <span>{state.shortLabel}</span>
            <span className="importance-chevron" aria-hidden="true">⌄</span>
          </button>
          {open && (
            <div className="importance-options" id={menuId} role="listbox" aria-label={`${name} importance choices`}>
              {IMPORTANCE_STATES.map((item) => (
                <button
                  type="button"
                  role="option"
                  aria-selected={item.value === state.value}
                  className={item.value === state.value ? 'is-selected' : undefined}
                  key={item.value}
                  onClick={() => {
                    onChange(item.value)
                    setOpen(false)
                  }}
                >
                  {item.label}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
