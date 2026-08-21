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

	const visibleTags = allTags.slice(0, 4)

	const remaining = Math.max(
		allTags.length - visibleTags.length,
		0,
	)

	return (
		<button
			type="button"
			onClick={onSelect}
			className={`
				w-full rounded-2xl border bg-white p-5 text-left
				shadow-sm transition-all duration-200
				hover:-translate-y-0.5 hover:shadow-md
				${
				selected
					? 'border-blue-500 ring-2 ring-blue-100'
					: 'border-slate-200 hover:border-blue-300'
			}
			`}
		>
			<div className="flex gap-4">
				<MatchScore
					score={match.score}
				/>

				<div className="min-w-0 flex-1">
					<div className="flex items-start justify-between gap-3">
						<div className="min-w-0">
							<h3 className="truncate text-base font-bold text-slate-900">
								{job.title}
							</h3>

							{job.company && (
								<p className="mt-1 truncate text-sm font-semibold text-blue-600">
									{job.company}
								</p>
							)}
						</div>

						<span className="text-2xl font-light text-slate-400">
							›
						</span>
					</div>

					<div className="mt-3 flex flex-wrap gap-x-4 gap-y-2 text-xs text-slate-500">
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
						<div className="mt-4 flex flex-wrap gap-2">
							{visibleTags.map((tag) => (
								<span
									key={tag}
									className="
										rounded-lg border border-slate-200
										bg-slate-50 px-2.5 py-1
										text-xs text-slate-600
									"
								>
									{tag}
								</span>
							))}

							{remaining > 0 && (
								<span
									className="
										rounded-lg border border-slate-200
										bg-slate-50 px-2.5 py-1
										text-xs font-medium text-slate-500
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
