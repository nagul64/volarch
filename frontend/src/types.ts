export interface Student {
  id: number
  name: string
  school: string
  grade: string
  zip_code: string
  latitude: number
  longitude: number
  max_hours_per_week: number
  skills: string[]
  interests: string[]
  bio: string
}

export interface Opportunity {
  id: number
  title: string
  org_name: string
  category: string
  description: string
  tags: string[]
  zip_code: string
  latitude: number
  longitude: number
  hours_min: number
  hours_max: number
  required_skills: string[]
  helpful_skills: string[]
}

export interface ScoreFactor {
  name: string
  weight: number
  score: number
  note: string
}

export interface MatchResult {
  opportunity: Opportunity
  total: number
  breakdown: ScoreFactor[]
  reasons: string[]
}

export interface Diagnostics {
  provider: string
  description: string
}

export interface SearchProfile {
  skills: string[]
  interests: string[]
  max_hours_per_week: number
  zip_code: string
  bio: string
  latitude: number | null
  longitude: number | null
}

export interface SearchResult {
  extraction: string
  semantic: string
  profile: SearchProfile
  matches: MatchResult[]
}