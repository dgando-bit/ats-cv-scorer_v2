import type {
	RankedJob,
} from '../../types/ranking'

import MatchScore from './MatchScore'


interface JobCardProps {
	rankedJob: RankedJob
	selected: boolean
	onSelect: () => void
}


export default function JobCard({
									rankedJob,
									selected,
									onSelect,
								}: JobCardProps) {
	const {
		job,
		match,
	} = rankedJob

	const allTags = [
		...job.skills,
		...job.tools,
	]

	const visibleTags =
		allTags.slice(
			0,
			4,
		)

	const remaining =
		Math.max(
			allTags.length
			- visibleTags.length,
			0,
		)

	return (
		<button
			type="button"
			onClick={
				onSelect
			}
			className={`
				w-full rounded-2xl border
				bg-white p-4 text-left
				shadow-sm transition-all
				duration-200

				sm:p-5

				hover:border-blue-300
				hover:shadow-md

				${
				selected
					? 'border-blue-500 ring-2 ring-blue-100'
					: 'border-slate-200'
			}
			`}
		>
			<div
				className="
					flex items-start gap-3
					sm:gap-4
				"
			>
				<div className="shrink-0">
					<MatchScore
						score={
							match.score
						}
					/>
				</div>

				<div className="min-w-0 flex-1">
					<div
						className="
							flex items-start
							justify-between gap-3
						"
					>
						<div className="min-w-0">
							<h3
								className="
									line-clamp-2
									text-sm font-bold
									leading-5
									text-slate-900

									sm:text-base
								"
							>
								{job.title}
							</h3>

							{job.company && (
								<p
									className="
										mt-1 truncate
										text-xs font-semibold
										text-blue-600

										sm:text-sm
									"
								>
									{job.company}
								</p>
							)}
						</div>

						<span
							className="
								mt-1 shrink-0
								text-xl font-light
								text-slate-400
							"
							aria-hidden="true"
						>
							›
						</span>
					</div>

					<div
						className="
							mt-2 flex flex-wrap
							gap-x-3 gap-y-1.5
							text-[11px]
							text-slate-500

							sm:mt-3
							sm:text-xs
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

					{visibleTags.length > 0 && (
						<div
							className="
								mt-3 flex
								flex-wrap gap-1.5

								sm:mt-4
								sm:gap-2
							"
						>
							{visibleTags.map(
								(tag) => (
									<span
										key={
											tag
										}
										className="
											max-w-full
											truncate rounded-lg
											border border-slate-200
											bg-slate-50
											px-2 py-1
											text-[10px]
											text-slate-600

											sm:px-2.5
											sm:text-xs
										"
									>
										{tag}
									</span>
								),
							)}

							{remaining > 0 && (
								<span
									className="
										rounded-lg
										border border-slate-200
										bg-slate-50
										px-2 py-1
										text-[10px]
										font-medium
										text-slate-500

										sm:px-2.5
										sm:text-xs
									"
								>
									+{remaining}
								</span>
							)}
						</div>
					)}
				</div>
			</div>
		</button>
	)
}
