import { useMutation, useQuery } from '@tanstack/react-query'
import { useEffect, useMemo, useRef, useState } from 'react'

import {
  createComparison,
  createRanking,
  fetchCatalog,
  fetchOpportunityFilters,
} from './api/client'
import type {
  CatalogV2,
  ComparisonRequestV2,
  OpportunityFilterCatalogV2,
  PreferencePreset,
  RankingRequestV2,
  RankingV2,
  WeightSelectionV2,
} from './api/types'
import { ComparisonView } from './components/ComparisonView'
import { CountryDetails } from './components/CountryDetails'
import { ErrorNotice } from './components/ErrorNotice'
import { PreferencesPanel } from './components/PreferencesPanel'
import { RankingView } from './components/RankingView'
import { SourcesDialog } from './components/SourcesDialog'
import { countryCode } from './localityPresentation'
import {
  clonePreference,
  preferenceFromPreset,
  preferencesEqual,
  type PreferenceDraft,
} from './preferences'

const INTRODUCTION = 'Discover countries that better match your priorities.'

type HeaderProps = {
  onOpenSources: () => void
}

function Header({ onOpenSources }: HeaderProps) {
  const [menuOpen, setMenuOpen] = useState(false)
  const menuRef = useRef<HTMLDivElement>(null)
  const guestButtonRef = useRef<HTMLButtonElement>(null)

  useEffect(() => {
    const closeOutside = (event: MouseEvent) => {
      if (!menuRef.current?.contains(event.target as Node)) setMenuOpen(false)
    }
    document.addEventListener('mousedown', closeOutside)
    return () => document.removeEventListener('mousedown', closeOutside)
  }, [])

  return (
    <header className="site-header">
      <a className="brand" href="#main-content" aria-label="Konsider home">
        <span className="brand-mark" aria-hidden="true">
          K
        </span>
        <span>Konsider</span>
      </a>
      <div className="guest-menu" ref={menuRef}>
        <button
          ref={guestButtonRef}
          className="guest-menu-button"
          aria-haspopup="menu"
          aria-expanded={menuOpen}
          onClick={() => setMenuOpen((open) => !open)}
        >
          <span className="guest-avatar" aria-hidden="true">
            G
          </span>
          Guest
          <span aria-hidden="true">⌄</span>
        </button>
        {menuOpen && (
          <div className="guest-menu-popover" role="menu" aria-label="Guest session menu">
            <div className="guest-explanation">
              <strong>Guest session</strong>
              <p>Your priorities and selections are not saved.</p>
            </div>
            {['How Konsider works', 'Data & Sources'].map((label) => (
              <button
                role="menuitem"
                key={label}
                onClick={() => {
                  guestButtonRef.current?.focus()
                  setMenuOpen(false)
                  onOpenSources()
                }}
              >
                {label}
              </button>
            ))}
          </div>
        )}
      </div>
    </header>
  )
}

type ApplyVariables = {
  request: RankingRequestV2
  preference: PreferenceDraft
  opportunityFilterIds: string[]
  draftAfterSuccess?: {
    preference: PreferenceDraft
    opportunityFilterIds: string[]
  }
}

function selectionFor(
  preference: PreferenceDraft,
  opportunityFilterIds: string[] = [],
): WeightSelectionV2 {
  const preferenceSelection = preference.preferencePresetId
    ? { preference_preset_id: preference.preferencePresetId }
    : { weights: preference.weights }
  return opportunityFilterIds.length
    ? {
        ...preferenceSelection,
        opportunity_filters: {
          mode: 'ALL_REQUIRED',
          required_filter_ids: [...opportunityFilterIds].sort(),
        },
      }
    : preferenceSelection
}

const filterSelectionsEqual = (first: string[], second: string[]) =>
  first.length === second.length &&
  [...first].sort().every((value, index) => value === [...second].sort()[index])

function Workspace({
  catalog,
  opportunityCatalog,
  onOpenSources,
  onRankingChange,
}: {
  catalog: CatalogV2
  opportunityCatalog: OpportunityFilterCatalogV2
  onOpenSources: () => void
  onRankingChange: (ranking: RankingV2 | null) => void
}) {
  const enabledCriteria = useMemo(
    () =>
      catalog.criteria.filter(
        (criterion) => criterion.ready && criterion.default_enabled,
      ),
    [catalog.criteria],
  )
  const defaultPreset = catalog.preference_presets[0]

  if (!defaultPreset) {
    return (
      <main id="main-content" className="page-shell">
        <ErrorNotice
          error={new Error('No server preference presets')}
          title="No preference presets are available"
        />
      </main>
    )
  }

  return (
    <RankingWorkspace
      key={`${catalog.release_id}:${defaultPreset.id}`}
      catalog={catalog}
      opportunityCatalog={opportunityCatalog}
      defaultPreset={defaultPreset}
      enabledCriteria={enabledCriteria}
      onOpenSources={onOpenSources}
      onRankingChange={onRankingChange}
    />
  )
}

