import type {
	RankedJob,
} from '../../types/ranking'

import JobCard from './JobCard'


interface JobListProps {
	jobs: RankedJob[]
	selectedIndex: number
	onSelect: (index: number) => void
}

export default function JobList({
									jobs,
									selectedIndex,
									onSelect,
								}: JobListProps) {
	return (
		<section>
			<div className="mb-4 flex items-center justify-between gap-4">
				<h2 className="text-base font-bold text-slate-900">
					{jobs.length}{' '}
					{jobs.length > 1
						? 'offres analysées'
						: 'offre analysée'}
				</h2>

				<div className="flex items-center gap-2">
					<span className="hidden text-sm text-slate-500 sm:inline">
						Trier par :
					</span>

					<select
						defaultValue="score"
						className="
							rounded-xl border border-slate-200
							bg-white px-3 py-2 text-sm text-slate-700
							outline-none focus:border-blue-500
						"
					>
						<option value="score">
							Meilleur score
						</option>
					</select>
				</div>
			</div>

			<div className="space-y-3">
				{jobs.map(
					(rankedJob, index) => (
						<JobCard
							key={
								rankedJob.job.id
								?? `${rankedJob.job.title}-${index}`
							}
							rankedJob={rankedJob}
							selected={
								index === selectedIndex
							}
							onSelect={() => {
								onSelect(index)
							}}
						/>
					),
				)}
			</div>
		</section>
	)
}
