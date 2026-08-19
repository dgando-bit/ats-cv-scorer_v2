import {
	useEffect,
	useRef,
	useState,
} from 'react'

import {
	searchLocations,
	type LocationSuggestion,
} from '../api/locations'

interface LocationAutocompleteProps {
	value: LocationSuggestion | null
	onChange: (
		location: LocationSuggestion | null,
	) => void
}

export default function LocationAutocomplete({
												 value,
												 onChange,
											 }: LocationAutocompleteProps) {
	const [query, setQuery] = useState(
		value?.label ?? '',
	)

	const [suggestions, setSuggestions] =
		useState<LocationSuggestion[]>([])

	const [isLoading, setIsLoading] =
		useState(false)

	const [isOpen, setIsOpen] =
		useState(false)

	const containerRef =
		useRef<HTMLDivElement>(null)

	useEffect(() => {
		function handleClickOutside(
			event: MouseEvent,
		) {
			if (
				containerRef.current
				&& !containerRef.current.contains(
					event.target as Node,
				)
			) {
				setIsOpen(false)
			}
		}

		document.addEventListener(
			'mousedown',
			handleClickOutside,
		)

		return () => {
			document.removeEventListener(
				'mousedown',
				handleClickOutside,
			)
		}
	}, [])

	useEffect(() => {
		const trimmedQuery = query.trim()

		if (
			trimmedQuery.length < 2
			|| trimmedQuery === value?.label
		) {
			setSuggestions([])
			setIsLoading(false)
			return
		}

		const controller = new AbortController()

		const timer = window.setTimeout(
			async () => {
				try {
					setIsLoading(true)

					const results =
						await searchLocations(
							trimmedQuery,
						)

					if (!controller.signal.aborted) {
						setSuggestions(results)
						setIsOpen(true)
					}
				} catch (error) {
					if (!controller.signal.aborted) {
						console.error(
							'Location search error:',
							error,
						)

						setSuggestions([])
					}
				} finally {
					if (!controller.signal.aborted) {
						setIsLoading(false)
					}
				}
			},
			300,
		)

		return () => {
			window.clearTimeout(timer)
			controller.abort()
		}
	}, [query, value?.label])

	function handleInputChange(
		newValue: string,
	) {
		setQuery(newValue)

		// Une modification invalide la sélection
		// précédente.
		if (value) {
			onChange(null)
		}

		if (newValue.trim().length < 2) {
			setSuggestions([])
			setIsOpen(false)
		}
	}

	function handleSelect(
		suggestion: LocationSuggestion,
	) {
		setQuery(suggestion.label)
		setSuggestions([])
		setIsOpen(false)
		onChange(suggestion)
	}

	return (
		<div
			ref={containerRef}
			className="relative"
		>
			<label
				htmlFor="location"
				className="mb-2 block text-sm font-medium text-slate-700"
			>
				Localisation
			</label>

			<div className="relative">
				<input
					id="location"
					type="text"
					value={query}
					autoComplete="off"
					placeholder="Paris, Lyon, 75001..."
					onChange={(event) => {
						handleInputChange(
							event.target.value,
						)
					}}
					onFocus={() => {
						if (suggestions.length > 0) {
							setIsOpen(true)
						}
					}}
					className="
            w-full rounded-xl
            border border-slate-300
            px-3 py-2
            pr-10 text-base
            outline-none
            focus:border-blue-500
            focus:ring-2
            focus:ring-blue-100
          "
				/>

				{isLoading && (
					<div
						className="
              absolute right-3 top-1/2
              size-4 -translate-y-1/2
              animate-spin rounded-full
              border-2 border-slate-200
              border-t-blue-600
            "
					/>
				)}
			</div>

			{isOpen && suggestions.length > 0 && (
				<div
					className="
            absolute z-20 mt-2
            max-h-64 w-full
            overflow-y-auto
            rounded-xl
            border border-slate-200
            bg-white py-1
            shadow-lg
          "
				>
					{suggestions.map(
						(suggestion) => (
							<button
								key={`${suggestion.insee_code}-${suggestion.postal_code ?? ''}`}
								type="button"
								onClick={() => {
									handleSelect(suggestion)
								}}
								className="
                  block w-full
                  px-4 py-3
                  text-left text-sm
                  text-slate-700
                  transition
                  hover:bg-slate-50
                "
							>
                <span className="font-medium">
                  {suggestion.city}
                </span>

								{suggestion.postal_code && (
									<span className="ml-2 text-slate-400">
                    {suggestion.postal_code}
                  </span>
								)}
							</button>
						),
					)}
				</div>
			)}
		</div>
	)
}
