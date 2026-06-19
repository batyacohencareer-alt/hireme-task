import { useCallback, useRef, useState } from 'react'
import { evaluateUser } from '../services/api'
import { extractUsername } from '../utils/extractUsername'

/**
 * Custom hook encapsulating the evaluation workflow.
 *
 * Handles input validation, API calls, loading state,
 * error handling, and request cancellation via AbortController.
 */
export function useEvaluate() {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  const [errorStatus, setErrorStatus] = useState(null)
  const [isLoading, setIsLoading] = useState(false)

  const abortRef = useRef(null)

  const analyze = useCallback(async (rawInput) => {
    // Cancel any in-flight request
    abortRef.current?.abort()

    const username = extractUsername(rawInput)
    if (!username) {
      setError('Please enter a valid GitHub username.')
      setErrorStatus(null)
      return
    }

    const controller = new AbortController()
    abortRef.current = controller

    setIsLoading(true)
    setError(null)
    setErrorStatus(null)
    setData(null)

    try {
      const result = await evaluateUser(username, controller.signal)
      setData(result)
    } catch (err) {
      if (err.name === 'AbortError') return
      setError(err.message || 'Network error')
      setErrorStatus(err.status ?? null)
    } finally {
      setIsLoading(false)
    }
  }, [])

  const clearError = useCallback(() => {
    setError(null)
    setErrorStatus(null)
  }, [])

  const cancel = useCallback(() => {
    abortRef.current?.abort()
    setIsLoading(false)
  }, [])

  return { data, error, errorStatus, isLoading, analyze, clearError, cancel }
}
