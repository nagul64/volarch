import type { Diagnostics, MatchResult, Opportunity, SearchResult, Student } from './types'

const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://127.0.0.1:8000'

export class ApiError extends Error {}

async function getJson<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`)
  if (!res.ok) {
    throw new ApiError(`GET ${path} failed: ${res.status} ${res.statusText}`)
  }
  return res.json() as Promise<T>
}

export const api = {
  students: () => getJson<Student[]>('/students'),
  opportunities: () => getJson<Opportunity[]>('/opportunities'),
  diagnostics: () => getJson<Diagnostics>('/diagnostics/semantic'),
  matches: (studentId: number, limit = 10) =>
    getJson<MatchResult[]>(`/students/${studentId}/matches?limit=${limit}`),
  search: async (query: string, zip?: string, limit = 10): Promise<SearchResult> => {
    const res = await fetch(`${API_BASE}/search?limit=${limit}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, zip: zip || null }),
    })
    if (!res.ok) {
      const detail = await res.json().catch(() => null)
      throw new ApiError(detail?.detail ?? `POST /search failed: ${res.status} ${res.statusText}`)
    }
    return res.json() as Promise<SearchResult>
  },
}