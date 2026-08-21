import type {
	AnalysisHistoryItem,
} from '../../types/history'


interface AnalysisHistoryProps {
	items: AnalysisHistoryItem[]

	onOpen: (
		item: AnalysisHistoryItem,
	) => void

	onDelete: (
		id: string,
	) => void

	onClear: () => void

	onNewAnalysis: () => void
}


function formatDate(
	value: string,
): string {
	const date = new Date(
		value,
	)

	return new Intl.DateTimeFormat(
		'fr-FR',
		{
			dateStyle: 'medium',
			timeStyle: 'short',
		},
	).format(
		date,
	)
}


function getBestScore(
	item: AnalysisHistoryItem,
): number | null {
	if (
		item.result.jobs.length === 0
	) {
		return null
	}

	return Math.max(
		...item.result.jobs.map(
			(job) => job.match.score,
		),
	)
}


function getScoreClasses(
	score: number,
): string {
	if (score >= 85) {
		return (
			'border-emerald-200 '
			+ 'bg-emerald-50 '
			+ 'text-emerald-700'
		)
	}

	if (score >= 70) {
		return (
			'border-green-200 '
			+ 'bg-green-50 '
			+ 'text-green-700'
		)
	}

	if (score >= 55) {
		return (
			'border-amber-200 '
			+ 'bg-amber-50 '
			+ 'text-amber-700'
		)
	}

	return (
		'border-red-200 '
		+ 'bg-red-50 '
		+ 'text-red-700'
	)
}


export default function AnalysisHistory({
											items,
											onOpen,
											onDelete,
											onClear,
											onNewAnalysis,
										}: AnalysisHistoryProps) {
	if (items.length === 0) {
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
						sm:py-14
					"
				>
					<div
						className="
							flex h-14 w-14
							items-center
							justify-center
							rounded-2xl
							bg-indigo-50
							text-xl
							text-indigo-600
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
						Aucune analyse enregistrée
					</h3>

					<p
						className="
							mt-2 max-w-md
							text-sm leading-6
							text-slate-500
						"
					>
						Vos prochaines recherches
						apparaîtront ici et pourront être
						rouvertes sans relancer l'analyse.
					</p>

					<button
						type="button"
						onClick={
							onNewAnalysis
						}
						className="
							mt-6 w-full
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
						Nouvelle analyse
					</button>
				</div>
			</div>
		)
	}


	return (
		<div className="space-y-4 sm:space-y-5">
			<div
				className="
					flex flex-col
					gap-3
					sm:flex-row
					sm:items-center
					sm:justify-between
				"
			>
				<p className="text-sm text-slate-500">
					{items.length}{' '}

					{items.length > 1
						? 'analyses enregistrées'
						: 'analyse enregistrée'}
				</p>

				<button
					type="button"
					onClick={
						onClear
					}
					className="
						w-full
						rounded-lg
						border
						border-red-200
						bg-white
						px-3 py-2
						text-sm
						font-medium
						text-red-600
						transition
						hover:bg-red-50
						sm:w-auto
						sm:self-start
					"
				>
					Effacer l'historique
				</button>
			</div>

			<div className="space-y-3">
				{items.map(
					(item) => {
						const bestScore =
							getBestScore(
								item,
							)

						return (
							<div
								key={
									item.id
								}
								className="
									rounded-2xl
									border
									border-slate-200
									bg-white
									p-4 shadow-sm
									transition
									hover:shadow-md
									sm:p-5
								"
							>
								<div
									className="
										flex flex-col
										gap-4
										lg:flex-row
										lg:items-center
										lg:justify-between
										lg:gap-5
									"
								>
									<div
										className="
											min-w-0
											flex-1
										"
									>
										<div
											className="
												flex flex-col
												gap-2
												sm:flex-row
												sm:flex-wrap
												sm:items-center
											"
										>
											<h3
												className="
													break-words
													text-base
													font-bold
													text-slate-900
												"
											>
												{item.keywords}
											</h3>

											{bestScore !== null && (
												<span
													className={`
														self-start
														rounded-full
														border
														px-2.5
														py-1
														text-xs
														font-bold
														${getScoreClasses(
														bestScore,
													)}
													`}
												>
													Meilleur :
													{' '}
													{Math.round(
														bestScore,
													)}
													%
												</span>
											)}
										</div>

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
											{item.location && (
												<span className="break-words">
													📍{' '}
													{item.location}
												</span>
											)}

											<span>
												▤{' '}
												{
													item.result.jobs.length
												}{' '}
												offres
											</span>

											<span>
												◷{' '}
												{formatDate(
													item.createdAt,
												)}
											</span>
										</div>

										{item.candidateName && (
											<p
												className="
													mt-3
													break-words
													text-xs
													text-slate-400
												"
											>
												CV :{' '}
												{item.candidateName}
											</p>
										)}
									</div>

									<div
										className="
											grid shrink-0
											grid-cols-2
											gap-2
											sm:flex
											sm:justify-end
										"
									>
										<button
											type="button"
											onClick={() => {
												onOpen(
													item,
												)
											}}
											className="
												rounded-xl
												bg-blue-600
												px-4 py-2.5
												text-sm
												font-semibold
												text-white
												transition
												hover:bg-blue-700
											"
										>
											Ouvrir
										</button>

										<button
											type="button"
											onClick={() => {
												onDelete(
													item.id,
												)
											}}
											className="
												rounded-xl
												border
												border-slate-200
												bg-white
												px-4 py-2.5
												text-sm
												font-medium
												text-slate-600
												transition
												hover:border-red-200
												hover:bg-red-50
												hover:text-red-600
											"
										>
											Supprimer
										</button>
									</div>
								</div>
							</div>
						)
					},
				)}
			</div>
		</div>
	)
}
