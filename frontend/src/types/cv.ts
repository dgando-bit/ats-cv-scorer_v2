export interface Contact {
	email?: string | null
	phone?: string | null
	location?: string | null
	website?: string | null
}


export interface Experience {
	company?: string | null
	role?: string | null
	start_date?: string | null
	end_date?: string | null
	description: string[]
}


export interface Education {
	institution?: string | null
	degree?: string | null
	year?: string | null
	level?: string | null
}


export interface CV {
	candidate_name?: string | null
	title?: string | null

	contact: Contact

	profile?: string | null

	experiences: Experience[]
	education: Education[]

	skills: string[]
	soft_skills: string[]
	tools: string[]
	languages: string[]
}
