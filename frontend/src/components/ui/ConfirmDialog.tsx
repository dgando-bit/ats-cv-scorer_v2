import {
	useEffect,
} from 'react'


interface ConfirmDialogProps {
	open: boolean
	title: string
	description: string

	confirmLabel?: string
	cancelLabel?: string

	onConfirm: () => void
	onCancel: () => void
}


export default function ConfirmDialog({
										  open,
										  title,
										  description,
										  confirmLabel = 'Confirmer',
										  cancelLabel = 'Annuler',
										  onConfirm,
										  onCancel,
									  }: ConfirmDialogProps) {
	useEffect(
		() => {
			if (!open) {
				return
			}

			function handleKeyDown(
				event: KeyboardEvent,
			) {
				if (event.key === 'Escape') {
					onCancel()
				}
			}

			document.addEventListener(
				'keydown',
				handleKeyDown,
			)

			const previousOverflow =
				document.body.style.overflow

			document.body.style.overflow =
				'hidden'

			return () => {
				document.removeEventListener(
					'keydown',
					handleKeyDown,
				)

				document.body.style.overflow =
					previousOverflow
			}
		},
		[
			open,
			onCancel,
		],
	)

	if (!open) {
		return null
	}

	return (
		<div
			className="
				fixed inset-0 z-[100]
				flex items-center justify-center
				bg-slate-950/40 p-4
				backdrop-blur-[2px]
			"
			onMouseDown={
				(event) => {
					if (
						event.target
						=== event.currentTarget
					) {
						onCancel()
					}
				}
			}
		>
			<div
				role="alertdialog"
				aria-modal="true"
				aria-labelledby="confirm-dialog-title"
				aria-describedby="confirm-dialog-description"
				className="
					w-full max-w-md
					rounded-2xl border
					border-slate-200 bg-white
					p-6 shadow-2xl
				"
			>
				<div className="flex gap-4">
					<div
						className="
							flex h-11 w-11
							shrink-0 items-center
							justify-center rounded-full
							bg-red-50
							text-xl text-red-600
						"
						aria-hidden="true"
					>
						!
					</div>

					<div className="min-w-0">
						<h2
							id="confirm-dialog-title"
							className="
								text-lg font-bold
								text-slate-900
							"
						>
							{title}
						</h2>

						<p
							id="confirm-dialog-description"
							className="
								mt-2 text-sm
								leading-6 text-slate-500
							"
						>
							{description}
						</p>
					</div>
				</div>

				<div
					className="
						mt-7 flex flex-col-reverse
						gap-3 sm:flex-row
						sm:justify-end
					"
				>
					<button
						type="button"
						onClick={onCancel}
						className="
							rounded-xl border
							border-slate-300 bg-white
							px-4 py-2.5
							text-sm font-semibold
							text-slate-700
							transition
							hover:bg-slate-50
							focus:outline-none
							focus:ring-2
							focus:ring-slate-300
						"
					>
						{cancelLabel}
					</button>

					<button
						type="button"
						onClick={onConfirm}
						autoFocus
						className="
							rounded-xl bg-red-600
							px-4 py-2.5
							text-sm font-semibold
							text-white transition
							hover:bg-red-700
							focus:outline-none
							focus:ring-2
							focus:ring-red-300
						"
					>
						{confirmLabel}
					</button>
				</div>
			</div>
		</div>
	)
}
