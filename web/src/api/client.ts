import type {
  CatalogV3,
  ComparisonRequestV3,
  ComparisonV3,
  CountryDetailsV3,
  ErrorEnvelope,
  OpportunityFilterCatalogV3,
  RankingRequestV3,
  RankingV3,
  TfcCatalogV3,
  WeightSelectionV3,
} from './types'

const DEFAULT_API_BASE_URL = 'http://127.0.0.1:8000/api/v3'
const API_BASE_URL = (import.meta.env.VITE_KONSIDER_API_BASE_URL || DEFAULT_API_BASE_URL).replace(
  /\/$/,
  '',
)

export class ApiError extends Error {
  readonly status: number
  readonly code: string
  readonly details: Record<string, unknown>
  readonly requestId: string | null

  constructor(status: number, envelope?: ErrorEnvelope) {
    const body = envelope?.error
    super(body?.message || (status ? `The request failed (${status}).` : 'The API is unreachable.'))
    this.name = 'ApiError'
    this.status = status
    this.code = body?.code || (status ? 'http_error' : 'network_error')
    this.details = body?.details || {}
    this.requestId = body?.request_id || null
  }
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  let response: Response
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      headers: {
        ...(init.body ? { 'Content-Type': 'application/json' } : {}),
        ...init.headers,
      },
    })
  } catch {
    throw new ApiError(0)
  }

  if (!response.ok) {
    let envelope: ErrorEnvelope | undefined
    try {
      envelope = (await response.json()) as ErrorEnvelope
    } catch {
      envelope = undefined
    }
    throw new ApiError(response.status, envelope)
  }
  return (await response.json()) as T
}

export const fetchCatalog = (signal?: AbortSignal) =>
  request<CatalogV3>('/catalog', { signal })

export const fetchOpportunityFilters = (signal?: AbortSignal) =>
  request<OpportunityFilterCatalogV3>('/opportunity-filters', { signal })

export const fetchTfcs = (signal?: AbortSignal) =>
  request<TfcCatalogV3>('/tfcs', { signal })

export const createRanking = (payload: RankingRequestV3, signal?: AbortSignal) =>
  request<RankingV3>('/rankings', {
    method: 'POST',
    body: JSON.stringify(payload),
    signal,
  })

export const fetchCountryDetails = (
  countryCode: string,
  payload: WeightSelectionV3,
  signal?: AbortSignal,
) =>
  request<CountryDetailsV3>(`/countries/${encodeURIComponent(countryCode)}/details`, {
    method: 'POST',
    body: JSON.stringify(payload),
    signal,
  })

export const createComparison = (payload: ComparisonRequestV3, signal?: AbortSignal) =>
  request<ComparisonV3>('/comparisons', {
    method: 'POST',
    body: JSON.stringify(payload),
    signal,
  })

export const apiBaseUrl = API_BASE_URL
