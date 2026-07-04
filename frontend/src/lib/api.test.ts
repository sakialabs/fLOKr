import { describe, expect, it } from 'vitest'
import { normalizeApiBaseUrl } from './api'

describe('normalizeApiBaseUrl', () => {
  it('defaults blank values to the same-origin Next API proxy', () => {
    expect(normalizeApiBaseUrl('')).toBe('/api')
  })

  it('keeps the same-origin Next API proxy when it is configured directly', () => {
    expect(normalizeApiBaseUrl('/api')).toBe('/api')
  })

  it('adds the Django API prefix when the environment URL points at the backend origin', () => {
    expect(normalizeApiBaseUrl('http://localhost:8000')).toBe('http://localhost:8000/api')
  })

  it('keeps an existing API prefix and removes trailing slashes', () => {
    expect(normalizeApiBaseUrl('http://localhost:8000/api/')).toBe('http://localhost:8000/api')
  })
})
