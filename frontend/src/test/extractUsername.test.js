import { describe, expect, it } from 'vitest'
import { extractUsername } from '../utils/extractUsername'

describe('extractUsername', () => {
  it('returns plain username as-is', () => {
    expect(extractUsername('octocat')).toBe('octocat')
  })

  it('trims whitespace', () => {
    expect(extractUsername('  octocat  ')).toBe('octocat')
  })

  it('extracts from full HTTPS URL', () => {
    expect(extractUsername('https://github.com/octocat')).toBe('octocat')
  })

  it('extracts from URL with trailing slash', () => {
    expect(extractUsername('https://github.com/octocat/')).toBe('octocat')
  })

  it('extracts from URL with www prefix', () => {
    expect(extractUsername('https://www.github.com/octocat')).toBe('octocat')
  })

  it('extracts username only from URL with repo path', () => {
    expect(extractUsername('https://github.com/octocat/hello-world')).toBe('octocat')
  })

  it('extracts username from deep URL path', () => {
    expect(extractUsername('https://github.com/octocat/repo/tree/main')).toBe('octocat')
  })

  it('strips query parameters', () => {
    expect(extractUsername('https://github.com/octocat?tab=repos')).toBe('octocat')
  })

  it('strips fragment', () => {
    expect(extractUsername('https://github.com/octocat#readme')).toBe('octocat')
  })

  it('handles bare github.com path', () => {
    expect(extractUsername('github.com/octocat')).toBe('octocat')
  })

  it('returns empty string for empty input', () => {
    expect(extractUsername('')).toBe('')
  })

  it('returns empty string for whitespace-only input', () => {
    expect(extractUsername('   ')).toBe('')
  })

  it('returns empty string for non-string input', () => {
    expect(extractUsername(123)).toBe('')
    expect(extractUsername(null)).toBe('')
    expect(extractUsername(undefined)).toBe('')
  })
})
