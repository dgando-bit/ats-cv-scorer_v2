interface MatchScoreProps {
	score: number
	size?: 'sm' | 'lg'
}

function getScoreStyle(score: number) {
	if (score >= 85) {
		return {
			label: 'Excellent',
			ring: 'border-emerald-500',
			text: 'text-emerald-600',
			bg: 'bg-emerald-50',
		}
	}

	if (score >= 70) {
		return {
			label: 'Très bon',
			ring: 'border-green-500',
			text: 'text-green-600',
			bg: 'bg-green-50',
		}
	}

	if (score >= 55) {
		return {
			label: 'Moyen',
			ring: 'border-amber-400',
			text: 'text-amber-600',
			bg: 'bg-amber-50',
		}
	}

	return {
		label: 'Faible',
		ring: 'border-red-500',
		text: 'text-red-600',
		bg: 'bg-red-50',
	}
}

export default function MatchScore({
									   score,
									   size = 'sm',
								   }: MatchScoreProps) {
	const roundedScore = Math.round(score)
	const style = getScoreStyle(roundedScore)

	const dimensions =
		size === 'lg'
			? 'h-24 w-24'
			: 'h-20 w-20'

	return (
		<div
			className={`
				${dimensions}
				${style.ring}
				${style.bg}
				flex shrink-0 flex-col items-center justify-center
				rounded-full border-[5px]
			`}
		>
			<div className="flex items-start">
				<span
					className={`
						${style.text}
						text-2xl font-bold
					`}
				>
					{roundedScore}
				</span>

				<span
					className={`
						${style.text}
						mt-1 text-xs font-semibold
					`}
				>
					%
				</span>
			</div>

			<span
				className={`
					${style.text}
					text-xs font-medium
				`}
			>
				{style.label}
			</span>
		</div>
	)
}
