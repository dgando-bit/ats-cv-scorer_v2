import {
  useState,
} from 'react'

import {
  rankJobs,
} from './api/jobs'

import SearchForm, {
  type SearchFormValues,
} from './components/SearchForm'

import JobDetails from './components/dashboard/JobDetails'
import JobList from './components/dashboard/JobList'

import type {
  JobRankingResult,
} from './types/ranking'


function App() {
  const [
    result,
    setResult,
  ] = useState<JobRankingResult | null>(
      null,
  )

  const [
    selectedIndex,
    setSelectedIndex,
  ] = useState(0)

  const [
    isLoading,
    setIsLoading,
  ] = useState(false)

  const [
    error,
    setError,
  ] = useState<string | null>(
      null,
  )

  async function handleSearch(
      values: SearchFormValues,
  ) {
    setIsLoading(true)
    setError(null)

    try {
      const data = await rankJobs({
        file: values.file,
        keywords: values.keywords,
        location:
        values.location?.label,
        inseeCode:
        values.location?.insee_code,
        limit: values.limit,
      })

      setResult(data)
      setSelectedIndex(0)
    } catch (error) {
      console.error(error)

      setError(
          error instanceof Error
              ? error.message
              : "Une erreur est survenue pendant l'analyse.",
      )
    } finally {
      setIsLoading(false)
    }
  }

  const selectedJob =
      result?.jobs[selectedIndex]

  const initial =
      result?.candidate_name
          ?.trim()
          .charAt(0)
          .toUpperCase()
      ?? 'C'

  return (
      <div className="min-h-screen bg-slate-50 text-slate-900">
        <header className="border-b border-slate-200 bg-white">
          <div
              className="
						mx-auto flex max-w-[1600px] items-center
						justify-between gap-6 px-4 py-4
						sm:px-6 lg:px-8
					"
          >
            <div className="flex items-center gap-3">
              <div
                  className="
								flex h-11 w-11 items-center
								justify-center rounded-xl
								bg-gradient-to-br from-blue-500
								to-indigo-600 text-lg font-bold
								text-white shadow-sm
							"
              >
                ◇
              </div>

              <div>
                <h1 className="text-xl font-bold tracking-tight">
                  ATS CV Scorer
                </h1>

                <p className="hidden text-xs text-slate-500 sm:block">
                  Trouvez les offres adaptées à votre profil
                </p>
              </div>
            </div>

            {result?.candidate_name && (
                <div className="flex items-center gap-3">
                  <div
                      className="
									flex h-10 w-10 items-center justify-center
									rounded-full bg-blue-600 text-sm
									font-bold text-white
								"
                  >
                    {initial}
                  </div>

                  <div className="hidden sm:block">
                    <p className="text-sm font-semibold">
                      {result.candidate_name}
                    </p>

                    <p className="text-xs text-slate-500">
                      Profil candidat
                    </p>
                  </div>
                </div>
            )}
          </div>
        </header>

        <main
            className="
					mx-auto max-w-[1600px] px-4 py-6
					sm:px-6 lg:px-8
				"
        >
          <SearchForm
              onSubmit={handleSearch}
              isLoading={isLoading}
          />

          {error && (
              <div
                  className="
							mt-5 rounded-xl border border-red-200
							bg-red-50 p-4 text-sm text-red-700
						"
              >
                <strong>
                  Impossible d'analyser les offres.
                </strong>

                <p className="mt-1">
                  {error}
                </p>
              </div>
          )}

          {isLoading && (
              <div
                  className="
							mt-8 flex flex-col items-center
							justify-center rounded-2xl border
							border-slate-200 bg-white px-6 py-20
							text-center shadow-sm
						"
              >
                <div
                    className="
								h-10 w-10 animate-spin rounded-full
								border-4 border-blue-100
								border-t-blue-600
							"
                />

                <h2 className="mt-5 text-lg font-bold">
                  Analyse des offres en cours
                </h2>

                <p className="mt-2 max-w-md text-sm text-slate-500">
                  Nous recherchons les offres,
                  analysons leurs exigences et les
                  comparons avec votre CV.
                </p>
              </div>
          )}

          {result
              && !isLoading
              && result.jobs.length === 0 && (
                  <div
                      className="
								mt-8 rounded-2xl border border-slate-200
								bg-white p-12 text-center shadow-sm
							"
                  >
                    <h2 className="text-lg font-bold">
                      Aucune offre trouvée
                    </h2>

                    <p className="mt-2 text-sm text-slate-500">
                      Essayez d'autres mots-clés ou
                      une autre localisation.
                    </p>
                  </div>
              )}

          {result
              && !isLoading
              && selectedJob && (
                  <div
                      className="
								mt-6 grid gap-6
								xl:grid-cols-[minmax(380px,0.82fr)_minmax(600px,1.35fr)]
							"
                  >
                    <JobList
                        jobs={result.jobs}
                        selectedIndex={selectedIndex}
                        onSelect={setSelectedIndex}
                    />

                    <div className="xl:sticky xl:top-6 xl:self-start">
                      <JobDetails
                          rankedJob={selectedJob}
                      />
                    </div>
                  </div>
              )}
        </main>
      </div>
  )
}

export default App
