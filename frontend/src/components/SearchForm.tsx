import { useState } from 'react'
import LocationAutocomplete from './LocationAutocomplete'

import type {
	LocationSuggestion,
} from '../api/locations'

export interface SearchFormValues {
	file: File
	keywords: string
	location: LocationSuggestion | null
	limit: number
}

interface SearchFormProps {
	onSubmit: (values: SearchFormValues) => void
	isLoading?: boolean
}

export default function SearchForm({
									   onSubmit,
									   isLoading = false,
								   }: SearchFormProps) {
	const [file, setFile] = useState<File | null>(null)
	const [keywords, setKeywords] = useState('')
	const [location, setLocation] =
		useState<LocationSuggestion | null>(null)
	const [limit, setLimit] = useState(5)

	function handleSubmit(
		event: React.FormEvent<HTMLFormElement>,
	) {
		event.preventDefault()

		if (!file || !keywords.trim()) {
			return
		}

		onSubmit({
			file,
			keywords: keywords.trim(),
			location,
			limit,
		})
	}

	return (
		<form
			onSubmit={handleSubmit}
			className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"
		>
			<div className="grid gap-5 lg:grid-cols-[1.4fr_1.5fr_1fr_160px_auto] lg:items-end">
				<div>
					<label
						htmlFor="cv"
						className="mb-2 block text-sm font-medium text-slate-700"
					>
						Votre CV
					</label>

					<input
						id="cv"
						type="file"
						accept="application/pdf"
						onChange={(event) => {
							setFile(
								event.target.files?.[0] ?? null,
							)
						}}
						className="block w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm text-slate-700"
					/>

					{file && (
						<p className="mt-2 truncate text-sm text-slate-500">
							{file.name}
						</p>
					)}
				</div>

				<div>
					<label
						htmlFor="keywords"
						className="mb-2 block text-sm font-medium text-slate-700"
					>
						Mots-clés
					</label>

					<input
						id="keywords"
						type="text"
						value={keywords}
						onChange={(event) => {
							setKeywords(event.target.value)
						}}
						placeholder="Machine Learning Engineer"
						className="w-full rounded-xl border border-slate-300 px-3 py-2 text-base outline-none focus:border-blue-500"
					/>
				</div>

				<div>
					{/*<label*/}
					{/*	htmlFor="location"*/}
					{/*	className="mb-2 block text-sm font-medium text-slate-700"*/}
					{/*>*/}
					{/*	Localisation*/}
					{/*</label>*/}
					<LocationAutocomplete
						value={location}
						onChange={setLocation}
					/>
					{/*<input*/}
					{/*	id="location"*/}
					{/*	type="text"*/}
					{/*	value={location}*/}
					{/*	onChange={(event) => {*/}
					{/*		setLocation(event.target.value)*/}
					{/*	}}*/}
					{/*	placeholder="Paris"*/}
					{/*	className="w-full rounded-xl border border-slate-300 px-3 py-2 text-base outline-none focus:border-blue-500"*/}
					{/*/>*/}
				</div>

				<div>
					<label
						htmlFor="limit"
						className="mb-2 block text-sm font-medium text-slate-700"
					>
						Nombre d'offres
					</label>

					<select
						id="limit"
						value={limit}
						onChange={(event) => {
							setLimit(Number(event.target.value))
						}}
						className="w-full rounded-xl border border-slate-300 px-3 py-2 text-base outline-none focus:border-blue-500"
					>
						<option value={5}>5</option>
						<option value={10}>10</option>
						<option value={20}>20</option>
					</select>
				</div>

				<button
					type="submit"
					disabled={
						isLoading
						|| !file
						|| !keywords.trim()
					}
					className="rounded-xl bg-blue-600 px-5 py-2.5 font-medium text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-300"
				>
					{isLoading
						? 'Analyse...'
						: 'Analyser les offres'}
				</button>
			</div>
		</form>
	)
}
