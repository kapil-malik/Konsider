import { useEffect, useMemo, useRef, useState } from 'react'

import type {
  CatalogCriterionV2,
  CatalogV2,
  OpportunityFilterCatalogV2,
  RankingV2,
  TfcCatalogV2,
} from '../api/types'
import {
  COVERAGE_CONTENT,
  LOCALITY_CONTENT,
  PROFILE_CONTENT,
  countryCode,
  readableCode,
} from '../localityPresentation'

export type HelperPage = 'how' | 'criteria' | 'countries'

type SourcesDialogProps = {
  catalog: CatalogV2
  opportunityCatalog: OpportunityFilterCatalogV2
  tfcCatalog: TfcCatalogV2 | null
  ranking: RankingV2 | null
  initialPage: HelperPage
  onClose: () => void
}

const FOCUSABLE =
  'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'

const PAGES: { id: HelperPage; label: string }[] = [
  { id: 'how', label: 'How Konsider works' },
  { id: 'criteria', label: 'Criteria and sources' },
  { id: 'countries', label: 'Countries and coverage' },
]

function criterionKind(criterion: CatalogCriterionV2) {
  if (criterion.scope.derivation === 'AGGREGATED_FROM_LOCALITIES') {
    return 'Locality-derived criterion'
  }
  if (criterion.coverage.mode === 'CONDITIONAL_COMPLETE_CASE') {
    return 'Partial-coverage criterion'
  }
  return 'Full-coverage criterion'
}

function HowPage({ ranking }: { ranking: RankingV2 | null }) {
  const statuses = ranking
    ? [
        ['Coverage', COVERAGE_CONTENT[ranking.assessments.coverage.status]],
        ['Locality', LOCALITY_CONTENT[ranking.assessments.locality.status]],
        ['Profile', PROFILE_CONTENT[ranking.assessments.profile.status]],
      ] as const
    : null

  return (
    <section className="helper-page" aria-labelledby="how-page-heading">
      <h3 id="how-page-heading">From priorities to an inspectable shortlist</h3>
      <p className="lead-copy">
        Konsider separates what you prefer, which opportunities you require, and what may be
        feasible for your situation. Keeping those decisions separate makes the result easier to
        understand and challenge.
      </p>

      <ol className="how-flow">
        <li>
          <span className="step-number">1</span>
          <div>
            <h4>Shape the ranking with criteria</h4>
            <p>
              Choose a preset or adjust weights. Active criteria contribute to each country’s
              affinity score; stronger weights make that evidence matter more.
            </p>
          </div>
        </li>
        <li>
          <span className="step-number">2</span>
          <div>
            <h4>Narrow results with opportunity filters</h4>
            <p>
              Filters require a verified strong signal for every selected opportunity. They can
              remove countries from view, but never change affinity scores or reorder the base
              ranking.
            </p>
          </div>
        </li>
        <li>
          <span className="step-number">3</span>
          <div>
            <h4>Add a situation and feasibility checks</h4>
            <p>
              Your purpose, destinations, citizenship, qualifications, household, and other
              relevant details are used only by the checks you select. Checks assess supported
              routes or scenario metrics separately from preference fit.
            </p>
          </div>
        </li>
        <li>
          <span className="step-number">4</span>
          <div>
            <h4>Inspect and compare the evidence</h4>
            <p>
              Open a country or comparison to see criterion values, source lineage, locality
              derivation, opportunity evidence, and feasibility outcomes.
            </p>
          </div>
        </li>
      </ol>

      <div className="method-sections">
        <article>
          <h4>National and locality-derived criteria</h4>
          <p>
            National criteria use country-level evidence directly. Locality-derived criteria use
            comparable places within a country and aggregate the selected locality results into a
            country score. Locality analysis shows whether the same place performs well across
            active local criteria; it does not choose a city for you.
          </p>
        </article>
        <article>
          <h4>Coverage and exclusion</h4>
          <p>
            Full-coverage criteria support the stable country universe. When an active
            partial-coverage criterion lacks usable evidence, that country is excluded from the
            complete-case ranking. Its available evidence remains inspectable, and Konsider does
            not invent a replacement value.
          </p>
        </article>
        <article>
          <h4>What feasibility checks do</h4>
          <p>
            Feasibility checks answer bounded questions supported by current evidence. Missing
            inputs and insufficient destination evidence are shown explicitly. A result is not a
            visa decision, legal advice, or a general judgment about personal or household
            suitability.
          </p>
        </article>
      </div>

      <div className="status-explainer" aria-label="Current ranking status explanations">
        <div className="section-heading-row">
          <div>
            <p className="eyebrow">Reading the ranking</p>
            <h3>{statuses ? 'Your current status' : 'Status messages you may see'}</h3>
          </div>
        </div>
        {statuses ? (
          <dl>
            {statuses.map(([domain, content]) => (
              <div key={domain} role="status" aria-label={`${domain} status: ${content.label}`}>
                <dt>{domain}</dt>
                <dd>
                  <strong>{content.label}</strong>
                  <span>{content.message}</span>
                </dd>
              </div>
            ))}
          </dl>
        ) : (
          <dl>
            <div>
              <dt>Coverage</dt>
              <dd><strong>Limited-coverage ranking</strong><span>Countries without every active criterion are excluded; their available evidence remains inspectable.</span></dd>
            </div>
            <div>
              <dt>Locality</dt>
              <dd><strong>National evidence only</strong><span>No locality-derived criterion contributes to this ranking.</span></dd>
            </div>
            <div>
              <dt>Profile</dt>
              <dd><strong>No applicant profile assessed</strong><span>Results use preference weights only; no personal or household suitability is inferred.</span></dd>
            </div>
          </dl>
        )}
      </div>

      <div className="advice-note">
        Konsider supports exploration and evidence review. It is not immigration, tax, legal,
        employment, school, or personal financial advice.
      </div>
    </section>
  )
}

