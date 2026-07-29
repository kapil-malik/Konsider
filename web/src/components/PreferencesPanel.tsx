import type { CatalogCriterionV2, PreferencePreset } from '../api/types'
import type { PreferenceDraft } from '../preferences'
import { ImportanceControl } from './ImportanceControl'

type PreferencesPanelProps = {
  criteria: CatalogCriterionV2[]
  presets: PreferencePreset[]
  draft: PreferenceDraft
  dirty: boolean
  isApplying: boolean
  onPresetChange: (preset: PreferencePreset) => void
  onWeightChange: (criterionId: string, value: number) => void
  onApply: () => void
  onUndo: () => void
}

export function PreferencesPanel({
  criteria,
  presets,
  draft,
  dirty,
  isApplying,
  onPresetChange,
  onWeightChange,
  onApply,
  onUndo,
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
            />
          ))}
        </div>
      ) : (
        <div className="inline-message inline-message-warning" role="status">
          No criteria are currently enabled, so rankings cannot be updated.
        </div>
      )}

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
          ? 'Changes are ready to apply.'
          : 'Your visible ranking matches these priorities.'}
      </p>
    </aside>
  )
}
