export interface LocationSuggestion {
	label: string
	city: string
	postal_code: string | null
	insee_code: string
}

const API_URL =
	import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export async function searchLocations(
	query: string,
	limit = 8,
): Promise<LocationSuggestion[]> {
	const params = new URLSearchParams({
		q: query,
		limit: String(limit),
	})

	const response = await fetch(
		`${API_URL}/api/locations/search?${params}`,
	)

	if (!response.ok) {
		throw new Error(
			`Erreur lors de la recherche des villes (${response.status})`,
		)
	}

	return response.json()
}
