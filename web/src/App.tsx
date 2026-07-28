import { useMutation, useQuery } from '@tanstack/react-query'
import { useEffect, useMemo, useRef, useState } from 'react'

import { createComparison, createRanking, fetchCatalog } from './api/client'
import type {
  Catalog,
  ComparisonRequest,
  Profile,
  Ranking,
  RankingRequest,
} from './api/types'
import { ComparisonView } from './components/ComparisonView'
import { CountryDetails } from './components/CountryDetails'
import { ErrorNotice } from './components/ErrorNotice'
import { PreferencesPanel } from './components/PreferencesPanel'
import { RankingView } from './components/RankingView'
import { SourcesDialog } from './components/SourcesDialog'
import {
  clonePreference,
  preferenceFromProfile,
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
            <button
              role="menuitem"
              onClick={() => {
                guestButtonRef.current?.focus()
                setMenuOpen(false)
                onOpenSources()
              }}
            >
              How Konsider works
            </button>
            <button
              role="menuitem"
              onClick={() => {
                guestButtonRef.current?.focus()
                setMenuOpen(false)
                onOpenSources()
              }}
            >
              Data &amp; Sources
            </button>
          </div>
        )}
      </div>
    </header>
  )
}

type ApplyVariables = {
  request: RankingRequest
  preference: PreferenceDraft
}

function Workspace({ catalog, onOpenSources }: { catalog: Catalog; onOpenSources: () => void }) {
  const enabledCriteria = useMemo(
    () => catalog.criteria.filter((criterion) => criterion.ready && criterion.default_enabled),
    [catalog.criteria],
  )
  const defaultProfile = catalog.profiles[0]

  if (!defaultProfile) {
    return (
      <main id="main-content" className="page-shell">
        <ErrorNotice error={new Error('No server profiles')} title="No preference profiles are available" />
      </main>
    )
  }

  return (
    <RankingWorkspace
      key={`${catalog.release_id}:${defaultProfile.id}`}
      catalog={catalog}
      defaultProfile={defaultProfile}
      enabledCriteria={enabledCriteria}
      onOpenSources={onOpenSources}
    />
  )
}

type RankingWorkspaceProps = {
  catalog: Catalog
  defaultProfile: Profile
  enabledCriteria: Catalog['criteria']
  onOpenSources: () => void
}

