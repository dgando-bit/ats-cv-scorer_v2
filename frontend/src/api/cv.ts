import type {
	CV,
} from '../types/cv'


const API_URL =
	import.meta.env.VITE_API_URL
	?? 'http://localhost:8000'


export async function extractCV(
	file: File,
): Promise<CV> {
	const formData = new FormData()

	formData.append(
		'file',
		file,
	)

	const response = await fetch(
		`${API_URL}/api/cv/extract`,
		{
			method: 'POST',
			body: formData,
		},
	)

	if (!response.ok) {
		let message =
			"Impossible d'analyser le CV."

		try {
			const data = await response.json()

			if (
				typeof data.detail === 'string'
			) {
				message = data.detail
			}
		} catch {
			// La réponse n'est pas du JSON.
		}

		throw new Error(
			message,
		)
	}

	return response.json()
}
