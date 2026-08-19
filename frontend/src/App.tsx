import { useState } from 'react'

import { rankJobs } from './api/jobs'
import SearchForm, {
  type SearchFormValues,
} from './components/SearchForm'
import type { JobRankingResult } from './types/ranking'

function App() {
  const [result, setResult] =
      useState<JobRankingResult | null>(null)

  const [isLoading, setIsLoading] =
      useState(false)

  const [error, setError] =
      useState<string | null>(null)

  async function handleSearch(
      values: SearchFormValues,
  ) {
    setIsLoading(true)
    setError(null)
    setResult(null)

    try {
      const data = await rankJobs({
        file: values.file,
        keywords: values.keywords,
        location: values.location,
        limit: values.limit,
      })

      setResult(data)

      console.log('Ranking result:', data)
    } catch (err) {
      console.error(err)

      setError(
          err instanceof Error
              ? err.message
              : "Une erreur est survenue pendant l'analyse.",
      )
    } finally {
      setIsLoading(false)
    }
  }

  return (
      <main className="min-h-screen bg-slate-50 px-6 py-8">
        <div className="mx-auto max-w-7xl">
          <header className="mb-8">
            <h1 className="text-3xl font-semibold text-slate-900">
              ATS CV Scorer
            </h1>

            <p className="mt-2 text-slate-600">
              Analysez votre CV et trouvez les offres
              les plus compatibles.
            </p>
          </header>

          <SearchForm
              onSubmit={handleSearch}
              isLoading={isLoading}
          />

          {error && (
              <div
                  className="
              mt-6 rounded-xl
              border border-red-200
              bg-red-50
              px-4 py-3
              text-sm text-red-700
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
              <div className="mt-10 text-center">
                <div
                    className="
                mx-auto size-8
                animate-spin rounded-full
                border-4 border-slate-200
                border-t-blue-600
              "
                />

                <p className="mt-4 text-sm text-slate-600">
                  Recherche et analyse des offres en cours...
                </p>
              </div>
          )}

          {result && !isLoading && (
              <section className="mt-8">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-xl font-semibold text-slate-900">
                      Résultats
                    </h2>

                    {result.candidate_name && (
                        <p className="mt-1 text-sm text-slate-500">
                          Candidat : {result.candidate_name}
                        </p>
                    )}
                  </div>

                  <p className="text-sm text-slate-500">
                    {result.jobs.length}{' '}
                    {result.jobs.length > 1
                        ? 'offres analysées'
                        : 'offre analysée'}
                  </p>
                </div>

                <div className="mt-6 space-y-4">
                  {result.jobs.map(
                      (rankedJob, index) => (
                          <article
                              key={
                                  rankedJob.job.id
                                  ?? `${rankedJob.job.title}-${index}`
                              }
                              className="
                      rounded-2xl
                      border border-slate-200
                      bg-white p-6
                      shadow-sm
                    "
                          >
                            <div className="flex items-start justify-between gap-6">
                              <div>
                                <h3 className="text-lg font-semibold text-slate-900">
                                  {rankedJob.job.title}
                                </h3>

                                {rankedJob.job.company && (
                                    <p className="mt-1 font-medium text-blue-600">
                                      {rankedJob.job.company}
                                    </p>
                                )}

                                <div className="mt-3 flex flex-wrap gap-3 text-sm text-slate-500">
                                  {rankedJob.job.location && (
                                      <span>
                              {rankedJob.job.location}
                            </span>
                                  )}

                                  {rankedJob.job.contract_type && (
                                      <span>
                              {rankedJob.job.contract_type}
                            </span>
                                  )}
                                </div>
                              </div>

                              <div
                                  className="
                          flex size-20 shrink-0
                          items-center justify-center
                          rounded-full
                          border-4 border-emerald-500
                        "
                              >
                        <span className="text-xl font-bold text-slate-900">
                          {Math.round(
                              rankedJob.match.score,
                          )}
                          %
                        </span>
                              </div>
                            </div>

                            <p className="mt-5 text-sm text-slate-600">
                              {rankedJob.explanation.summary}
                            </p>
                          </article>
                      ),
                  )}
                </div>
              </section>
          )}
        </div>
      </main>
  )
}

export default App
