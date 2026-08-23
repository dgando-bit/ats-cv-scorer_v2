export interface MatchDetails {
  skills: number
  tools: number
  languages: number
  experience: number
  education: number
}

export interface MatchResult {
  score: number
  details: MatchDetails

  matched_skills: string[]
  missing_skills: string[]

  matched_tools: string[]
  missing_tools: string[]

  matched_languages: string[]
  missing_languages: string[]
}

export interface MatchExplanation {
  summary: string
  strengths: string[]
  weaknesses: string[]
  recommendations: string[]
}

export interface JobOffer {
  id?: string | null
  title: string
  company?: string | null
  description: string

  location?: string | null
  contract_type?: string | null

  skills: string[]
  tools: string[]
  languages: string[]

  experience_required?: string | null
  education_required?: string | null

  source?: string | null
  source_url?: string | null
}

export interface RankedJob {
  job: JobOffer
  match: MatchResult
  explanation: MatchExplanation
}

export interface JobRankingResult {
  candidate_name?: string | null
  jobs: RankedJob[]
}