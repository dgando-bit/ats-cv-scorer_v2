import type {
	RankedJob,
} from '../../types/ranking'

import MatchScore from './MatchScore'
import ScoreBar from './ScoreBar'


interface JobDetailsProps {
	rankedJob: RankedJob
}

export default function JobDetails({
									   rankedJob,
								   }: JobDetailsProps) {
	const {
		job,
		match,
		explanation,
	} = rankedJob

	return (
		<section
			className="
				overflow-hidden rounded-2xl border border-slate-200
				bg-white shadow-sm
			"
		>
			<header
				className="
					flex flex-col gap-5 border-b border-slate-200
					p-6 md:flex-row md:items-start
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
					flex gap-1 overflow-x-auto border-b border-slate-200
					px-5
				"
			>
				{[
					'Résumé',
					'Compétences',
					'Outils',
					'Expérience',
					'Formation',
					'Langues',
					"Détails de l'offre",
				].map((tab, index) => (
					<button
						key={tab}
						type="button"
						className={`
							whitespace-nowrap border-b-2 px-3 py-4
							text-sm font-medium transition
							${
							index === 0
								? 'border-blue-600 text-blue-600'
								: 'border-transparent text-slate-500 hover:text-slate-800'
						}
						`}
					>
						{tab}
					</button>
				))}
			</nav>

			<div className="grid gap-6 p-6 xl:grid-cols-[0.9fr_1.1fr]">
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
		</section>
	)
}
