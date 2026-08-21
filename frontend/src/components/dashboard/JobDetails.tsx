import {
	useState,
} from 'react'

import type {
	RankedJob,
} from '../../types/ranking'

import MatchScore from './MatchScore'
import ScoreBar from './ScoreBar'


type TabKey =
	| 'summary'
	| 'skills'
	| 'tools'
	| 'experience'
	| 'education'
	| 'languages'
	| 'details'


interface JobDetailsProps {
	rankedJob: RankedJob
}


const tabs: {
	key: TabKey
	label: string
}[] = [
	{
		key: 'summary',
		label: 'Résumé',
	},
	{
		key: 'skills',
		label: 'Compétences',
	},
	{
		key: 'tools',
		label: 'Outils',
	},
	{
		key: 'experience',
		label: 'Expérience',
	},
	{
		key: 'education',
		label: 'Formation',
	},
	{
		key: 'languages',
		label: 'Langues',
	},
	{
		key: 'details',
		label: "Détails de l'offre",
	},
]


function EmptyState({
						message,
					}: {
	message: string
}) {
	return (
		<div
			className="
				rounded-xl border border-dashed
				border-slate-300 bg-slate-50
				p-6 text-center sm:p-8
			"
		>
			<p className="text-sm text-slate-500">
				{message}
			</p>
		</div>
	)
}


function Tag({
				 value,
				 variant,
			 }: {
	value: string
	variant:
		| 'success'
		| 'danger'
		| 'neutral'
}) {
	const styles = {
		success:
			'border-emerald-200 bg-emerald-50 text-emerald-700',
		danger:
			'border-red-200 bg-red-50 text-red-700',
		neutral:
			'border-slate-200 bg-slate-50 text-slate-700',
	}

	return (
		<span
			className={`
				inline-flex max-w-full items-center
				rounded-lg border px-2.5 py-1.5
				text-xs font-medium sm:px-3 sm:text-sm
				${styles[variant]}
			`}
		>
			{variant === 'success' && (
				<span className="mr-1.5">
					✓
				</span>
			)}

			{variant === 'danger' && (
				<span className="mr-1.5">
					×
				</span>
			)}

			<span className="truncate">
				{value}
			</span>
		</span>
	)
}


