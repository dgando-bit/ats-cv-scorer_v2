import type {
	JobRankingResult,
} from './ranking'


export interface AnalysisHistoryItem {
	id: string
	createdAt: string

	keywords: string
	location: string | null
	limit: number

	candidateName: string | null

	result: JobRankingResult
}
