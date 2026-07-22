import type { CatalogCriterion, Profile } from '../api/types'
import type { PreferenceDraft } from '../preferences'
import { ImportanceControl } from './ImportanceControl'

type PreferencesPanelProps = {
  criteria: CatalogCriterion[]
  profiles: Profile[]
  draft: PreferenceDraft
  dirty: boolean
  isApplying: boolean
  onProfileChange: (profile: Profile) => void
  onWeightChange: (criterionId: string, value: number) => void
  onApply: () => void
  onUndo: () => void
}

export function PreferencesPanel({
  criteria,
  profiles,
  draft,
  dirty,
  isApplying,
  onProfileChange,
  onWeightChange,
  onApply,
  onUndo,
}: PreferencesPanelProps) {
  const selectedProfile = profiles.find((profile) => profile.id === draft.profileId)

  return (
    <aside className="preferences-panel" aria-labelledby="priorities-heading">
      <div className="panel-heading">
        <p className="eyebrow">Your priorities</p>
        <h2 id="priorities-heading">What matters most?</h2>
        <p>Choose a starting profile, then adjust any priority before applying.</p>
      </div>

      <label className="field-label" htmlFor="profile-select">
        Preference profile
      </label>
      <select
        id="profile-select"
        value={draft.profileId ?? '__custom'}
        disabled={isApplying}
        onChange={(event) => {
          const profile = profiles.find((item) => item.id === event.currentTarget.value)
          if (profile) onProfileChange(profile)
        }}
      >
        {profiles.map((profile) => (
          <option value={profile.id} key={profile.id}>
            {profile.name}
          </option>
        ))}
        <option value="__custom" disabled>
          Custom
        </option>
      </select>
      <p className="profile-description" aria-live="polite">
        {selectedProfile?.description ?? 'Your priorities have been adjusted into a custom mix.'}
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
        <button className="button button-secondary" disabled={!dirty || isApplying} onClick={onUndo}>
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
        {dirty ? 'Changes are ready to apply.' : 'Your visible ranking matches these priorities.'}
      </p>
    </aside>
  )
}
