import type {
	AnalysisHistoryItem,
} from '../types/history'

import type {
	JobRankingResult,
} from '../types/ranking'


const STORAGE_KEY =
	'ats-cv-scorer:analysis-history'

const MAX_HISTORY_ITEMS = 20


interface SaveAnalysisParams {
	keywords: string
	location: string | null
	limit: number
	result: JobRankingResult
}


export function getAnalysisHistory():
	AnalysisHistoryItem[] {
	if (
		typeof window === 'undefined'
	) {
		return []
	}

	try {
		const raw = localStorage.getItem(
			STORAGE_KEY,
		)

		if (!raw) {
			return []
		}

		const parsed = JSON.parse(
			raw,
		) as AnalysisHistoryItem[]

		if (!Array.isArray(parsed)) {
			return []
		}

		return parsed
	} catch {
		return []
	}
}


export function saveAnalysis(
	params: SaveAnalysisParams,
): AnalysisHistoryItem {
	const history =
		getAnalysisHistory()

	const item: AnalysisHistoryItem = {
		id: crypto.randomUUID(),
		createdAt: new Date().toISOString(),

		keywords: params.keywords,
		location: params.location,
		limit: params.limit,

		candidateName:
			params.result.candidate_name
			?? null,

		result: params.result,
	}

	const updated = [
		item,
		...history,
	].slice(
		0,
		MAX_HISTORY_ITEMS,
	)

	localStorage.setItem(
		STORAGE_KEY,
		JSON.stringify(updated),
	)

	return item
}


export function deleteAnalysis(
	id: string,
): AnalysisHistoryItem[] {
	const updated =
		getAnalysisHistory().filter(
			(item) => item.id !== id,
		)

	localStorage.setItem(
		STORAGE_KEY,
		JSON.stringify(updated),
	)

	return updated
}


export function clearAnalysisHistory(): void {
	localStorage.removeItem(
		STORAGE_KEY,
	)
}
