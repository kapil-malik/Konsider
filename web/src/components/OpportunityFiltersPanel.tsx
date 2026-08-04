import type { OpportunityFilterCatalogV2 } from '../api/types'
import { EDUCATION_SHARED_LIMITATION } from '../opportunityPresentation'

type OpportunityFiltersPanelProps = {
  catalog: OpportunityFilterCatalogV2
  selectedFilterIds: string[]
  disabled: boolean
  onToggle: (filterId: string) => void
  onClear: () => void
}

export function OpportunityFiltersPanel({
  catalog,
  selectedFilterIds,
  disabled,
  onToggle,
  onClear,
}: OpportunityFiltersPanelProps) {
  const definitions = catalog.definitions.filter(
    (definition) => definition.active && definition.availability === 'AVAILABLE',
  )
  const groups = [
    { category: 'CAREER' as const, label: 'Career' },
    {
      category: 'EDUCATION' as const,
      label: 'Education and research universities',
    },
  ]

  return (
    <section
      className="opportunity-filter-panel"
      aria-labelledby="opportunity-filters-heading"
    >
      <div className="opportunity-filter-heading">
        <div>
          <p className="eyebrow">Optional destination evidence</p>
          <h2 id="opportunity-filters-heading">Opportunity filters</h2>
        </div>
        <span className="filter-count" aria-live="polite">
          {selectedFilterIds.length} selected
        </span>
      </div>
      <p>
        Opportunity filters do not change affinity scores. They keep only countries where
        Konsider has verified a strong signal for every selected opportunity.
      </p>
      <p className="all-required-note">
        <strong>All selected opportunity filters must have a verified strong signal.</strong>
      </p>

      <details className="opportunity-help">
        <summary>How opportunity filters work</summary>
        <div>
          <p>
            Only a verified strong signal passes. Insufficient evidence is not negative and does
            not mean an opportunity is absent. Filters never change weights, affinity scores, or
            the order of countries that pass.
          </p>
          <p>{EDUCATION_SHARED_LIMITATION}</p>
          <p>
            Evidence freshness is shown in country details. Read the{' '}
            <a
              href="https://github.com/kapil-malik/Konsider/blob/main/docs/product/opportunity-filter-engine.md"
              target="_blank"
              rel="noreferrer"
            >
              Opportunity Filter methodology (opens in a new tab)
            </a>
            .
          </p>
        </div>
      </details>

      {!definitions.length ? (
        <div className="inline-message inline-message-warning" role="status">
          Opportunity filters are not available in this configured API release.
        </div>
      ) : (
        <div className="opportunity-groups">
          {groups.map((group) => {
            const members = definitions.filter(
              (definition) => definition.category === group.category,
            )
            return (
              <details className="opportunity-group" open key={group.category}>
                <summary>
                  {group.label} <span>{members.length}</span>
                </summary>
                <div className="opportunity-options">
                  {members.map((definition) => {
                    const checked = selectedFilterIds.includes(definition.id)
                    return (
                      <label
                        className={`opportunity-option${checked ? ' opportunity-option-selected' : ''}`}
                        title={definition.display_name}
                        key={definition.id}
                      >
                        <input
                          type="checkbox"
                          checked={checked}
                          disabled={disabled}
                          aria-label={definition.display_name}
                          aria-describedby={`${definition.id}-meaning`}
                          onChange={() => onToggle(definition.id)}
                        />
                        <span>
                          <strong>
                            {definition.compact_label ?? definition.display_name}
                          </strong>
                          <small id={`${definition.id}-meaning`}>
                            {definition.meaning}
                          </small>
                        </span>
                      </label>
                    )
                  })}
                </div>
              </details>
            )
          })}
        </div>
      )}

      <button
        type="button"
        className="text-button clear-opportunity-filters"
        disabled={disabled || !selectedFilterIds.length}
        onClick={onClear}
      >
        Clear all opportunity filters
      </button>
    </section>
  )
}
