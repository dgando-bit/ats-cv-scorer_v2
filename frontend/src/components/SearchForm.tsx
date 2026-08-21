import {
	useState,
} from 'react'

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
	onSubmit: (
		values: SearchFormValues,
	) => void

	isLoading?: boolean
}


export default function SearchForm({
									   onSubmit,
									   isLoading = false,
								   }: SearchFormProps) {
	const [
		file,
		setFile,
	] = useState<File | null>(
		null,
	)

	const [
		keywords,
		setKeywords,
	] = useState('')

	const [
		location,
		setLocation,
	] = useState<LocationSuggestion | null>(
		null,
	)

	const [
		limit,
		setLimit,
	] = useState(5)


	function handleSubmit(
		event: React.FormEvent<HTMLFormElement>,
	) {
		event.preventDefault()

		if (
			!file
			|| !keywords.trim()
		) {
			return
		}

		onSubmit({
			file,
			keywords:
				keywords.trim(),
			location,
			limit,
		})
	}


	return (
		<form
			onSubmit={
				handleSubmit
			}
			className="
				rounded-2xl border
				border-slate-200 bg-white
				p-4 shadow-sm
				sm:p-5 lg:p-6
			"
		>
			<div
				className="
					grid grid-cols-1
					gap-5
					md:grid-cols-2
					xl:grid-cols-[1.35fr_1.35fr_1fr_150px_auto]
					xl:items-end
				"
			>
				{/* CV */}
				<div className="min-w-0">
					<label
						htmlFor="cv"
						className="
							mb-2 block text-sm
							font-medium text-slate-700
						"
					>
						Votre CV
					</label>

					<label
						htmlFor="cv"
						className="
							flex min-h-11
							cursor-pointer items-center
							gap-3 rounded-xl
							border border-slate-300
							bg-white px-3 py-2
							transition
							hover:border-blue-400
							hover:bg-blue-50/30
						"
					>
						<span
							className="
								flex h-8 w-8
								shrink-0 items-center
								justify-center
								rounded-lg bg-blue-50
								text-blue-600
							"
							aria-hidden="true"
						>
							▤
						</span>

						<span
							className="
								min-w-0 flex-1
								truncate text-sm
								text-slate-600
							"
						>
							{file
								? file.name
								: 'Choisir un fichier PDF'}
						</span>

						<span
							className="
								hidden shrink-0
								text-xs font-medium
								text-blue-600
								sm:inline
							"
						>
							Parcourir
						</span>
					</label>

					<input
						id="cv"
						type="file"
						accept="application/pdf,.pdf"
						onChange={
							(event) => {
								setFile(
									event.target
										.files?.[0]
									?? null,
								)
							}
						}
						className="sr-only"
					/>

					{file && (
						<p
							className="
								mt-2 truncate
								text-xs text-slate-400
							"
							title={
								file.name
							}
						>
							{(
								file.size
								/ 1024
								/ 1024
							).toFixed(2)} Mo
						</p>
					)}
				</div>

				{/* Mots-clés */}
				<div className="min-w-0">
					<label
						htmlFor="keywords"
						className="
							mb-2 block text-sm
							font-medium text-slate-700
						"
					>
						Mots-clés
					</label>

					<input
						id="keywords"
						type="text"
						value={
							keywords
						}
						onChange={
							(event) => {
								setKeywords(
									event.target.value,
								)
							}
						}
						placeholder={
							'Machine Learning Engineer'
						}
						className="
							h-11 w-full
							min-w-0 rounded-xl
							border border-slate-300
							bg-white px-3
							text-base text-slate-900
							outline-none transition
							placeholder:text-slate-400
							focus:border-blue-500
							focus:ring-2
							focus:ring-blue-100
						"
					/>
				</div>

				{/* Localisation */}
				<div className="min-w-0">
					<LocationAutocomplete
						value={
							location
						}
						onChange={
							setLocation
						}
					/>
				</div>

				{/* Nombre d'offres */}
				<div className="min-w-0">
					<label
						htmlFor="limit"
						className="
							mb-2 block text-sm
							font-medium text-slate-700
						"
					>
						Nombre d'offres
					</label>

					<select
						id="limit"
						value={
							limit
						}
						onChange={
							(event) => {
								setLimit(
									Number(
										event.target.value,
									),
								)
							}
						}
						className="
							h-11 w-full
							rounded-xl border
							border-slate-300
							bg-white px-3
							text-base text-slate-900
							outline-none transition
							focus:border-blue-500
							focus:ring-2
							focus:ring-blue-100
						"
					>
						<option value={5}>
							5
						</option>

						<option value={10}>
							10
						</option>

						<option value={20}>
							20
						</option>
					</select>
				</div>

				{/* Bouton */}
				<div
					className="
						md:col-span-2
						xl:col-span-1
					"
				>
					<button
						type="submit"
						disabled={
							isLoading
							|| !file
							|| !keywords.trim()
						}
						className="
							flex h-11 w-full
							items-center justify-center
							gap-2 rounded-xl
							bg-blue-600 px-5
							text-sm font-semibold
							text-white shadow-sm
							transition
							hover:bg-blue-700
							focus:outline-none
							focus:ring-2
							focus:ring-blue-300
							disabled:cursor-not-allowed
							disabled:bg-slate-300
							disabled:shadow-none
							xl:w-auto
							xl:whitespace-nowrap
						"
					>
						{isLoading ? (
							<>
								<span
									className="
										h-4 w-4
										animate-spin
										rounded-full
										border-2
										border-white/40
										border-t-white
									"
								/>

								Analyse...
							</>
						) : (
							<>
								<span
									aria-hidden="true"
								>
									⌕
								</span>

								Analyser les offres
							</>
						)}
					</button>
				</div>
			</div>
		</form>
	)
}