export default function JobDetails({
									   rankedJob,
								   }: JobDetailsProps) {
	const [
		activeTab,
		setActiveTab,
	] = useState<TabKey>(
		'summary',
	)

	const {
		job,
		match,
		explanation,
	} = rankedJob


	function renderSummary() {
		return (
			<div
				className="
					grid gap-6
					xl:grid-cols-[0.9fr_1.1fr]
				"
			>
				<div>
					<h3 className="mb-5 text-base font-bold text-slate-900">
						Scores détaillés
					</h3>

					<div className="space-y-5 sm:space-y-6">
						<ScoreBar
							label="Compétences"
							score={
								match.details.skills
							}
						/>

						<ScoreBar
							label="Outils & Technologies"
							score={
								match.details.tools
							}
						/>

						<ScoreBar
							label="Expérience"
							score={
								match.details.experience
							}
						/>

						<ScoreBar
							label="Formation"
							score={
								match.details.education
							}
						/>

						<ScoreBar
							label="Langues"
							score={
								match.details.languages
							}
						/>
					</div>

					<div
						className="
							mt-7 border-t
							border-slate-100 pt-5
							sm:mt-8 sm:pt-6
						"
					>
						<h3
							className="
								mb-3 text-sm
								font-bold text-slate-800
							"
						>
							Exigences principales
						</h3>

						<div className="space-y-2 text-sm text-slate-600">
							{job.experience_required && (
								<p>
									<span className="font-medium">
										Expérience :
									</span>{' '}
									{job.experience_required}
								</p>
							)}

							{job.education_required && (
								<p>
									<span className="font-medium">
										Formation :
									</span>{' '}
									{job.education_required}
								</p>
							)}

							{!job.experience_required
								&& !job.education_required && (
									<p className="text-slate-400">
										Aucune exigence principale détectée.
									</p>
								)}
						</div>
					</div>
				</div>

				<div className="space-y-4">
					{explanation.summary && (
						<div
							className="
								rounded-xl border
								border-slate-200
								bg-slate-50 p-4
							"
						>
							<p
								className="
									text-sm leading-6
									text-slate-700
								"
							>
								{explanation.summary}
							</p>
						</div>
					)}

					{explanation.strengths.length > 0 && (
						<div
							className="
								rounded-xl border
								border-emerald-200
								bg-emerald-50/70
								p-4 sm:p-5
							"
						>
							<h3
								className="
									mb-3 font-bold
									text-emerald-800
								"
							>
								✓ Points forts
							</h3>

							<ul className="space-y-2">
								{explanation.strengths.map(
									(strength) => (
										<li
											key={strength}
											className="
												flex gap-2
												text-sm leading-5
												text-slate-700
											"
										>
											<span>•</span>

											<span>
												{strength}
											</span>
										</li>
									),
								)}
							</ul>
						</div>
					)}

					{explanation.weaknesses.length > 0 && (
						<div
							className="
								rounded-xl border
								border-amber-200
								bg-amber-50/70
								p-4 sm:p-5
							"
						>
							<h3
								className="
									mb-3 font-bold
									text-amber-800
								"
							>
								△ Points à renforcer
							</h3>

							<ul className="space-y-2">
								{explanation.weaknesses.map(
									(weakness) => (
										<li
											key={weakness}
											className="
												flex gap-2
												text-sm leading-5
												text-slate-700
											"
										>
											<span>•</span>

											<span>
												{weakness}
											</span>
										</li>
									),
								)}
							</ul>
						</div>
					)}

					{explanation.recommendations.length > 0 && (
						<div
							className="
								rounded-xl border
								border-blue-200
								bg-blue-50/70
								p-4 sm:p-5
							"
						>
							<h3
								className="
									mb-3 font-bold
									text-blue-800
								"
							>
								☆ Recommandations
							</h3>

							<ul className="space-y-2">
								{explanation.recommendations.map(
									(recommendation) => (
										<li
											key={recommendation}
											className="
												flex gap-2
												text-sm leading-5
												text-slate-700
											"
										>
											<span>•</span>

											<span>
												{recommendation}
											</span>
										</li>
									),
								)}
							</ul>
						</div>
					)}
				</div>
			</div>
		)
	}


	function renderSkills() {
		const hasContent =
			match.matched_skills.length > 0
			|| match.missing_skills.length > 0

		if (!hasContent) {
			return (
				<EmptyState
					message="Aucune compétence spécifique n'a été détectée pour cette offre."
				/>
			)
		}

		return (
			<div className="space-y-7 sm:space-y-8">
				<div>
					<div
						className="
							mb-5 flex items-center
							justify-between gap-4
						"
					>
						<h3 className="text-base font-bold text-slate-900">
							Compétences
						</h3>

						<span className="text-sm font-semibold text-slate-600">
							{Math.round(
								match.details.skills,
							)}
							%
						</span>
					</div>

					<ScoreBar
						label="Couverture des compétences"
						score={
							match.details.skills
						}
					/>
				</div>

				<div>
					<h4
						className="
							mb-3 text-sm font-bold
							text-emerald-700
						"
					>
						Compétences présentes dans votre CV
					</h4>

					{match.matched_skills.length > 0 ? (
						<div className="flex flex-wrap gap-2">
							{match.matched_skills.map(
								(skill) => (
									<Tag
										key={skill}
										value={skill}
										variant="success"
									/>
								),
							)}
						</div>
					) : (
						<p className="text-sm text-slate-500">
							Aucune compétence demandée n'a été reconnue dans le CV.
						</p>
					)}
				</div>

				<div>
					<h4
						className="
							mb-3 text-sm font-bold
							text-red-700
						"
					>
						Compétences à renforcer
					</h4>

					{match.missing_skills.length > 0 ? (
						<div className="flex flex-wrap gap-2">
							{match.missing_skills.map(
								(skill) => (
									<Tag
										key={skill}
										value={skill}
										variant="danger"
									/>
								),
							)}
						</div>
					) : (
						<div
							className="
								rounded-xl border
								border-emerald-200
								bg-emerald-50
								p-4
							"
						>
							<p className="text-sm text-emerald-700">
								Toutes les compétences détectées dans l'offre sont couvertes.
							</p>
						</div>
					)}
				</div>
			</div>
		)
	}


	function renderTools() {
		const hasContent =
			match.matched_tools.length > 0
			|| match.missing_tools.length > 0

		if (!hasContent) {
			return (
				<EmptyState
					message="Aucun outil ou technologie spécifique n'a été détecté pour cette offre."
				/>
			)
		}

		return (
			<div className="space-y-7 sm:space-y-8">
				<div>
					<ScoreBar
						label="Couverture des outils & technologies"
						score={
							match.details.tools
						}
					/>
				</div>

				<div>
					<h4 className="mb-3 text-sm font-bold text-emerald-700">
						Outils maîtrisés
					</h4>

					{match.matched_tools.length > 0 ? (
						<div className="flex flex-wrap gap-2">
							{match.matched_tools.map(
								(tool) => (
									<Tag
										key={tool}
										value={tool}
										variant="success"
									/>
								),
							)}
						</div>
					) : (
						<p className="text-sm text-slate-500">
							Aucun outil demandé n'a été reconnu dans le CV.
						</p>
					)}
				</div>

				<div>
					<h4 className="mb-3 text-sm font-bold text-red-700">
						Outils manquants
					</h4>

					{match.missing_tools.length > 0 ? (
						<div className="flex flex-wrap gap-2">
							{match.missing_tools.map(
								(tool) => (
									<Tag
										key={tool}
										value={tool}
										variant="danger"
									/>
								),
							)}
						</div>
					) : (
						<div
							className="
								rounded-xl border
								border-emerald-200
								bg-emerald-50 p-4
							"
						>
							<p className="text-sm text-emerald-700">
								Tous les outils détectés dans l'offre sont couverts.
							</p>
						</div>
					)}
				</div>
			</div>
		)
	}


	function renderExperience() {
		return (
			<div className="space-y-6">
				<ScoreBar
					label="Compatibilité de l'expérience"
					score={
						match.details.experience
					}
				/>

				<div
					className="
						grid gap-4
						sm:grid-cols-2
					"
				>
					<div
						className="
							rounded-xl border
							border-slate-200
							bg-slate-50 p-4
							sm:p-5
						"
					>
						<p
							className="
								text-xs font-semibold
								uppercase tracking-wide
								text-slate-400
							"
						>
							Expérience demandée
						</p>

						<p
							className="
								mt-2 text-base
								font-bold
								text-slate-900
								sm:text-lg
							"
						>
							{job.experience_required
								?? 'Non précisée'}
						</p>
					</div>

					<div
						className="
							rounded-xl border
							border-slate-200
							bg-slate-50 p-4
							sm:p-5
						"
					>
						<p
							className="
								text-xs font-semibold
								uppercase tracking-wide
								text-slate-400
							"
						>
							Score expérience
						</p>

						<p
							className="
								mt-2 text-base
								font-bold
								text-slate-900
								sm:text-lg
							"
						>
							{Math.round(
								match.details.experience,
							)}
							%
						</p>
					</div>
				</div>

				<div
					className="
						rounded-xl border
						border-blue-100
						bg-blue-50 p-4
						sm:p-5
					"
				>
					<p className="text-sm leading-6 text-slate-700">
						Ce score estime la correspondance entre
						l'expérience demandée dans l'offre et
						l'expérience pertinente détectée dans votre CV.
					</p>
				</div>
			</div>
		)
	}


	function renderEducation() {
		return (
			<div className="space-y-6">
				<ScoreBar
					label="Compatibilité de la formation"
					score={
						match.details.education
					}
				/>

				<div
					className="
						grid gap-4
						sm:grid-cols-2
					"
				>
					<div
						className="
							rounded-xl border
							border-slate-200
							bg-slate-50 p-4
							sm:p-5
						"
					>
						<p
							className="
								text-xs font-semibold
								uppercase
								text-slate-400
							"
						>
							Formation demandée
						</p>

						<p
							className="
								mt-2 text-base
								font-bold
								text-slate-900
								sm:text-lg
							"
						>
							{job.education_required
								?? 'Non précisée'}
						</p>
					</div>

					<div
						className="
							rounded-xl border
							border-slate-200
							bg-slate-50 p-4
							sm:p-5
						"
					>
						<p
							className="
								text-xs font-semibold
								uppercase
								text-slate-400
							"
						>
							Score formation
						</p>

						<p
							className="
								mt-2 text-base
								font-bold
								text-slate-900
								sm:text-lg
							"
						>
							{Math.round(
								match.details.education,
							)}
							%
						</p>
					</div>
				</div>
			</div>
		)
	}


	function renderLanguages() {
		const hasContent =
			match.matched_languages.length > 0
			|| match.missing_languages.length > 0
			|| job.languages.length > 0

		if (!hasContent) {
			return (
				<EmptyState
					message="Aucune exigence linguistique n'a été détectée pour cette offre."
				/>
			)
		}

		return (
			<div className="space-y-7 sm:space-y-8">
				<ScoreBar
					label="Compatibilité linguistique"
					score={
						match.details.languages
					}
				/>

				{job.languages.length > 0 && (
					<div>
						<h4 className="mb-3 text-sm font-bold text-slate-800">
							Langues demandées
						</h4>

						<div className="flex flex-wrap gap-2">
							{job.languages.map(
								(language) => (
									<Tag
										key={language}
										value={language}
										variant="neutral"
									/>
								),
							)}
						</div>
					</div>
				)}

				<div>
					<h4 className="mb-3 text-sm font-bold text-emerald-700">
						Langues couvertes
					</h4>

					{match.matched_languages.length > 0 ? (
						<div className="flex flex-wrap gap-2">
							{match.matched_languages.map(
								(language) => (
									<Tag
										key={language}
										value={language}
										variant="success"
									/>
								),
							)}
						</div>
					) : (
						<p className="text-sm text-slate-500">
							Aucune langue demandée n'a été reconnue.
						</p>
					)}
				</div>

				{match.missing_languages.length > 0 && (
					<div>
						<h4 className="mb-3 text-sm font-bold text-red-700">
							Langues manquantes
						</h4>

						<div className="flex flex-wrap gap-2">
							{match.missing_languages.map(
								(language) => (
									<Tag
										key={language}
										value={language}
										variant="danger"
									/>
								),
							)}
						</div>
					</div>
				)}
			</div>
		)
	}


	function renderDetails() {
		return (
			<div className="space-y-6">
				<div
					className="
						grid gap-4
						sm:grid-cols-2
					"
				>
					<div className="rounded-xl bg-slate-50 p-4">
						<p
							className="
								text-xs font-semibold
								uppercase
								text-slate-400
							"
						>
							Localisation
						</p>

						<p
							className="
								mt-1 text-sm
								font-semibold
								text-slate-800
							"
						>
							{job.location
								?? 'Non précisée'}
						</p>
					</div>

					<div className="rounded-xl bg-slate-50 p-4">
						<p
							className="
								text-xs font-semibold
								uppercase
								text-slate-400
							"
						>
							Type de contrat
						</p>

						<p
							className="
								mt-1 text-sm
								font-semibold
								text-slate-800
							"
						>
							{job.contract_type
								?? 'Non précisé'}
						</p>
					</div>
				</div>

				<div>
					<h3 className="mb-3 text-base font-bold text-slate-900">
						Description de l'offre
					</h3>

					<div
						className="
							max-h-[60vh]
							overflow-y-auto
							whitespace-pre-line
							rounded-xl border
							border-slate-200
							bg-slate-50
							p-4 text-sm
							leading-7
							text-slate-700
							sm:max-h-[600px]
							sm:p-5
						"
					>
						{job.description
							|| 'Aucune description disponible.'}
					</div>
				</div>
			</div>
		)
	}


	function renderActiveTab() {
		switch (activeTab) {
			case 'skills':
				return renderSkills()

			case 'tools':
				return renderTools()

			case 'experience':
				return renderExperience()

			case 'education':
				return renderEducation()

			case 'languages':
				return renderLanguages()

			case 'details':
				return renderDetails()

			case 'summary':
			default:
				return renderSummary()
		}
	}


	return (
		<section
			className="
				overflow-hidden
				rounded-2xl border
				border-slate-200
				bg-white shadow-sm
			"
		>
			<header
				className="
					border-b
					border-slate-200
					p-4 sm:p-5 md:p-6
				"
			>
				<div
					className="
						flex flex-col gap-5
						md:flex-row
						md:items-start
						md:justify-between
					"
				>
					<div className="min-w-0 flex-1">
						<h2
							className="
								text-lg font-bold
								leading-6
								text-slate-900
								sm:text-xl
								lg:text-2xl
							"
						>
							{job.title}
						</h2>

						{job.company && (
							<p
								className="
									mt-2 text-sm
									font-semibold
									text-blue-600
									sm:text-base
								"
							>
								{job.company}
							</p>
						)}

						<div
							className="
								mt-3 flex
								flex-wrap gap-x-4
								gap-y-2
								text-xs
								text-slate-500
								sm:mt-4
								sm:text-sm
							"
						>
							{job.location && (
								<span>
									📍 {job.location}
								</span>
							)}

							{job.contract_type && (
								<span>
									▣ {job.contract_type}
								</span>
							)}
						</div>
					</div>

					<div
						className="
							flex items-center
							justify-between
							gap-4
							md:flex-col
							md:justify-start
						"
					>
						<div className="flex flex-col items-center">
							<MatchScore
								score={
									match.score
								}
								size="lg"
							/>

							<span
								className="
									mt-2 text-xs
									font-medium
									text-slate-500
								"
							>
								Compatibilité CV
							</span>
						</div>

						{job.source_url && (
							<a
								href={job.source_url}
								target="_blank"
								rel="noopener noreferrer"
								className="
									inline-flex
									min-h-10
									items-center
									justify-center
									gap-2 rounded-xl
									border
									border-blue-200
									bg-blue-50
									px-3 py-2
									text-xs
									font-semibold
									text-blue-700
									transition
									hover:border-blue-300
									hover:bg-blue-100
									sm:px-4
									sm:text-sm
									md:w-full
								"
							>
								<span>
									Voir l'offre
								</span>

								<span
									className="
										hidden sm:inline
									"
								>
									originale
								</span>

								<span aria-hidden="true">
									↗
								</span>
							</a>
						)}
					</div>
				</div>
			</header>

			<div
				className="
					border-b
					border-slate-200
					bg-white
				"
			>
				<nav
					className="
						flex gap-1
						overflow-x-auto
						px-3
						scroll-smooth
						sm:px-5
					"
				>
					{tabs.map(
						(tab) => (
							<button
								key={tab.key}
								type="button"
								onClick={() => {
									setActiveTab(
										tab.key,
									)
								}}
								className={`
									shrink-0
									whitespace-nowrap
									border-b-2
									px-3 py-3
									text-xs
									font-medium
									transition
									sm:py-4
									sm:text-sm
									${
									activeTab
									=== tab.key
										? 'border-blue-600 text-blue-600'
										: 'border-transparent text-slate-500 hover:text-slate-800'
								}
								`}
							>
								{tab.label}
							</button>
						),
					)}
				</nav>
			</div>

			<div
				className="
					p-4
					sm:p-5
					md:p-6
				"
			>
				{renderActiveTab()}
			</div>
		</section>
	)
}
