import type { JobRankingResult } from '../types/ranking'

const API_URL =
	import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export interface RankJobsParams {
	file: File
	keywords: string
	location?: string
	limit?: number
}

export async function rankJobs({
								   file,
								   keywords,
								   location,
								   limit = 5,
							   }: RankJobsParams): Promise<JobRankingResult> {
	const formData = new FormData()

	formData.append('file', file)
	formData.append('keywords', keywords)

	if (location) {
		formData.append('location', location)
	}

	formData.append('limit', String(limit))

	const response = await fetch(
		`${API_URL}/api/jobs/rank`,
		{
			method: 'POST',
			body: formData,
		},
	)

	if (!response.ok) {
		const message = await response.text()

		throw new Error(
			message || `Erreur API (${response.status})`,
		)
	}

	return response.json()
}
