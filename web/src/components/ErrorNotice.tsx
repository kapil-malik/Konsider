import { ApiError } from '../api/client'

type ErrorNoticeProps = {
  error: unknown
  title?: string
  onRetry?: () => void
}

function errorSummary(error: unknown): { title: string; message: string } {
  if (!(error instanceof ApiError)) {
    return { title: 'Something went wrong', message: 'Please try again.' }
  }
  if (error.code === 'release_unavailable' || error.code === 'unsupported_release_contract') {
    return {
      title: 'Country data is temporarily unavailable',
      message: 'Konsider could not load a validated data release. Try again after the API is ready.',
    }
  }
  if (error.status === 422) {
    return {
      title: 'Those priorities could not be applied',
      message: 'The server rejected the request. Review your choices and try again.',
    }
  }
  if (error.code === 'network_error') {
    return {
      title: 'Konsider cannot reach the API',
      message: 'Check that the local API is running, then retry.',
    }
  }
  return {
    title: 'The request could not be completed',
    message: 'Konsider kept your existing results safe. Please try again.',
  }
}

export function ErrorNotice({ error, title, onRetry }: ErrorNoticeProps) {
  const summary = errorSummary(error)
  return (
    <div className="error-notice" role="alert">
      <div>
        <h3>{title ?? summary.title}</h3>
        <p>{summary.message}</p>
      </div>
      {onRetry && (
        <button className="button button-secondary" onClick={onRetry}>
          Retry
        </button>
      )}
    </div>
  )
}
