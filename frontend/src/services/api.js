const API_BASE_URL =
  import.meta.env.VITE_API_URL || 'http://localhost:8000'

/**
 * Evaluate a GitHub user's repositories.
 *
 * @param {string} username - GitHub username.
 * @param {AbortSignal} [signal] - Optional AbortController signal.
 * @returns {Promise<object>} Evaluation response.
 */
export async function evaluateUser(username, signal) {
  const url = `${API_BASE_URL}/api/evaluate/${encodeURIComponent(username)}`

  const response = await fetch(url, { signal })

  if (!response.ok) {
    let message = `Request failed with status ${response.status}`
    try {
      const body = await response.json()
      if (body?.detail) message = body.detail
      else if (body?.error) message = body.error
      else if (body?.message) message = body.message
    } catch {
      // Response is not JSON — use status text
    }

    const error = new Error(message)
    error.status = response.status
    throw error
  }

  return response.json()
}