function RankingCriterion({ criterion, ranking }: { criterion: CatalogCriterionV2; ranking: RankingV2 | null }) {
  const contribution = ranking?.rankings
    .flatMap((country) => country.contributions)
    .find((item) => item.criterion_id === criterion.id)

  return (
    <article className="source-criterion">
      <div className="source-criterion-heading">
        <div>
          <p className="eyebrow">{criterionKind(criterion)}</p>
          <h4>{criterion.displayName}</h4>
        </div>
        <div className="badge-row">
          {!criterion.ready && <span className="badge badge-unavailable">! Unavailable</span>}
          <span className="badge badge-scope">
            {criterion.scope.derivation === 'AGGREGATED_FROM_LOCALITIES' ? 'Locality-derived' : 'National'}
          </span>
          {criterion.experimental && <span className="badge badge-experimental">Experimental</span>}
        </div>
      </div>
      <p>{criterion.description}</p>
      <dl className="source-metadata-grid">
        <div><dt>Coverage</dt><dd>{criterion.coverage.valid_country_count}/{criterion.coverage.stable_country_count} countries · {readableCode(criterion.coverage.mode)}</dd></div>
        <div><dt>Scope</dt><dd>{readableCode(criterion.scope.evidence_level)} evidence · {readableCode(criterion.scope.derivation)}</dd></div>
        <div><dt>Applicability</dt><dd>{readableCode(criterion.applicability.mode)}</dd></div>
        {criterion.scope.locality_universe_id && (
          <div><dt>Locality universe</dt><dd><code>{criterion.scope.locality_universe_id}</code></dd></div>
        )}
        {criterion.scope.aggregation_policy_id && (
          <div><dt>Aggregation</dt><dd>{contribution?.aggregation_policy ? `${readableCode(contribution.aggregation_policy.method)} · ` : 'Server policy · '}<code>{criterion.scope.aggregation_policy_id}</code></dd></div>
        )}
      </dl>
      {criterion.sources.map((source) => (
        <div className="source-record" key={`${source.source_id}:${source.source_version}:${source.role}`}>
          <div><span>Source</span><strong>{source.publisher ?? source.source_id}</strong></div>
          <div><span>Version and role</span><strong>{source.source_version}{source.role ? ` · ${readableCode(source.role)}` : ''}</strong></div>
          {source.canonical_page_url && <a href={source.canonical_page_url} target="_blank" rel="noreferrer">Visit source website</a>}
        </div>
      ))}
      <p className="transformation-note">Scoring: <code>{criterion.scoring_method_version}</code>. {criterion.caveats.join(' ')}</p>
    </article>
  )
}

