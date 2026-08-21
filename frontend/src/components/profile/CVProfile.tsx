import type {
	CV,
	Experience,
	Education,
} from '../../types/cv'


interface CVProfileProps {
	cv: CV | null
	isLoading?: boolean
	error?: string | null
	onUpload?: (file: File) => void
}


function Tag({
				 children,
			 }: {
	children: string
}) {
	return (
		<span
			className="
				inline-flex rounded-lg border border-blue-100
				bg-blue-50 px-3 py-1.5 text-sm
				font-medium text-blue-700
			"
		>
			{children}
		</span>
	)
}


function SectionTitle({
						  children,
					  }: {
	children: string
}) {
	return (
		<h3
			className="
				mb-4 text-base font-bold
				text-slate-900
			"
		>
			{children}
		</h3>
	)
}


function ExperienceItem({
							experience,
						}: {
	experience: Experience
}) {
	return (
		<div className="relative border-l-2 border-slate-200 pb-8 pl-6 last:pb-0">
			<div
				className="
					absolute -left-[7px] top-1
					h-3 w-3 rounded-full
					border-2 border-blue-600 bg-white
				"
			/>

			<div
				className="
					flex flex-col gap-2
					sm:flex-row sm:items-start
					sm:justify-between
				"
			>
				<div>
					<h4 className="font-bold text-slate-900">
						{experience.role
							?? 'Poste non précisé'}
					</h4>

					{experience.company && (
						<p className="mt-1 text-sm font-medium text-blue-600">
							{experience.company}
						</p>
					)}
				</div>

				{(
					experience.start_date
					|| experience.end_date
				) && (
					<span
						className="
							shrink-0 rounded-lg
							bg-slate-100 px-3 py-1
							text-xs font-medium
							text-slate-600
						"
					>
						{experience.start_date
							?? '?'}

						{' — '}

						{experience.end_date
							?? 'Aujourd’hui'}
					</span>
				)}
			</div>

			{experience.description.length > 0 && (
				<ul className="mt-4 space-y-2">
					{experience.description.map(
						(item, index) => (
							<li
								key={`${item}-${index}`}
								className="
									flex gap-2 text-sm
									leading-6 text-slate-600
								"
							>
								<span className="text-slate-400">
									•
								</span>

								<span>
									{item}
								</span>
							</li>
						),
					)}
				</ul>
			)}
		</div>
	)
}


function EducationItem({
						   education,
					   }: {
	education: Education
}) {
	return (
		<div
			className="
				rounded-xl border border-slate-200
				bg-slate-50 p-4
			"
		>
			<div
				className="
					flex flex-col gap-2
					sm:flex-row sm:justify-between
				"
			>
				<div>
					<h4 className="font-bold text-slate-900">
						{education.degree
							?? 'Formation'}
					</h4>

					{education.institution && (
						<p className="mt-1 text-sm text-slate-600">
							{education.institution}
						</p>
					)}
				</div>

				{education.year && (
					<span
						className="
							shrink-0 text-sm
							font-medium text-slate-500
						"
					>
						{education.year}
					</span>
				)}
			</div>

			{education.level && (
				<div className="mt-3">
					<span
						className="
							inline-flex rounded-lg
							bg-indigo-50 px-2.5 py-1
							text-xs font-semibold
							text-indigo-700
						"
					>
						{education.level}
					</span>
				</div>
			)}
		</div>
	)
}


