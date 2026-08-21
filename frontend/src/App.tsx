import {
  useState,
} from 'react'

import {
  ApiError,
  rankJobs,
} from './api/jobs'

import {
  extractCV,
} from './api/cv'

import SearchForm, {
  type SearchFormValues,
} from './components/SearchForm'

import JobDetails from './components/dashboard/JobDetails'
import JobList from './components/dashboard/JobList'
import AnalysisHistory from './components/history/AnalysisHistory'
import CVProfile from './components/profile/CVProfile'
import ConfirmDialog from './components/ui/ConfirmDialog'

import {
  clearAnalysisHistory,
  deleteAnalysis,
  getAnalysisHistory,
  saveAnalysis,
} from './utils/historyStorage'

import type {
  CV,
} from './types/cv'

import type {
  AnalysisHistoryItem,
} from './types/history'

import type {
  JobRankingResult,
} from './types/ranking'


type AppView =
    | 'dashboard'
    | 'history'
    | 'profile'


type ConfirmationState =
    | {
  type: 'delete-analysis'
  id: string
}
    | {
  type: 'clear-history'
}
    | null


interface NavigationItem {
  key: AppView
  label: string
  icon: string
}


const navigationItems: NavigationItem[] = [
  {
    key: 'dashboard',
    label: 'Tableau de bord',
    icon: '⌂',
  },
  {
    key: 'history',
    label: 'Offres analysées',
    icon: '▤',
  },
  {
    key: 'profile',
    label: 'CV & Profil',
    icon: '♙',
  },
]