function CriteriaPage({ catalog, opportunityCatalog, tfcCatalog, ranking }: Omit<SourcesDialogProps, 'initialPage' | 'onClose'>) {
  return (
    <section className="helper-page" aria-labelledby="criteria-page-heading">
      <div className="section-heading-row">
        <div>
          <h3 id="criteria-page-heading">Criteria and source lineage</h3>
          <p className="lead-copy">The complete catalog is grouped by the role each item plays. Ranking criteria shape affinity; opportunity filters narrow results; feasibility checks assess a supplied situation.</p>
        </div>
        <span className="release-chip">Release {catalog.release_id}</span>
      </div>

      <div className="criteria-group-heading"><p className="eyebrow">Preference evidence</p><h4>Ranking criteria</h4></div>
      <div className="source-criteria-list">
        {catalog.criteria.map((criterion) => <RankingCriterion criterion={criterion} ranking={ranking} key={criterion.id} />)}
      </div>

      <div className="criteria-group-heading">
        <p className="eyebrow">Required opportunities</p>
        <h4>Opportunity filters</h4>
        <p>
          Only a verified strong signal passes. Insufficient evidence is not negative and does
          not mean an opportunity is absent. Filters never change weights, affinity scores, or
          the order of countries that pass. Evidence freshness is shown in country details.
        </p>
        <p>
          Education evidence describes research-intensive university ecosystems. It does not
          establish teaching quality, programme availability, admission access, affordability,
          accreditation, or applicant eligibility.
        </p>
      </div>
      <div className="source-criteria-list compact-source-list">
        {opportunityCatalog.definitions.map((definition) => (
          <article className="source-criterion" key={definition.id}>
            <div className="source-criterion-heading"><div><p className="eyebrow">{definition.sectionName}</p><h4>{definition.displayName}</h4></div><span className="badge badge-scope">{definition.coverage.assessable_count} assessable</span></div>
            <p>{definition.meaning}</p>
            {definition.source_vintage.map((source) => <div className="source-record" key={`${definition.id}:${source.source_id}`}><div><span>Source</span><strong>{source.publisher}</strong></div><div><span>Version</span><strong>{source.source_version}</strong></div></div>)}
            {definition.limitations.length > 0 && <p className="transformation-note">{definition.limitations.join(' ')}</p>}
          </article>
        ))}
      </div>

      <div className="criteria-group-heading"><p className="eyebrow">Situation evidence</p><h4>Feasibility checks</h4><p>Explicitly selected checks with no affinity-score impact.</p></div>
      <div className="source-criteria-list compact-source-list">
        {tfcCatalog ? tfcCatalog.definitions.map((definition) => (
          <article className="source-criterion" key={definition.id}>
            <div className="source-criterion-heading"><div><p className="eyebrow">{readableCode(definition.check_kind)}</p><h4>{definition.displayName}</h4></div><span className="badge badge-scope">{definition.supported_destination_codes.length} destinations</span></div>
            <p>{definition.user_question}</p>
            <p>{definition.supported_profile_boundary}</p>
            {definition.source_summary.map((source) => <div className="source-record" key={`${definition.id}:${source.source_id}`}><div><span>Source</span><strong>{source.publisher}</strong></div><div><span>Effective</span><strong>{source.effective_from} onward</strong></div></div>)}
            {definition.limitations.length > 0 && <p className="transformation-note">{definition.limitations.join(' ')}</p>}
          </article>
        )) : <p className="empty-helper-state">Feasibility-check metadata is currently unavailable.</p>}
      </div>
    </section>
  )
}