export default function CVProfile({
									  cv,
									  isLoading = false,
									  error = null,
									  onUpload,
								  }: CVProfileProps) {
	function handleFileChange(
		event: React.ChangeEvent<HTMLInputElement>,
	) {
		const file =
			event.target.files?.[0]

		if (
			file
			&& onUpload
		) {
			onUpload(file)
		}

		event.target.value = ''
	}

	if (isLoading) {
		return (
			<div
				className="
					flex min-h-[400px] flex-col
					items-center justify-center
					rounded-2xl border
					border-slate-200 bg-white
					p-8 shadow-sm
				"
			>
				<div
					className="
						h-10 w-10 animate-spin
						rounded-full border-4
						border-blue-100
						border-t-blue-600
					"
				/>

				<h3 className="mt-5 font-bold text-slate-900">
					Analyse du CV
				</h3>

				<p className="mt-2 text-sm text-slate-500">
					Extraction des informations en cours...
				</p>
			</div>
		)
	}

	if (!cv) {
		return (
			<div
				className="
					rounded-2xl border
					border-slate-200 bg-white
					p-8 shadow-sm
				"
			>
				<div
					className="
						mx-auto flex max-w-lg
						flex-col items-center
						py-12 text-center
					"
				>
					<div
						className="
							flex h-16 w-16
							items-center justify-center
							rounded-2xl bg-blue-50
							text-2xl text-blue-600
						"
					>
						▤
					</div>

					<h3
						className="
							mt-5 text-lg font-bold
							text-slate-900
						"
					>
						Analysez votre CV
					</h3>

					<p
						className="
							mt-2 max-w-md text-sm
							leading-6 text-slate-500
						"
					>
						Importez votre CV pour consulter
						les informations détectées par
						ATS CV Scorer.
					</p>

					{onUpload && (
						<label
							className="
								mt-6 cursor-pointer
								rounded-xl bg-blue-600
								px-5 py-2.5 text-sm
								font-semibold text-white
								transition hover:bg-blue-700
							"
						>
							Importer mon CV

							<input
								type="file"
								accept="application/pdf"
								onChange={
									handleFileChange
								}
								className="hidden"
							/>
						</label>
					)}

					{error && (
						<p
							className="
								mt-4 text-sm
								text-red-600
							"
						>
							{error}
						</p>
					)}
				</div>
			</div>
		)
	}

	const candidateName =
		cv.candidate_name
		?? 'Candidat'

	const initial =
		candidateName
			.trim()
			.charAt(0)
			.toUpperCase()
		|| 'C'

	return (
		<div className="space-y-6">
			{/* Identité */}
			<section
				className="
					rounded-2xl border
					border-slate-200 bg-white
					p-6 shadow-sm
				"
			>
				<div
					className="
						flex flex-col gap-6
						sm:flex-row sm:items-center
					"
				>
					<div
						className="
							flex h-20 w-20 shrink-0
							items-center justify-center
							rounded-2xl bg-gradient-to-br
							from-blue-500 to-indigo-600
							text-2xl font-bold text-white
							shadow-sm
						"
					>
						{initial}
					</div>

					<div className="min-w-0 flex-1">
						<h2
							className="
								text-2xl font-bold
								text-slate-900
							"
						>
							{candidateName}
						</h2>

						{cv.title && (
							<p
								className="
									mt-1 font-semibold
									text-blue-600
								"
							>
								{cv.title}
							</p>
						)}

						<div
							className="
								mt-3 flex flex-wrap
								gap-x-5 gap-y-2
								text-sm text-slate-500
							"
						>
							{cv.contact.location && (
								<span>
									📍 {cv.contact.location}
								</span>
							)}

							{cv.contact.email && (
								<span>
									✉ {cv.contact.email}
								</span>
							)}

							{cv.contact.phone && (
								<span>
									☎ {cv.contact.phone}
								</span>
							)}

							{cv.contact.website && (
								<span>
									⌘ {cv.contact.website}
								</span>
							)}
						</div>
					</div>

					{onUpload && (
						<label
							className="
								cursor-pointer rounded-xl
								border border-slate-300
								bg-white px-4 py-2.5
								text-sm font-semibold
								text-slate-700 transition
								hover:bg-slate-50
							"
						>
							Changer de CV

							<input
								type="file"
								accept="application/pdf"
								onChange={
									handleFileChange
								}
								className="hidden"
							/>
						</label>
					)}
				</div>
			</section>

			{error && (
				<div
					className="
						rounded-xl border
						border-red-200 bg-red-50
						p-4 text-sm text-red-700
					"
				>
					{error}
				</div>
			)}

			{/* Profil */}
			{cv.profile && (
				<section
					className="
						rounded-2xl border
						border-slate-200 bg-white
						p-6 shadow-sm
					"
				>
					<SectionTitle>
						Profil
					</SectionTitle>

					<p
						className="
							text-sm leading-7
							text-slate-600
						"
					>
						{cv.profile}
					</p>
				</section>
			)}

			{/* Compétences */}
			<div
				className="
					grid gap-6
					xl:grid-cols-2
				"
			>
				<section
					className="
						rounded-2xl border
						border-slate-200 bg-white
						p-6 shadow-sm
					"
				>
					<SectionTitle>
						Compétences
					</SectionTitle>

					{cv.skills.length > 0 ? (
						<div className="flex flex-wrap gap-2">
							{cv.skills.map(
								(skill) => (
									<Tag key={skill}>
										{skill}
									</Tag>
								),
							)}
						</div>
					) : (
						<p className="text-sm text-slate-400">
							Aucune compétence détectée.
						</p>
					)}
				</section>

				<section
					className="
						rounded-2xl border
						border-slate-200 bg-white
						p-6 shadow-sm
					"
				>
					<SectionTitle>
						Outils & Technologies
					</SectionTitle>

					{cv.tools.length > 0 ? (
						<div className="flex flex-wrap gap-2">
							{cv.tools.map(
								(tool) => (
									<Tag key={tool}>
										{tool}
									</Tag>
								),
							)}
						</div>
					) : (
						<p className="text-sm text-slate-400">
							Aucun outil détecté.
						</p>
					)}
				</section>
			</div>

			{/* Soft skills + langues */}
			<div
				className="
					grid gap-6
					xl:grid-cols-2
				"
			>
				<section
					className="
						rounded-2xl border
						border-slate-200 bg-white
						p-6 shadow-sm
					"
				>
					<SectionTitle>
						Soft skills
					</SectionTitle>

					{cv.soft_skills.length > 0 ? (
						<div className="flex flex-wrap gap-2">
							{cv.soft_skills.map(
								(skill) => (
									<Tag key={skill}>
										{skill}
									</Tag>
								),
							)}
						</div>
					) : (
						<p className="text-sm text-slate-400">
							Aucun soft skill détecté.
						</p>
					)}
				</section>

				<section
					className="
						rounded-2xl border
						border-slate-200 bg-white
						p-6 shadow-sm
					"
				>
					<SectionTitle>
						Langues
					</SectionTitle>

					{cv.languages.length > 0 ? (
						<div className="flex flex-wrap gap-2">
							{cv.languages.map(
								(language) => (
									<Tag key={language}>
										{language}
									</Tag>
								),
							)}
						</div>
					) : (
						<p className="text-sm text-slate-400">
							Aucune langue détectée.
						</p>
					)}
				</section>
			</div>

			{/* Expériences */}
			<section
				className="
					rounded-2xl border
					border-slate-200 bg-white
					p-6 shadow-sm
				"
			>
				<SectionTitle>
					Expériences professionnelles
				</SectionTitle>

				{cv.experiences.length > 0 ? (
					<div className="mt-2">
						{cv.experiences.map(
							(experience, index) => (
								<ExperienceItem
									key={
										`${experience.company}-${experience.role}-${index}`
									}
									experience={
										experience
									}
								/>
							),
						)}
					</div>
				) : (
					<p className="text-sm text-slate-400">
						Aucune expérience détectée.
					</p>
				)}
			</section>

			{/* Formation */}
			<section
				className="
					rounded-2xl border
					border-slate-200 bg-white
					p-6 shadow-sm
				"
			>
				<SectionTitle>
					Formation
				</SectionTitle>

				{cv.education.length > 0 ? (
					<div
						className="
							grid gap-4
							lg:grid-cols-2
						"
					>
						{cv.education.map(
							(education, index) => (
								<EducationItem
									key={
										`${education.institution}-${education.degree}-${index}`
									}
									education={
										education
									}
								/>
							),
						)}
					</div>
				) : (
					<p className="text-sm text-slate-400">
						Aucune formation détectée.
					</p>
				)}
			</section>
		</div>
	)
}
