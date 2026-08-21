import type {
	RankedJob,
} from '../../types/ranking'

import JobCard from './JobCard'


interface JobListProps {
	jobs: RankedJob[]
	selectedIndex: number
	onSelect: (
		index: number,
	) => void
}


export default function JobList({
									jobs,
									selectedIndex,
									onSelect,
								}: JobListProps) {
	return (
		<section className="min-w-0">
			<div
				className="
					mb-4 flex
					flex-col gap-3

					sm:flex-row
					sm:items-center
					sm:justify-between
				"
			>
				<h2
					className="
						text-base font-bold
						text-slate-900
					"
				>
					{jobs.length}{' '}
					{jobs.length > 1
						? 'offres analysées'
						: 'offre analysée'}
				</h2>

				<div
					className="
						flex items-center
						gap-2
					"
				>
					<span
						className="
							hidden text-sm
							text-slate-500
							sm:inline
						"
					>
						Trier par :
					</span>

					<select
						defaultValue="score"
						className="
							h-10 w-full
							rounded-xl border
							border-slate-200
							bg-white px-3
							text-sm text-slate-700
							outline-none
							transition

							focus:border-blue-500
							focus:ring-2
							focus:ring-blue-100

							sm:w-auto
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
					(
						rankedJob,
						index,
					) => (
						<JobCard
							key={
								rankedJob.job.id
								?? `${rankedJob.job.title}-${index}`
							}
							rankedJob={
								rankedJob
							}
							selected={
								index
								=== selectedIndex
							}
							onSelect={() => {
								onSelect(
									index,
								)
							}}
						/>
					),
				)}
			</div>
		</section>
	)
}