function RankingWorkspace({
  catalog,
  defaultProfile,
  enabledCriteria,
  onOpenSources,
}: RankingWorkspaceProps) {
  const initialPreference = preferenceFromProfile(defaultProfile)
  const [draft, setDraft] = useState<PreferenceDraft>(() => clonePreference(initialPreference))
  const [applied, setApplied] = useState<PreferenceDraft>(() => clonePreference(initialPreference))
  const [successfulRanking, setSuccessfulRanking] = useState<Ranking | null>(null)
  const [detailed, setDetailed] = useState(false)
  const [selectedCountry, setSelectedCountry] = useState<string | null>(null)
  const [comparisonCountries, setComparisonCountries] = useState<string[]>([])
  const [comparisonNotice, setComparisonNotice] = useState('')
  const [mode, setMode] = useState<'ranking' | 'comparison'>('ranking')
  const [showingBaseline, setShowingBaseline] = useState(false)
  const rankingScrollRef = useRef<HTMLDivElement>(null)
  const compareButtonRef = useRef<HTMLButtonElement>(null)
  const rankingScrollTop = useRef(0)

  const initialRanking = useQuery({
    queryKey: ['ranking', 'initial', catalog.release_id, defaultProfile.id],
    queryFn: ({ signal }) => createRanking({ profile_id: defaultProfile.id }, signal),
  })
  const applyMutation = useMutation({
    mutationFn: ({ request }: ApplyVariables) => createRanking(request),
    onSuccess: (ranking, variables) => {
      setSuccessfulRanking(ranking)
      setApplied(clonePreference(variables.preference))
      setDraft(clonePreference(variables.preference))
      setComparisonCountries([])
      setComparisonNotice('')
      setSelectedCountry(null)
      setMode('ranking')
      setShowingBaseline(false)
      baselineMutation.reset()
      comparisonMutation.reset()
    },
  })
  const baselineMutation = useMutation({
    mutationFn: (request: RankingRequest) => createRanking(request),
  })
  const comparisonMutation = useMutation({
    mutationFn: (request: ComparisonRequest) => createComparison(request),
    onSuccess: () => {
      rankingScrollTop.current = rankingScrollRef.current?.scrollTop ?? 0
      setMode('comparison')
    },
  })

  const ranking = successfulRanking ?? initialRanking.data
  const dirty = !preferencesEqual(draft, applied)

  const selectProfile = (profile: Profile) => {
    setDraft(preferenceFromProfile(profile))
  }

  const changeWeight = (criterionId: string, value: number) => {
    setDraft((current) => ({
      profileId: null,
      weights: { ...current.weights, [criterionId]: value },
    }))
  }

  const applyPriorities = () => {
    if (!dirty || applyMutation.isPending) return
    const preference = clonePreference(draft)
    const request: RankingRequest = preference.profileId
      ? { profile_id: preference.profileId }
      : { weights: preference.weights }
    applyMutation.mutate({ request, preference })
  }

  const toggleComparison = (countryCode: string) => {
    setComparisonCountries((current) => {
      if (current.includes(countryCode)) {
        setComparisonNotice('')
        return current.filter((code) => code !== countryCode)
      }
      if (current.length >= 4) {
        setComparisonNotice('You can compare up to four countries. Deselect one to add another.')
        return current
      }
      setComparisonNotice(current.length === 3 ? 'Four countries selected—the comparison is full.' : '')
      return [...current, countryCode]
    })
  }

  const compareSelected = () => {
    if (comparisonCountries.length < 2 || comparisonMutation.isPending) return
    const selector = applied.profileId
      ? { profile_id: applied.profileId }
      : { weights: applied.weights }
    comparisonMutation.mutate({ country_codes: comparisonCountries, ...selector })
  }

  const toggleBaseline = () => {
    if (!ranking) return
    if (showingBaseline) {
      setShowingBaseline(false)
      return
    }
    setShowingBaseline(true)
    if (baselineMutation.data) return
    const baselineWeights = Object.fromEntries(
      Object.entries(applied.weights).map(([criterionId, weight]) => [
        criterionId,
        ranking.active_pcc_ids.includes(criterionId) ? 0 : weight,
      ]),
    )
    baselineMutation.mutate({
      weights: baselineWeights,
      top_k: catalog.countries.length,
    })
  }

  const backToRankings = () => {
    setMode('ranking')
    window.requestAnimationFrame(() => {
      if (rankingScrollRef.current) rankingScrollRef.current.scrollTop = rankingScrollTop.current
      compareButtonRef.current?.focus()
    })
  }

  const selectFromComparison = (countryCode: string) => {
    setSelectedCountry(countryCode)
    setMode('ranking')
  }

  const rankingCountry = ranking?.rankings.find((item) => item.country_code === selectedCountry)
  const selectedCatalogCountry = catalog.countries.find((item) => item.code === selectedCountry)
  const excludedCountry = ranking?.excluded_countries.find(
    (item) => item.country_code === selectedCountry,
  )

  return (
    <main id="main-content" className="page-shell">
      <section className="intro-section" aria-labelledby="intro-heading">
        <p className="eyebrow">A clearer way to explore relocation choices</p>
        <h1 id="intro-heading">{INTRODUCTION}</h1>
        <p>
          Shape the ranking with your priorities, inspect the evidence, and compare the countries
          that stand out.
        </p>
      </section>

      <div className="workspace-grid">
        <PreferencesPanel
          criteria={enabledCriteria}
          profiles={catalog.profiles}
          draft={draft}
          dirty={dirty}
          isApplying={applyMutation.isPending}
          onProfileChange={selectProfile}
          onWeightChange={changeWeight}
          onApply={applyPriorities}
          onUndo={() => setDraft(clonePreference(applied))}
        />

        <div className="ranking-workspace">
          {applyMutation.error && <ErrorNotice error={applyMutation.error} />}
          {baselineMutation.error && <ErrorNotice error={baselineMutation.error} />}
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
            <ErrorNotice error={initialRanking.error} onRetry={() => void initialRanking.refetch()} />
          )}
          {ranking && mode === 'ranking' && (
            <RankingView
              ranking={ranking}
              criteria={enabledCriteria}
              detailed={detailed}
              isUpdating={applyMutation.isPending}
              isComparing={comparisonMutation.isPending}
              selectedCountry={selectedCountry}
              comparisonCountries={comparisonCountries}
              comparisonNotice={comparisonNotice}
              baselineRanking={baselineMutation.data ?? null}
              showingBaseline={showingBaseline}
              isLoadingBaseline={baselineMutation.isPending}
              scrollRef={rankingScrollRef}
              compareButtonRef={compareButtonRef}
              onDetailedChange={setDetailed}
              onSelectCountry={setSelectedCountry}
              onToggleComparison={toggleComparison}
              onCompare={compareSelected}
              onToggleBaseline={toggleBaseline}
              onOpenSources={onOpenSources}
            />
          )}
          {mode === 'comparison' && comparisonMutation.data && (
            <ComparisonView
              comparison={comparisonMutation.data}
              criteria={enabledCriteria}
              onBack={backToRankings}
              onSelectCountry={selectFromComparison}
            />
          )}
        </div>
      </div>

      {ranking && mode === 'ranking' && selectedCountry && (
        <CountryDetails
          countryCode={selectedCountry}
          rankingCountry={rankingCountry}
          catalogCountry={selectedCatalogCountry}
          excludedCountry={excludedCountry}
          onClose={() => setSelectedCountry(null)}
        />
      )}
    </main>
  )
}

export default function App() {
  const [sourcesOpen, setSourcesOpen] = useState(false)
  const sourcesReturnFocus = useRef<HTMLElement | null>(null)
  const catalogQuery = useQuery({
    queryKey: ['catalog'],
    queryFn: ({ signal }) => fetchCatalog(signal),
  })
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
      {catalogQuery.isPending && (
        <main id="main-content" className="page-shell initial-loading" aria-live="polite">
          <div className="brand-mark brand-mark-large" aria-hidden="true">
            K
          </div>
          <h1>Loading Konsider…</h1>
          <p>Connecting to the current country catalog.</p>
        </main>
      )}
      {catalogQuery.error && (
        <main id="main-content" className="page-shell initial-error">
          <ErrorNotice error={catalogQuery.error} onRetry={() => void catalogQuery.refetch()} />
        </main>
      )}
      {catalogQuery.data && (
        <Workspace catalog={catalogQuery.data} onOpenSources={openSources} />
      )}
      {sourcesOpen && catalogQuery.data && (
        <SourcesDialog catalog={catalogQuery.data} onClose={closeSources} />
      )}
    </div>
  )
}
