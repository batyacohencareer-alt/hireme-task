/**
 * Extract a GitHub username from raw user input.
 *
 * Accepts plain usernames, full GitHub profile URLs (with or without scheme),
 * and URLs with extra path segments, query params, or fragments.
 *
 * @param {string} input - Raw user input.
 * @returns {string} The extracted username, or an empty string.
 */
export function extractUsername(input) {
  if (typeof input !== 'string') return ''

  let cleaned = input.trim()
  if (!cleaned) return ''

  // Strip query parameters and fragments
  const queryIndex = cleaned.indexOf('?')
  if (queryIndex !== -1) cleaned = cleaned.slice(0, queryIndex)

  const hashIndex = cleaned.indexOf('#')
  if (hashIndex !== -1) cleaned = cleaned.slice(0, hashIndex)

  // Remove GitHub URL prefix (with or without scheme)
  cleaned = cleaned.replace(/^https?:\/\/(www\.)?github\.com\//i, '')
  cleaned = cleaned.replace(/^github\.com\//i, '')
  cleaned = cleaned.replace(/\/+$/g, '')

  // Isolate first path segment (the username)
  const slashIndex = cleaned.indexOf('/')
  if (slashIndex !== -1) {
    cleaned = cleaned.slice(0, slashIndex)
  }

  return cleaned
}
