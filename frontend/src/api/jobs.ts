import type {
	JobRankingResult,
} from '../types/ranking'


const API_URL =
	import.meta.env.VITE_API_URL
	?? 'http://localhost:8000'


export interface RankJobsParams {
	file: File
	keywords: string
	location?: string
	inseeCode?: string
	limit?: number
}


interface ApiErrorDetail {
	code?: string
	message?: string
	location?: string
}


interface ApiErrorResponse {
	detail?: string | ApiErrorDetail
}


export class ApiError extends Error {
	status: number
	code?: string
	location?: string

	constructor({
					message,
					status,
					code,
					location,
				}: {
		message: string
		status: number
		code?: string
		location?: string
	}) {
		super(message)

		this.name = 'ApiError'
		this.status = status
		this.code = code
		this.location = location
	}
}


export async function rankJobs({
								   file,
								   keywords,
								   location,
								   inseeCode,
								   limit = 5,
							   }: RankJobsParams): Promise<JobRankingResult> {
	const formData = new FormData()

	formData.append(
		'file',
		file,
	)

	formData.append(
		'keywords',
		keywords,
	)

	if (location) {
		formData.append(
			'location',
			location,
		)
	}

	if (inseeCode) {
		formData.append(
			'insee_code',
			inseeCode,
		)
	}

	formData.append(
		'limit',
		String(limit),
	)

	const response = await fetch(
		`${API_URL}/api/jobs/rank`,
		{
			method: 'POST',
			body: formData,
		},
	)

	if (!response.ok) {
		let payload: ApiErrorResponse | null =
			null

		try {
			payload =
				await response.json()
		} catch {
			// La réponse n'est pas JSON.
		}

		const detail =
			payload?.detail

		if (
			detail
			&& typeof detail === 'object'
		) {
			throw new ApiError({
				message:
					detail.message
					?? `Erreur API (${response.status})`,
				status: response.status,
				code: detail.code,
				location: detail.location,
			})
		}

		if (
			typeof detail === 'string'
		) {
			throw new ApiError({
				message: detail,
				status: response.status,
			})
		}

		throw new ApiError({
			message:
				`Erreur API (${response.status})`,
			status: response.status,
		})
	}

	return response.json()
}