type RankingWorkspaceProps = {
  catalog: CatalogV2
  opportunityCatalog: OpportunityFilterCatalogV2
  defaultPreset: PreferencePreset
  enabledCriteria: CatalogV2['criteria']
  onOpenSources: () => void
  onRankingChange: (ranking: RankingV2 | null) => void
}

function RankingWorkspace({
  catalog,
  opportunityCatalog,
  defaultPreset,
  enabledCriteria,
  onOpenSources,
  onRankingChange,
}: RankingWorkspaceProps) {
  const initialPreference = preferenceFromPreset(defaultPreset)
  const [draft, setDraft] = useState<PreferenceDraft>(() =>
    clonePreference(initialPreference),
  )
  const [applied, setApplied] = useState<PreferenceDraft>(() =>
    clonePreference(initialPreference),
  )
  const [draftOpportunityFilterIds, setDraftOpportunityFilterIds] = useState<string[]>([])
  const [appliedOpportunityFilterIds, setAppliedOpportunityFilterIds] = useState<string[]>([])
  const [successfulRanking, setSuccessfulRanking] = useState<RankingV2 | null>(null)
  const [detailed, setDetailed] = useState(false)
  const [selectedCountry, setSelectedCountry] = useState<string | null>(null)
  const [comparisonCountries, setComparisonCountries] = useState<string[]>([])
  const [comparisonNotice, setComparisonNotice] = useState('')
  const [mode, setMode] = useState<'ranking' | 'comparison'>('ranking')
  const rankingScrollRef = useRef<HTMLDivElement>(null)
  const compareButtonRef = useRef<HTMLButtonElement>(null)
  const rankingScrollTop = useRef(0)

  const initialRanking = useQuery({
    queryKey: ['ranking', 'initial', catalog.release_id, defaultPreset.id],
    queryFn: ({ signal }) =>
      createRanking({ preference_preset_id: defaultPreset.id }, signal),
  })
  const applyMutation = useMutation({
    mutationFn: ({ request }: ApplyVariables) => createRanking(request),
    onSuccess: (ranking, variables) => {
      setSuccessfulRanking(ranking)
      setApplied(clonePreference(variables.preference))
      setAppliedOpportunityFilterIds([...variables.opportunityFilterIds])
      setDraft(
        clonePreference(
          variables.draftAfterSuccess?.preference ?? variables.preference,
        ),
      )
      setDraftOpportunityFilterIds([
        ...(variables.draftAfterSuccess?.opportunityFilterIds ??
          variables.opportunityFilterIds),
      ])
      setComparisonCountries([])
      setComparisonNotice('')
      setSelectedCountry(null)
      setMode('ranking')
      comparisonMutation.reset()
    },
  })
  const comparisonMutation = useMutation({
    mutationFn: (request: ComparisonRequestV2) => createComparison(request),
    onSuccess: () => {
      rankingScrollTop.current = rankingScrollRef.current?.scrollTop ?? 0
      setMode('comparison')
    },
  })

  const ranking = successfulRanking ?? initialRanking.data
  useEffect(() => onRankingChange(ranking ?? null), [onRankingChange, ranking])
  const dirty =
    !preferencesEqual(draft, applied) ||
    !filterSelectionsEqual(
      draftOpportunityFilterIds,
      appliedOpportunityFilterIds,
    )

  const selectPreset = (preset: PreferencePreset) => {
    setDraft(preferenceFromPreset(preset))
  }

  const changeWeight = (criterionId: string, value: number) => {
    setDraft((current) => ({
      preferencePresetId: null,
      weights: { ...current.weights, [criterionId]: value },
    }))
  }

  const toggleOpportunityFilter = (filterId: string) => {
    setDraftOpportunityFilterIds((current) =>
      current.includes(filterId)
        ? current.filter((id) => id !== filterId)
        : [...current, filterId],
    )
  }

  const applyPriorities = () => {
    if (!dirty || applyMutation.isPending) return
    const preference = clonePreference(draft)
    const opportunityFilterIds = [...draftOpportunityFilterIds].sort()
    applyMutation.mutate({
      request: selectionFor(preference, opportunityFilterIds),
      preference,
      opportunityFilterIds,
    })
  }

  const removeAppliedOpportunityFilter = (filterId: string) => {
    if (applyMutation.isPending) return
    const nextApplied = appliedOpportunityFilterIds.filter((id) => id !== filterId)
    applyMutation.mutate({
      request: selectionFor(applied, nextApplied),
      preference: clonePreference(applied),
      opportunityFilterIds: nextApplied,
      draftAfterSuccess: {
        preference: clonePreference(draft),
        opportunityFilterIds: draftOpportunityFilterIds.filter(
          (id) => id !== filterId,
        ),
      },
    })
  }

  const clearAppliedOpportunityFilters = () => {
    if (applyMutation.isPending || !appliedOpportunityFilterIds.length) return
    applyMutation.mutate({
      request: selectionFor(applied),
      preference: clonePreference(applied),
      opportunityFilterIds: [],
      draftAfterSuccess: {
        preference: clonePreference(draft),
        opportunityFilterIds: [],
      },
    })
  }

  const toggleComparison = (code: string) => {
    setComparisonCountries((current) => {
      if (current.includes(code)) {
        setComparisonNotice('')
        return current.filter((item) => item !== code)
      }
      if (current.length >= 4) {
        setComparisonNotice(
          'You can compare up to four countries. Deselect one to add another.',
        )
        return current
      }
      setComparisonNotice(
        current.length === 3 ? 'Four countries selected—the comparison is full.' : '',
      )
      return [...current, code]
    })
  }

  const compareSelected = () => {
    if (comparisonCountries.length < 2 || comparisonMutation.isPending) return
    comparisonMutation.mutate({
      country_codes: comparisonCountries,
      ...selectionFor(applied, appliedOpportunityFilterIds),
    })
  }

  const backToRankings = () => {
    setMode('ranking')
    window.requestAnimationFrame(() => {
      if (rankingScrollRef.current)
        rankingScrollRef.current.scrollTop = rankingScrollTop.current
      compareButtonRef.current?.focus()
    })
  }

  const selectFromComparison = (code: string) => {
    setSelectedCountry(code)
    setMode('ranking')
  }

  const rankingCountry = ranking?.rankings.find(
    (item) => countryCode(item.country.entity_id) === selectedCountry,
  )
  const selectedCatalogCountry = catalog.countries.find(
    (item) => countryCode(item.entity_id) === selectedCountry,
  )
  const excludedCountry = ranking?.assessments.coverage.excluded_countries.find(
    (item) => countryCode(item.country.entity_id) === selectedCountry,
  )

  return (
    <main id="main-content" className="page-shell">
      <section className="intro-section" aria-labelledby="intro-heading">
        <p className="eyebrow">A clearer way to explore relocation choices</p>
        <h1 id="intro-heading">{INTRODUCTION}</h1>
        <p>
          Shape the ranking with your priorities, inspect national, locality, and opportunity
          evidence, and
          compare the countries that stand out.
        </p>
      </section>

      <div className="workspace-grid">
        <PreferencesPanel
          criteria={enabledCriteria}
          presets={catalog.preference_presets}
          draft={draft}
          dirty={dirty}
          isApplying={applyMutation.isPending}
          opportunityCatalog={opportunityCatalog}
          selectedOpportunityFilterIds={draftOpportunityFilterIds}
          onPresetChange={selectPreset}
          onWeightChange={changeWeight}
          onOpportunityFilterToggle={toggleOpportunityFilter}
          onOpportunityFiltersClear={() => setDraftOpportunityFilterIds([])}
          onApply={applyPriorities}
          onUndo={() => {
            setDraft(clonePreference(applied))
            setDraftOpportunityFilterIds([...appliedOpportunityFilterIds])
          }}
        />

        <div className="ranking-workspace">
          {applyMutation.error && <ErrorNotice error={applyMutation.error} />}
          {comparisonMutation.error && <ErrorNotice error={comparisonMutation.error} />}
          {initialRanking.isPending && !ranking && (
            <section className="results-panel loading-panel" aria-busy="true" aria-live="polite">
              <p className="eyebrow">Current match</p>
              <h2>Building the initial ranking…</h2>
              <div className="loading-lines" aria-hidden="true">
                <span />
                <span />
                <span />
              </div>
            </section>
          )}
          {initialRanking.error && !ranking && (
            <ErrorNotice
              error={initialRanking.error}
              onRetry={() => void initialRanking.refetch()}
            />
          )}
          {ranking && mode === 'ranking' && (
            <RankingView
              ranking={ranking}
              criteria={enabledCriteria}
              countries={catalog.countries}
              opportunityCatalog={opportunityCatalog}
              detailed={detailed}
              isUpdating={applyMutation.isPending}
              isComparing={comparisonMutation.isPending}
              selectedCountry={selectedCountry}
              comparisonCountries={comparisonCountries}
              comparisonNotice={comparisonNotice}
              scrollRef={rankingScrollRef}
              compareButtonRef={compareButtonRef}
              onDetailedChange={setDetailed}
              onSelectCountry={setSelectedCountry}
              onToggleComparison={toggleComparison}
              onCompare={compareSelected}
              onOpenSources={onOpenSources}
              onRemoveOpportunityFilter={removeAppliedOpportunityFilter}
              onClearOpportunityFilters={clearAppliedOpportunityFilters}
            />
          )}
          {mode === 'comparison' && comparisonMutation.data && (
            <ComparisonView
              comparison={comparisonMutation.data}
              opportunityCatalog={opportunityCatalog}
              onBack={backToRankings}
              onSelectCountry={selectFromComparison}
            />
          )}
        </div>
      </div>

      {ranking && mode === 'ranking' && selectedCountry && (
        <CountryDetails
          countryCode={selectedCountry}
          selection={selectionFor(applied, appliedOpportunityFilterIds)}
          opportunityCatalog={opportunityCatalog}
          rankingCountry={rankingCountry}
          countryName={
            rankingCountry?.country.display_name ??
            excludedCountry?.country.display_name ??
            selectedCatalogCountry?.display_name ??
            selectedCountry
          }
          coverageExcluded={Boolean(excludedCountry)}
          opportunityExcluded={Boolean(
            ranking.assessments.opportunity.excluded_countries.some(
              (item) => item.country_code === selectedCountry,
            ),
          )}
          opportunityBaseRank={
            ranking.assessments.opportunity.excluded_countries.find(
              (item) => item.country_code === selectedCountry,
            )?.base_rank ?? null
          }
          onClose={() => setSelectedCountry(null)}
        />
      )}
    </main>
  )
}