function CountriesPage({ catalog }: { catalog: CatalogV2 }) {
  const [query, setQuery] = useState('')
  const criterionNames = useMemo(() => new Map(catalog.criteria.map((criterion) => [criterion.id, criterion.displayName])), [catalog.criteria])
  const rows = useMemo(() => {
    const normalized = query.trim().toLocaleLowerCase()
    return catalog.country_coverage.filter(({ country }) => !normalized || country.display_name.toLocaleLowerCase().startsWith(normalized) || countryCode(country.entity_id).toLocaleLowerCase().startsWith(normalized))
  }, [catalog.country_coverage, query])

  return (
    <section className="helper-page" aria-labelledby="countries-page-heading">
      <div className="section-heading-row">
        <div><h3 id="countries-page-heading">Countries and criterion coverage</h3><p className="lead-copy">Coverage reflects the current release. A missing, stale, invalid, or rejected value is shown explicitly and is never silently estimated.</p></div>
        <span className="release-chip">{catalog.countries.length} countries</span>
      </div>
      <label className="coverage-search"><span>Search countries</span><input type="search" value={query} placeholder="Country name or code" onChange={(event) => setQuery(event.target.value)} /></label>
      <div className="coverage-table-wrap">
        <table className="coverage-table">
          <thead><tr><th scope="col">Code</th><th scope="col">Country</th><th scope="col">Coverage</th><th scope="col">Missing or unavailable criteria</th></tr></thead>
          <tbody>
            {rows.map(({ country, criteria }) => {
              const gaps = criteria.filter((criterion) => criterion.outcome !== 'valid')
              return <tr key={country.entity_id}>
                <td><code>{country.country_codes[0] ?? countryCode(country.entity_id)}</code></td>
                <th scope="row">{country.display_name}</th>
                <td><span className={`coverage-status ${gaps.length ? 'coverage-status-limited' : 'coverage-status-complete'}`}>{criteria.length - gaps.length}/{criteria.length} available</span></td>
                <td>{gaps.length ? <ul className="coverage-gap-list">{gaps.map((gap) => <li key={gap.criterion_id}><span aria-hidden="true">!</span><span><strong>{criterionNames.get(gap.criterion_id) ?? gap.criterion_id}</strong><small>{readableCode(gap.outcome)}{gap.reason_codes.length ? ` · ${gap.reason_codes.map(readableCode).join(', ')}` : ''}</small></span></li>)}</ul> : <span className="coverage-complete-copy">Complete criterion coverage</span>}</td>
              </tr>
            })}
          </tbody>
        </table>
        {rows.length === 0 && <p className="empty-helper-state">No countries match “{query}”.</p>}
      </div>
    </section>
  )
}

export function SourcesDialog({ catalog, opportunityCatalog, tfcCatalog, ranking, initialPage, onClose }: SourcesDialogProps) {
  const [page, setPage] = useState(initialPage)
  const dialogRef = useRef<HTMLDivElement>(null)
  const closeRef = useRef<HTMLButtonElement>(null)
  const selectedTabRef = useRef<HTMLButtonElement>(null)
  const selectedPage = PAGES.find((item) => item.id === page) ?? PAGES[0]

  useEffect(() => {
    selectedTabRef.current?.scrollIntoView?.({ block: 'nearest', inline: 'center' })
  }, [page])

  useEffect(() => {
    closeRef.current?.focus()
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') { event.preventDefault(); onClose(); return }
      if (event.key !== 'Tab' || !dialogRef.current) return
      const items = [...dialogRef.current.querySelectorAll<HTMLElement>(FOCUSABLE)]
      if (!items.length) return
      const first = items[0]
      const last = items[items.length - 1]
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus() }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus() }
    }
    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [onClose])

  return (
    <div className="dialog-backdrop" role="presentation" onMouseDown={onClose}>
      <div className="sources-dialog" ref={dialogRef} role="dialog" aria-modal="true" aria-labelledby="sources-heading" onMouseDown={(event) => event.stopPropagation()}>
        <header className="dialog-header"><div><p className="eyebrow">Guidance and provenance</p><h2 id="sources-heading">{selectedPage.label}</h2></div><button ref={closeRef} className="icon-button" aria-label={`Close ${selectedPage.label}`} onClick={onClose}>×</button></header>
        <nav className="helper-tabs" role="tablist" aria-label="Konsider help pages">
          {PAGES.map((item) => <button ref={page === item.id ? selectedTabRef : undefined} type="button" role="tab" aria-selected={page === item.id} key={item.id} onClick={() => setPage(item.id)}>{item.label}</button>)}
        </nav>
        <div className="dialog-content">
          {page === 'how' && <HowPage ranking={ranking} />}
          {page === 'criteria' && <CriteriaPage catalog={catalog} opportunityCatalog={opportunityCatalog} tfcCatalog={tfcCatalog} ranking={ranking} />}
          {page === 'countries' && <CountriesPage catalog={catalog} />}
        </div>
      </div>
    </div>
  )
}