function App() {
  const [
    activeView,
    setActiveView,
  ] = useState<AppView>(
      'dashboard',
  )

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

  const [
    locationError,
    setLocationError,
  ] = useState<string | null>(
      null,
  )

  const [
    cv,
    setCV,
  ] = useState<CV | null>(
      null,
  )

  const [
    isCVLoading,
    setIsCVLoading,
  ] = useState(false)

  const [
    cvError,
    setCVError,
  ] = useState<string | null>(
      null,
  )

  const [
    history,
    setHistory,
  ] = useState<AnalysisHistoryItem[]>(
      () => getAnalysisHistory(),
  )

  const [
    isMobileMenuOpen,
    setIsMobileMenuOpen,
  ] = useState(false)

  const [
    isMobileJobDetailsOpen,
    setIsMobileJobDetailsOpen,
  ] = useState(false)

  const [
    confirmation,
    setConfirmation,
  ] = useState<ConfirmationState>(
      null,
  )


  async function handleCVUpload(
      file: File,
  ) {
    setIsCVLoading(
        true,
    )

    setCVError(
        null,
    )

    try {
      const extractedCV =
          await extractCV(
              file,
          )

      setCV(
          extractedCV,
      )
    } catch (error) {
      console.error(
          error,
      )

      setCVError(
          error instanceof Error
              ? error.message
              : (
                  "Une erreur est survenue "
                  + "pendant l'analyse du CV."
              ),
      )
    } finally {
      setIsCVLoading(
          false,
      )
    }
  }


  async function handleSearch(
      values: SearchFormValues,
  ) {
    setIsLoading(
        true,
    )

    setError(
        null,
    )

    setLocationError(
        null,
    )

    /*
     * On analyse aussi le CV pour alimenter
     * automatiquement "CV & Profil".
     *
     * L'extraction est lancée en parallèle
     * de la recherche d'offres.
     */
    if (!isCVLoading) {
      void handleCVUpload(
          values.file,
      )
    }

    try {
      const data =
          await rankJobs({
            file:
            values.file,

            keywords:
            values.keywords,

            location:
            values.location?.label,

            inseeCode:
            values.location?.insee_code,

            limit:
            values.limit,
          })

      setResult(
          data,
      )

      setSelectedIndex(
          0,
      )

      setIsMobileJobDetailsOpen(
          false,
      )

      saveAnalysis({
        keywords:
        values.keywords,

        location:
            values.location?.label
            ?? null,

        limit:
        values.limit,

        result:
        data,
      })

      setHistory(
          getAnalysisHistory(),
      )
    } catch (error) {
      console.error(
          error,
      )

      if (
          error instanceof ApiError
          && error.code === 'unknown_location'
      ) {
        setLocationError(
            error.message,
        )

        return
      }

      setError(
          error instanceof Error
              ? error.message
              : (
                  "Une erreur est survenue "
                  + "pendant l'analyse."
              ),
      )
    } finally {
      setIsLoading(
          false,
      )
    }
  }


  function changeView(
      view: AppView,
  ) {
    setActiveView(
        view,
    )

    setIsMobileMenuOpen(
        false,
    )
  }


  function handleOpenHistory(
      item: AnalysisHistoryItem,
  ) {
    setResult(
        item.result,
    )

    setSelectedIndex(
        0,
    )

    setIsMobileJobDetailsOpen(
        false,
    )

    changeView(
        'dashboard',
    )
  }


  function handleDeleteHistory(
      id: string,
  ) {
    setConfirmation({
      type:
          'delete-analysis',

      id,
    })
  }


  function handleClearHistory() {
    setConfirmation({
      type:
          'clear-history',
    })
  }


  function handleCancelConfirmation() {
    setConfirmation(
        null,
    )
  }


  function handleConfirmAction() {
    if (!confirmation) {
      return
    }

    if (
        confirmation.type
        === 'delete-analysis'
    ) {
      const updated =
          deleteAnalysis(
              confirmation.id,
          )

      setHistory(
          updated,
      )
    }

    if (
        confirmation.type
        === 'clear-history'
    ) {
      clearAnalysisHistory()

      setHistory(
          [],
      )
    }

    setConfirmation(
        null,
    )
  }


  const selectedJob =
      result?.jobs[
          selectedIndex
          ]


  const candidateName =
      cv?.candidate_name
      ?? result?.candidate_name
      ?? 'Candidat'


  const initial =
      candidateName
          .trim()
          .charAt(0)
          .toUpperCase()
      || 'C'


  function renderDashboard() {
    return (
        <>
          <div className="mb-6">
            <h2
                className="
              text-2xl font-bold
              tracking-tight
              text-slate-900
            "
            >
              Tableau de bord
            </h2>

            <p
                className="
              mt-1 text-sm
              text-slate-500
            "
            >
              Recherchez des offres
              et comparez-les avec votre CV.
            </p>
          </div>

          <SearchForm
              onSubmit={
                handleSearch
              }
              isLoading={
                isLoading
              }
              locationError={
                locationError
              }
              onLocationChange={() => {
                setLocationError(
                    null,
                )
              }}
          />

          {error && (
              <div
                  className="
              mt-5 rounded-xl
              border border-red-200
              bg-red-50 p-4
              text-sm text-red-700
            "
              >
                <strong>
                  Impossible d'analyser
                  les offres.
                </strong>

                <p className="mt-1">
                  {error}
                </p>
              </div>
          )}

          {isLoading && (
              <div
                  className="
              mt-8 flex flex-col
              items-center
              justify-center
              rounded-2xl border
              border-slate-200
              bg-white px-6
              py-20 text-center
              shadow-sm
            "
              >
                <div
                    className="
                h-10 w-10
                animate-spin
                rounded-full
                border-4
                border-blue-100
                border-t-blue-600
              "
                />

                <h2
                    className="
                mt-5 text-lg
                font-bold
              "
                >
                  Analyse des offres
                  en cours
                </h2>

                <p
                    className="
                mt-2 max-w-md
                text-sm
                text-slate-500
              "
                >
                  Nous recherchons les offres,
                  analysons leur pertinence
                  et les comparons avec votre CV.
                </p>

                <p
                    className="
                mt-4 text-xs
                text-slate-400
              "
                >
                  Cette étape peut prendre
                  quelques secondes.
                </p>
              </div>
          )}

          {result
              && !isLoading
              && result.jobs.length === 0 && (
                  <div
                      className="
                mt-8 rounded-2xl
                border
                border-slate-200
                bg-white p-12
                text-center
                shadow-sm
              "
                  >
                    <h2
                        className="
                  text-lg font-bold
                "
                    >
                      Aucune offre trouvée
                    </h2>

                    <p
                        className="
                  mt-2 text-sm
                  text-slate-500
                "
                    >
                      Essayez d'autres
                      mots-clés ou une autre
                      localisation.
                    </p>
                  </div>
              )}

          {result
              && !isLoading
              && selectedJob && (
                  <div className="mt-6">
                    {/* Mobile / tablette */}
                    <div className="xl:hidden">
                      {!isMobileJobDetailsOpen ? (
                          <JobList
                              jobs={
                                result.jobs
                              }
                              selectedIndex={
                                selectedIndex
                              }
                              onSelect={
                                (index) => {
                                  setSelectedIndex(
                                      index,
                                  )

                                  setIsMobileJobDetailsOpen(
                                      true,
                                  )

                                  window.scrollTo({
                                    top: 0,
                                    behavior:
                                        'smooth',
                                  })
                                }
                              }
                          />
                      ) : (
                          <div>
                            <button
                                type="button"
                                onClick={() => {
                                  setIsMobileJobDetailsOpen(
                                      false,
                                  )
                                }}
                                className="
                        mb-4
                        inline-flex
                        items-center
                        gap-2
                        rounded-xl
                        border
                        border-slate-200
                        bg-white
                        px-4 py-2
                        text-sm
                        font-semibold
                        text-slate-700
                        shadow-sm
                        transition
                        hover:bg-slate-50
                      "
                            >
                      <span
                          aria-hidden="true"
                      >
                        ←
                      </span>

                              Retour aux offres
                            </button>

                            <JobDetails
                                rankedJob={
                                  selectedJob
                                }
                            />
                          </div>
                      )}
                    </div>

                    {/* Desktop */}
                    <div
                        className="
                  hidden gap-6
                  xl:grid
                  xl:grid-cols-[minmax(360px,0.8fr)_minmax(620px,1.4fr)]
                "
                    >
                      <JobList
                          jobs={
                            result.jobs
                          }
                          selectedIndex={
                            selectedIndex
                          }
                          onSelect={
                            setSelectedIndex
                          }
                      />

                      <div
                          className="
                    xl:sticky
                    xl:top-6
                    xl:self-start
                  "
                      >
                        <JobDetails
                            rankedJob={
                              selectedJob
                            }
                        />
                      </div>
                    </div>
                  </div>
              )}

          {!result
              && !isLoading && (
                  <div
                      className="
                mt-8 rounded-2xl
                border
                border-dashed
                border-slate-300
                bg-white px-6
                py-16 text-center
              "
                  >
                    <div
                        className="
                  mx-auto flex
                  h-14 w-14
                  items-center
                  justify-center
                  rounded-2xl
                  bg-blue-50
                  text-2xl
                  text-blue-600
                "
                    >
                      ⌕
                    </div>

                    <h3
                        className="
                  mt-5 text-lg
                  font-bold
                  text-slate-900
                "
                    >
                      Commencez une analyse
                    </h3>

                    <p
                        className="
                  mx-auto mt-2
                  max-w-md
                  text-sm
                  leading-6
                  text-slate-500
                "
                    >
                      Importez votre CV,
                      indiquez le poste
                      recherché et laissez
                      ATS CV Scorer classer
                      les offres les plus
                      pertinentes.
                    </p>
                  </div>
              )}
        </>
    )
  }


  function renderHistory() {
    return (
        <div>
          <div className="mb-6">
            <h2
                className="
              text-2xl font-bold
              tracking-tight
              text-slate-900
            "
            >
              Offres analysées
            </h2>

            <p
                className="
              mt-1 text-sm
              text-slate-500
            "
            >
              Retrouvez et rouvrez
              vos analyses précédentes
              sans relancer le moteur.
            </p>
          </div>

          <AnalysisHistory
              items={
                history
              }
              onOpen={
                handleOpenHistory
              }
              onDelete={
                handleDeleteHistory
              }
              onClear={
                handleClearHistory
              }
              onNewAnalysis={() => {
                changeView(
                    'dashboard',
                )
              }}
          />
        </div>
    )
  }


  function renderProfile() {
    return (
        <div>
          <div className="mb-6">
            <h2
                className="
              text-2xl font-bold
              tracking-tight
              text-slate-900
            "
            >
              CV & Profil
            </h2>

            <p
                className="
              mt-1 text-sm
              text-slate-500
            "
            >
              Consultez et gérez
              les informations extraites
              de votre CV.
            </p>
          </div>

          <CVProfile
              cv={
                cv
              }
              isLoading={
                isCVLoading
              }
              error={
                cvError
              }
              onUpload={
                handleCVUpload
              }
          />
        </div>
    )
  }


  function renderActiveView() {
    switch (
        activeView
        ) {
      case 'history':
        return renderHistory()

      case 'profile':
        return renderProfile()

      case 'dashboard':
      default:
        return renderDashboard()
    }
  }


  return (
      <div
          className="
        min-h-screen
        bg-slate-50
        text-slate-900
      "
      >
        {/* Header mobile */}
        <header
            className="
          sticky top-0 z-40
          flex items-center
          justify-between
          border-b
          border-slate-200
          bg-white px-4
          py-3 lg:hidden
        "
        >
          <div
              className="
            flex items-center
            gap-3
          "
          >
            <div
                className="
              flex h-10 w-10
              items-center
              justify-center
              rounded-xl
              bg-gradient-to-br
              from-blue-500
              to-indigo-600
              font-bold
              text-white
            "
            >
              ◇
            </div>

            <span className="font-bold">
            ATS CV Scorer
          </span>
          </div>

          <button
              type="button"
              onClick={() => {
                setIsMobileMenuOpen(
                    (value) => !value,
                )
              }}
              className="
            flex h-10 w-10
            items-center
            justify-center
            rounded-xl
            border
            border-slate-200
            bg-white text-xl
          "
          >
            ☰
          </button>
        </header>

        <div className="flex min-h-screen">
          {/* Sidebar */}
          <aside
              className={`
            fixed inset-y-0 left-0
            z-50 flex w-64
            flex-col border-r
            border-slate-200
            bg-white
            transition-transform
            duration-200
            lg:translate-x-0
            ${
                  isMobileMenuOpen
                      ? 'translate-x-0'
                      : '-translate-x-full'
              }
          `}
          >
            <div
                className="
              flex h-[76px]
              items-center gap-3
              border-b
              border-slate-100
              px-5
            "
            >
              <div
                  className="
                flex h-11 w-11
                items-center
                justify-center
                rounded-xl
                bg-gradient-to-br
                from-blue-500
                to-indigo-600
                text-lg font-bold
                text-white shadow-sm
              "
              >
                ◇
              </div>

              <div>
                <h1
                    className="
                  font-bold
                  tracking-tight
                "
                >
                  ATS CV Scorer
                </h1>

                <p
                    className="
                  text-xs
                  text-slate-400
                "
                >
                  Analyse intelligente
                </p>
              </div>
            </div>

            <nav
                className="
              flex-1
              space-y-1 p-4
            "
            >
              {navigationItems.map(
                  (item) => (
                      <button
                          key={
                            item.key
                          }
                          type="button"
                          onClick={() => {
                            changeView(
                                item.key,
                            )
                          }}
                          className={`
                    flex w-full
                    items-center
                    gap-3 rounded-xl
                    px-4 py-3
                    text-left
                    text-sm
                    font-medium
                    transition
                    ${
                              activeView
                              === item.key
                                  ? 'bg-blue-50 text-blue-700'
                                  : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                          }
                  `}
                      >
                  <span
                      className="
                      w-5
                      text-center
                      text-lg
                    "
                  >
                    {item.icon}
                  </span>

                        <span>
                    {item.label}
                  </span>
                      </button>
                  ),
              )}
            </nav>

            <div
                className="
              border-t
              border-slate-100
              p-4
            "
            >
              <div
                  className="
                flex items-center
                gap-3 rounded-xl
                bg-slate-50
                p-3
              "
              >
                <div
                    className="
                  flex h-10 w-10
                  shrink-0
                  items-center
                  justify-center
                  rounded-full
                  bg-blue-600
                  text-sm
                  font-bold
                  text-white
                "
                >
                  {initial}
                </div>

                <div className="min-w-0">
                  <p
                      className="
                    truncate
                    text-sm
                    font-semibold
                    text-slate-800
                  "
                  >
                    {candidateName}
                  </p>

                  <p
                      className="
                    text-xs
                    text-slate-400
                  "
                  >
                    Profil candidat
                  </p>
                </div>
              </div>
            </div>
          </aside>

          {/* Overlay mobile */}
          {isMobileMenuOpen && (
              <button
                  type="button"
                  aria-label="Fermer le menu"
                  onClick={() => {
                    setIsMobileMenuOpen(
                        false,
                    )
                  }}
                  className="
              fixed inset-0
              z-40
              bg-slate-900/30
              backdrop-blur-[1px]
              lg:hidden
            "
              />
          )}

          {/* Contenu principal */}
          <div
              className="
            min-w-0 flex-1
            lg:ml-64
          "
          >
            <header
                className="
              hidden h-[76px]
              items-center
              justify-end
              border-b
              border-slate-200
              bg-white px-8
              lg:flex
            "
            >
              <div
                  className="
                flex items-center
                gap-3
              "
              >
                <div
                    className="
                  flex h-10 w-10
                  items-center
                  justify-center
                  rounded-full
                  bg-blue-600
                  text-sm
                  font-bold
                  text-white
                "
                >
                  {initial}
                </div>

                <div>
                  <p
                      className="
                    text-sm
                    font-semibold
                  "
                  >
                    {candidateName}
                  </p>

                  <p
                      className="
                    text-xs
                    text-slate-400
                  "
                  >
                    Profil candidat
                  </p>
                </div>
              </div>
            </header>

            <main
                className="
              mx-auto
              max-w-[1600px]
              p-4
              sm:p-6
              lg:p-8
            "
            >
              {renderActiveView()}
            </main>
          </div>
        </div>

        <ConfirmDialog
            open={
                confirmation !== null
            }
            title={
              confirmation?.type
              === 'clear-history'
                  ? "Effacer tout l'historique ?"
                  : 'Supprimer cette analyse ?'
            }
            description={
              confirmation?.type
              === 'clear-history'
                  ? (
                      `Les ${history.length} analyses enregistrées `
                      + 'seront définitivement supprimées. '
                      + 'Cette action est irréversible.'
                  )
                  : (
                      'Cette analyse sera définitivement '
                      + 'supprimée de votre historique.'
                  )
            }
            confirmLabel={
              confirmation?.type
              === 'clear-history'
                  ? 'Tout supprimer'
                  : 'Supprimer'
            }
            cancelLabel="Annuler"
            onConfirm={
              handleConfirmAction
            }
            onCancel={
              handleCancelConfirmation
            }
        />
      </div>
  )
}


export default App
