import type {
	CV,
	Experience,
	Education,
} from '../../types/cv'


interface CVProfileProps {
	cv: CV | null
	isLoading?: boolean
	error?: string | null
	onUpload?: (
		file: File,
	) => void
}


function Tag({
				 children,
			 }: {
	children: string
}) {
	return (
		<span
			className="
				inline-flex max-w-full
				rounded-lg border
				border-blue-100
				bg-blue-50
				px-2.5 py-1.5
				text-xs font-medium
				text-blue-700
				sm:px-3
				sm:text-sm
			"
		>
			<span className="truncate">
				{children}
			</span>
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
				mb-4 text-base
				font-bold text-slate-900
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
		<div
			className="
				relative border-l-2
				border-slate-200
				pb-7 pl-5
				last:pb-0
				sm:pb-8
				sm:pl-6
			"
		>
			<div
				className="
					absolute -left-[7px]
					top-1 h-3 w-3
					rounded-full
					border-2
					border-blue-600
					bg-white
				"
			/>

			<div
				className="
					flex flex-col gap-2
					sm:flex-row
					sm:items-start
					sm:justify-between
				"
			>
				<div className="min-w-0">
					<h4
						className="
							font-bold
							text-slate-900
						"
					>
						{experience.role
							?? 'Poste non précisé'}
					</h4>

					{experience.company && (
						<p
							className="
								mt-1 text-sm
								font-medium
								text-blue-600
							"
						>
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
							self-start
							shrink-0
							rounded-lg
							bg-slate-100
							px-3 py-1
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
						(
							item,
							index,
						) => (
							<li
								key={
									`${item}-${index}`
								}
								className="
									flex gap-2
									text-sm leading-6
									text-slate-600
								"
							>
								<span
									className="
										shrink-0
										text-slate-400
									"
								>
									•
								</span>

								<span className="min-w-0">
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
				rounded-xl border
				border-slate-200
				bg-slate-50
				p-4
			"
		>
			<div
				className="
					flex flex-col gap-2
					sm:flex-row
					sm:justify-between
				"
			>
				<div className="min-w-0">
					<h4
						className="
							font-bold
							text-slate-900
						"
					>
						{education.degree
							?? 'Formation'}
					</h4>

					{education.institution && (
						<p
							className="
								mt-1 text-sm
								text-slate-600
							"
						>
							{education.institution}
						</p>
					)}
				</div>

				{education.year && (
					<span
						className="
							shrink-0
							text-sm
							font-medium
							text-slate-500
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
							inline-flex
							max-w-full
							rounded-lg
							bg-indigo-50
							px-2.5 py-1
							text-xs
							font-semibold
							text-indigo-700
						"
					>
						<span className="truncate">
							{education.level}
						</span>
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
			onUpload(
				file,
			)
		}

		event.target.value = ''
	}


	if (isLoading) {
		return (
			<div
				className="
					flex min-h-[320px]
					flex-col items-center
					justify-center
					rounded-2xl border
					border-slate-200
					bg-white p-6
					text-center
					shadow-sm
					sm:min-h-[400px]
					sm:p-8
				"
			>
				<div
					className="
						h-10 w-10
						animate-spin
						rounded-full
						border-4
						border-blue-100
						border-t-blue-600
					"
				/>

				<h3
					className="
						mt-5 font-bold
						text-slate-900
					"
				>
					Analyse du CV
				</h3>

				<p
					className="
						mt-2 text-sm
						text-slate-500
					"
				>
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
					border-slate-200
					bg-white p-5
					shadow-sm
					sm:p-8
				"
			>
				<div
					className="
						mx-auto flex
						max-w-lg flex-col
						items-center
						py-8 text-center
						sm:py-12
					"
				>
					<div
						className="
							flex h-14 w-14
							items-center
							justify-center
							rounded-2xl
							bg-blue-50
							text-xl
							text-blue-600
							sm:h-16
							sm:w-16
							sm:text-2xl
						"
					>
						▤
					</div>

					<h3
						className="
							mt-5 text-lg
							font-bold
							text-slate-900
						"
					>
						Analysez votre CV
					</h3>

					<p
						className="
							mt-2 max-w-md
							text-sm leading-6
							text-slate-500
						"
					>
						Importez votre CV pour consulter
						les informations détectées par
						ATS CV Scorer.
					</p>

					{onUpload && (
						<label
							className="
								mt-6 w-full
								cursor-pointer
								rounded-xl
								bg-blue-600
								px-5 py-2.5
								text-sm
								font-semibold
								text-white
								transition
								hover:bg-blue-700
								sm:w-auto
							"
						>
							Importer mon CV

							<input
								type="file"
								accept="
									application/pdf,.pdf
								"
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
		<div className="space-y-4 sm:space-y-6">
			{/* Identité */}
			<section
				className="
					rounded-2xl border
					border-slate-200
					bg-white p-4
					shadow-sm
					sm:p-6
				"
			>
				<div
					className="
						flex flex-col
						gap-5
						sm:flex-row
						sm:items-center
						sm:gap-6
					"
				>
					<div
						className="
							flex h-16 w-16
							shrink-0
							items-center
							justify-center
							rounded-2xl
							bg-gradient-to-br
							from-blue-500
							to-indigo-600
							text-xl font-bold
							text-white
							shadow-sm
							sm:h-20
							sm:w-20
							sm:text-2xl
						"
					>
						{initial}
					</div>

					<div
						className="
							min-w-0
							flex-1
						"
					>
						<h2
							className="
								break-words
								text-xl font-bold
								text-slate-900
								sm:text-2xl
							"
						>
							{candidateName}
						</h2>

						{cv.title && (
							<p
								className="
									mt-1
									font-semibold
									text-blue-600
								"
							>
								{cv.title}
							</p>
						)}

						<div
							className="
								mt-3 flex
								flex-col
								gap-2
								text-sm
								text-slate-500
								sm:flex-row
								sm:flex-wrap
								sm:gap-x-5
							"
						>
							{cv.contact.location && (
								<span className="break-words">
									📍 {cv.contact.location}
								</span>
							)}

							{cv.contact.email && (
								<span className="break-all">
									✉ {cv.contact.email}
								</span>
							)}

							{cv.contact.phone && (
								<span className="break-words">
									☎ {cv.contact.phone}
								</span>
							)}

							{cv.contact.website && (
								<span className="break-all">
									⌘ {cv.contact.website}
								</span>
							)}
						</div>
					</div>

					{onUpload && (
						<label
							className="
								w-full
								cursor-pointer
								rounded-xl
								border
								border-slate-300
								bg-white px-4
								py-2.5
								text-center
								text-sm
								font-semibold
								text-slate-700
								transition
								hover:bg-slate-50
								sm:w-auto
							"
						>
							Changer de CV

							<input
								type="file"
								accept="
									application/pdf,.pdf
								"
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
						border-red-200
						bg-red-50 p-4
						text-sm
						text-red-700
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
						border-slate-200
						bg-white p-4
						shadow-sm
						sm:p-6
					"
				>
					<SectionTitle>
						Profil
					</SectionTitle>

					<p
						className="
							text-sm
							leading-7
							text-slate-600
						"
					>
						{cv.profile}
					</p>
				</section>
			)}

			{/* Compétences + outils */}
			<div
				className="
					grid gap-4
					sm:gap-6
					xl:grid-cols-2
				"
			>
				<section
					className="
						min-w-0
						rounded-2xl
						border
						border-slate-200
						bg-white p-4
						shadow-sm
						sm:p-6
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
						min-w-0
						rounded-2xl
						border
						border-slate-200
						bg-white p-4
						shadow-sm
						sm:p-6
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
					grid gap-4
					sm:gap-6
					xl:grid-cols-2
				"
			>
				<section
					className="
						min-w-0
						rounded-2xl
						border
						border-slate-200
						bg-white p-4
						shadow-sm
						sm:p-6
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
						min-w-0
						rounded-2xl
						border
						border-slate-200
						bg-white p-4
						shadow-sm
						sm:p-6
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
					border-slate-200
					bg-white p-4
					shadow-sm
					sm:p-6
				"
			>
				<SectionTitle>
					Expériences professionnelles
				</SectionTitle>

				{cv.experiences.length > 0 ? (
					<div className="mt-2">
						{cv.experiences.map(
							(
								experience,
								index,
							) => (
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
					border-slate-200
					bg-white p-4
					shadow-sm
					sm:p-6
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
							(
								education,
								index,
							) => (
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
