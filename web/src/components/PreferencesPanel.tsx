import type {
  CatalogCriterionV2,
  OpportunityFilterCatalogV2,
  PreferencePreset,
} from '../api/types'
import type { PreferenceDraft } from '../preferences'
import { ImportanceControl } from './ImportanceControl'
import { OpportunityFiltersPanel } from './OpportunityFiltersPanel'

type PreferencesPanelProps = {
  criteria: CatalogCriterionV2[]
  presets: PreferencePreset[]
  draft: PreferenceDraft
  dirty: boolean
  isApplying: boolean
  opportunityCatalog: OpportunityFilterCatalogV2
  selectedOpportunityFilterIds: string[]
  onPresetChange: (preset: PreferencePreset) => void
  onWeightChange: (criterionId: string, value: number) => void
  onOpportunityFilterToggle: (filterId: string) => void
  onOpportunityFiltersClear: () => void
  onApply: () => void
  onUndo: () => void
  onOpenSources: () => void
}

export function PreferencesPanel({
  criteria,
  presets,
  draft,
  dirty,
  isApplying,
  opportunityCatalog,
  selectedOpportunityFilterIds,
  onPresetChange,
  onWeightChange,
  onOpportunityFilterToggle,
  onOpportunityFiltersClear,
  onApply,
  onUndo,
  onOpenSources,
}: PreferencesPanelProps) {
  const selectedPreset = presets.find(
    (preset) => preset.id === draft.preferencePresetId,
  )

  return (
    <aside className="preferences-panel" aria-labelledby="priorities-heading">
      <div className="panel-heading">
        <p className="eyebrow">Your priorities</p>
        <h2 id="priorities-heading">What matters most?</h2>
        <p>Choose a preference preset, then adjust any priority before applying.</p>
      </div>

      <label className="field-label" htmlFor="preset-select">
        Preference preset
      </label>
      <select
        id="preset-select"
        value={draft.preferencePresetId ?? '__custom'}
        disabled={isApplying}
        onChange={(event) => {
          const preset = presets.find(
            (item) => item.id === event.currentTarget.value,
          )
          if (preset) onPresetChange(preset)
        }}
      >
        {presets.map((preset) => (
          <option value={preset.id} key={preset.id}>
            {preset.name}
          </option>
        ))}
        <option value="__custom" disabled>
          Custom
        </option>
      </select>
      <p className="profile-description" aria-live="polite">
        {selectedPreset?.description ??
          'Your priorities have been adjusted into a custom mix.'}
      </p>

      {criteria.length ? (
        <div className="importance-list">
          {criteria.map((criterion) => (
            <ImportanceControl
              key={criterion.id}
              criterion={criterion}
              value={draft.weights[criterion.id] ?? 0}
              disabled={isApplying}
              onChange={(value) => onWeightChange(criterion.id, value)}
              onOpenSources={onOpenSources}
            />
          ))}
        </div>
      ) : (
        <div className="inline-message inline-message-warning" role="status">
          No criteria are currently enabled, so rankings cannot be updated.
        </div>
      )}

      <div className="criterion-legend" aria-label="Criterion symbol legend">
        <span><b aria-hidden="true">●</b> Full coverage</span>
        <span><b aria-hidden="true">◐</b> Partial coverage</span>
        <span><b aria-hidden="true">⌖</b> Locality-derived</span>
        <span><b aria-hidden="true">◇</b> Experimental</span>
        <button type="button" className="text-button" onClick={onOpenSources}>Criteria and sources</button>
      </div>

      <OpportunityFiltersPanel
        catalog={opportunityCatalog}
        selectedFilterIds={selectedOpportunityFilterIds}
        disabled={isApplying}
        onToggle={onOpportunityFilterToggle}
        onClear={onOpportunityFiltersClear}
        onOpenSources={onOpenSources}
      />

      <div className="apply-bar">
        <button
          className="button button-secondary"
          disabled={!dirty || isApplying}
          onClick={onUndo}
        >
          Undo changes
        </button>
        <button
          className="button button-primary"
          disabled={!dirty || isApplying || !criteria.length}
          onClick={onApply}
        >
          {isApplying ? 'Applying…' : 'Apply priorities'}
        </button>
      </div>
      <p className="apply-hint" aria-live="polite">
        {dirty
          ? 'Priority or opportunity-filter changes are ready to apply.'
          : 'Your visible ranking matches these priorities and opportunity filters.'}
      </p>
    </aside>
  )
}
