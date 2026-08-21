interface ScoreBarProps {
	label: string
	score: number
}

function getBarColor(score: number) {
	if (score >= 75) {
		return 'bg-emerald-500'
	}

	if (score >= 50) {
		return 'bg-amber-400'
	}

	return 'bg-red-500'
}

export default function ScoreBar({
									 label,
									 score,
								 }: ScoreBarProps) {
	const roundedScore = Math.round(score)

	return (
		<div>
			<div className="mb-2 flex items-center justify-between gap-4">
				<span className="text-sm font-medium text-slate-700">
					{label}
				</span>

				<span className="text-sm font-bold text-slate-900">
					{roundedScore}%
				</span>
			</div>

			<div className="h-2 overflow-hidden rounded-full bg-slate-200">
				<div
					className={`
						h-full rounded-full transition-all duration-500
						${getBarColor(roundedScore)}
					`}
					style={{
						width: `${Math.max(
							0,
							Math.min(roundedScore, 100),
						)}%`,
					}}
				/>
			</div>
		</div>
	)
}
