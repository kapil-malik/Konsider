import type { OpportunityFilterCatalogV2 } from '../api/types'

type OpportunityFiltersPanelProps = {
  catalog: OpportunityFilterCatalogV2
  selectedFilterIds: string[]
  disabled: boolean
  onToggle: (filterId: string) => void
  onClear: () => void
  onOpenSources: () => void
}

export function OpportunityFiltersPanel({
  catalog,
  selectedFilterIds,
  disabled,
  onToggle,
  onClear,
  onOpenSources,
}: OpportunityFiltersPanelProps) {
  const definitions = catalog.definitions.filter(
    (definition) => definition.active && definition.availability === 'AVAILABLE',
  )
  const groups = [...catalog.sections].sort((first, second) => first.sortOrder - second.sortOrder)

  return (
    <section
      className="opportunity-filter-panel"
      aria-labelledby="opportunity-filters-heading"
    >
      <div className="opportunity-filter-heading">
        <div>
          <p className="eyebrow">Optional destination evidence</p>
          <div className="opportunity-filter-title">
            <h2 id="opportunity-filters-heading">Opportunity filters</h2>
            <button
              className="criterion-source-link"
              type="button"
              onClick={onOpenSources}
              aria-label="Open criteria and sources for opportunity filters"
              title="Open criteria and sources"
            >
              ↗
            </button>
          </div>
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

      {!definitions.length ? (
        <div className="inline-message inline-message-warning" role="status">
          Opportunity filters are not available in this configured API release.
        </div>
      ) : (
        <div className="opportunity-groups">
          {groups.map((group) => {
            const members = definitions.filter(
              (definition) => definition.sectionId === group.sectionId,
            ).sort((first, second) => first.sortOrder - second.sortOrder)
            const selectedCount = members.filter((definition) =>
              selectedFilterIds.includes(definition.id),
            ).length
            return (
              <details className="opportunity-group" key={group.sectionId}>
                <summary>
                  {group.sectionName}{' '}
                  <span
                    aria-label={`${selectedCount} of ${members.length} filters selected`}
                  >
                    {selectedCount}/{members.length} selected
                  </span>
                </summary>
                <div className="opportunity-options">
                  {members.map((definition) => {
                    const checked = selectedFilterIds.includes(definition.id)
                    return (
                      <label
                        className={`opportunity-option${checked ? ' opportunity-option-selected' : ''}`}
                        title={definition.displayName}
                        key={definition.id}
                      >
                        <input
                          type="checkbox"
                          checked={checked}
                          disabled={disabled}
                          aria-label={definition.displayName}
                          aria-describedby={`${definition.id}-meaning`}
                          onChange={() => onToggle(definition.id)}
                        />
                        <span>
                          <strong>
                            {definition.compactName ?? definition.displayName}
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