export default function App() {
  const [sourcesOpen, setSourcesOpen] = useState(false)
  const [currentRanking, setCurrentRanking] = useState<RankingV2 | null>(null)
  const sourcesReturnFocus = useRef<HTMLElement | null>(null)
  const catalogQuery = useQuery({
    queryKey: ['catalog'],
    queryFn: ({ signal }) => fetchCatalog(signal),
  })
  const opportunityCatalogQuery = useQuery({
    queryKey: ['opportunity-filters'],
    queryFn: ({ signal }) => fetchOpportunityFilters(signal),
  })
  const catalogError = catalogQuery.error ?? opportunityCatalogQuery.error
  const openSources = () => {
    sourcesReturnFocus.current =
      document.activeElement instanceof HTMLElement ? document.activeElement : null
    setSourcesOpen(true)
  }
  const closeSources = () => {
    setSourcesOpen(false)
    window.requestAnimationFrame(() => sourcesReturnFocus.current?.focus())
  }

  return (
    <div className="app-frame">
      <a className="skip-link" href="#main-content">
        Skip to main content
      </a>
      <Header onOpenSources={openSources} />
      {(catalogQuery.isPending || opportunityCatalogQuery.isPending) && (
        <main id="main-content" className="page-shell initial-loading" aria-live="polite">
          <div className="brand-mark brand-mark-large" aria-hidden="true">
            K
          </div>
          <h1>Loading Konsider…</h1>
          <p>Connecting to the current country and opportunity-filter catalogs.</p>
        </main>
      )}
      {catalogError && (
        <main id="main-content" className="page-shell initial-error">
          <ErrorNotice
            error={catalogError}
            onRetry={() => {
              void catalogQuery.refetch()
              void opportunityCatalogQuery.refetch()
            }}
          />
        </main>
      )}
      {catalogQuery.data && opportunityCatalogQuery.data && (
        <Workspace
          catalog={catalogQuery.data}
          opportunityCatalog={opportunityCatalogQuery.data}
          onOpenSources={openSources}
          onRankingChange={setCurrentRanking}
        />
      )}
      {sourcesOpen && catalogQuery.data && (
        <SourcesDialog
          catalog={catalogQuery.data}
          ranking={currentRanking}
          onClose={closeSources}
        />
      )}
    </div>
  )
}
