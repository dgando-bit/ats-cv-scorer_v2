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
				p-8 text-center
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
	variant: 'success' | 'danger' | 'neutral'
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
				inline-flex items-center rounded-lg
				border px-3 py-1.5 text-sm font-medium
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

			{value}
		</span>
	)
}


export default function JobDetails({
									   rankedJob,
								   }: JobDetailsProps) {
	const [
		activeTab,
		setActiveTab,
	] = useState<TabKey>('summary')

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

					<div className="space-y-6">
						<ScoreBar
							label="Compétences"
							score={match.details.skills}
						/>

						<ScoreBar
							label="Outils & Technologies"
							score={match.details.tools}
						/>

						<ScoreBar
							label="Expérience"
							score={match.details.experience}
						/>

						<ScoreBar
							label="Formation"
							score={match.details.education}
						/>

						<ScoreBar
							label="Langues"
							score={match.details.languages}
						/>
					</div>

					<div className="mt-8 border-t border-slate-100 pt-6">
						<h3 className="mb-3 text-sm font-bold text-slate-800">
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
						<div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
							<p className="text-sm leading-6 text-slate-700">
								{explanation.summary}
							</p>
						</div>
					)}

					{explanation.strengths.length > 0 && (
						<div
							className="
								rounded-xl border border-emerald-200
								bg-emerald-50/70 p-5
							"
						>
							<h3 className="mb-3 font-bold text-emerald-800">
								✓ Points forts
							</h3>

							<ul className="space-y-2">
								{explanation.strengths.map(
									(strength) => (
										<li
											key={strength}
											className="
												flex gap-2 text-sm
												leading-5 text-slate-700
											"
										>
											<span>•</span>
											<span>{strength}</span>
										</li>
									),
								)}
							</ul>
						</div>
					)}

					{explanation.weaknesses.length > 0 && (
						<div
							className="
								rounded-xl border border-amber-200
								bg-amber-50/70 p-5
							"
						>
							<h3 className="mb-3 font-bold text-amber-800">
								△ Points à renforcer
							</h3>

							<ul className="space-y-2">
								{explanation.weaknesses.map(
									(weakness) => (
										<li
											key={weakness}
											className="
												flex gap-2 text-sm
												leading-5 text-slate-700
											"
										>
											<span>•</span>
											<span>{weakness}</span>
										</li>
									),
								)}
							</ul>
						</div>
					)}

					{explanation.recommendations.length > 0 && (
						<div
							className="
								rounded-xl border border-blue-200
								bg-blue-50/70 p-5
							"
						>
							<h3 className="mb-3 font-bold text-blue-800">
								☆ Recommandations
							</h3>

							<ul className="space-y-2">
								{explanation.recommendations.map(
									(recommendation) => (
										<li
											key={recommendation}
											className="
												flex gap-2 text-sm
												leading-5 text-slate-700
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
			<div className="space-y-8">
				<div>
					<div className="mb-5 flex items-center justify-between gap-4">
						<h3 className="text-base font-bold text-slate-900">
							Compétences
						</h3>

						<span className="text-sm font-semibold text-slate-600">
							{Math.round(match.details.skills)}%
						</span>
					</div>

					<ScoreBar
						label="Couverture des compétences"
						score={match.details.skills}
					/>
				</div>

				<div>
					<h4 className="mb-3 text-sm font-bold text-emerald-700">
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
					<h4 className="mb-3 text-sm font-bold text-red-700">
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
								rounded-xl border border-emerald-200
								bg-emerald-50 p-4
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
			<div className="space-y-8">
				<div>
					<ScoreBar
						label="Couverture des outils & technologies"
						score={match.details.tools}
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
								rounded-xl border border-emerald-200
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
				<div>
					<ScoreBar
						label="Compatibilité de l'expérience"
						score={match.details.experience}
					/>
				</div>

				<div
					className="
						grid gap-4 md:grid-cols-2
					"
				>
					<div
						className="
							rounded-xl border border-slate-200
							bg-slate-50 p-5
						"
					>
						<p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
							Expérience demandée
						</p>

						<p className="mt-2 text-lg font-bold text-slate-900">
							{job.experience_required
								?? 'Non précisée'}
						</p>
					</div>

					<div
						className="
							rounded-xl border border-slate-200
							bg-slate-50 p-5
						"
					>
						<p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
							Score expérience
						</p>

						<p className="mt-2 text-lg font-bold text-slate-900">
							{Math.round(
								match.details.experience,
							)}
							%
						</p>
					</div>
				</div>

				<div
					className="
						rounded-xl border border-blue-100
						bg-blue-50 p-5
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
					score={match.details.education}
				/>

				<div
					className="
						grid gap-4 md:grid-cols-2
					"
				>
					<div
						className="
							rounded-xl border border-slate-200
							bg-slate-50 p-5
						"
					>
						<p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
							Formation demandée
						</p>

						<p className="mt-2 text-lg font-bold text-slate-900">
							{job.education_required
								?? 'Non précisée'}
						</p>
					</div>

					<div
						className="
							rounded-xl border border-slate-200
							bg-slate-50 p-5
						"
					>
						<p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
							Score formation
						</p>

						<p className="mt-2 text-lg font-bold text-slate-900">
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
			<div className="space-y-8">
				<ScoreBar
					label="Compatibilité linguistique"
					score={match.details.languages}
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
						grid gap-4 sm:grid-cols-2
					"
				>
					<div className="rounded-xl bg-slate-50 p-4">
						<p className="text-xs font-semibold uppercase text-slate-400">
							Localisation
						</p>

						<p className="mt-1 text-sm font-semibold text-slate-800">
							{job.location
								?? 'Non précisée'}
						</p>
					</div>

					<div className="rounded-xl bg-slate-50 p-4">
						<p className="text-xs font-semibold uppercase text-slate-400">
							Type de contrat
						</p>

						<p className="mt-1 text-sm font-semibold text-slate-800">
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
							max-h-[600px] overflow-y-auto
							whitespace-pre-line rounded-xl
							border border-slate-200 bg-slate-50
							p-5 text-sm leading-7 text-slate-700
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
				overflow-hidden rounded-2xl border
				border-slate-200 bg-white shadow-sm
			"
		>
			<header
				className="
					flex flex-col gap-5
					border-b border-slate-200 p-6
					md:flex-row md:items-start
					md:justify-between
				"
			>
				<div className="min-w-0">
					<h2 className="text-xl font-bold text-slate-900 lg:text-2xl">
						{job.title}
					</h2>

					{job.company && (
						<p className="mt-2 font-semibold text-blue-600">
							{job.company}
						</p>
					)}

					<div className="mt-4 flex flex-wrap gap-4 text-sm text-slate-500">
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

				<div className="flex flex-col items-center">
					<MatchScore
						score={match.score}
						size="lg"
					/>

					<span className="mt-2 text-xs font-medium text-slate-500">
						Compatibilité CV
					</span>
				</div>
			</header>

			<nav
				className="
					flex gap-1 overflow-x-auto
					border-b border-slate-200 px-5
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
								whitespace-nowrap border-b-2
								px-3 py-4 text-sm font-medium
								transition
								${
								activeTab === tab.key
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

			<div className="p-6">
				{renderActiveTab()}
			</div>
		</section>
	)
}
