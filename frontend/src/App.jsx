import { useState } from 'react'
import ErrorState from './components/ErrorState'
import LoadingSpinner from './components/LoadingSpinner'
import ResultsGrid from './components/ResultsGrid'
import SearchBar from './components/SearchBar'
import { useEvaluate } from './hooks/useEvaluate'

export default function App() {
  const [username, setUsername] = useState('')
  const { data, error, errorStatus, isLoading, analyze, clearError } =
    useEvaluate()

  const handleAnalyze = () => {
    if (username) analyze(username)
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-800 dark:text-gray-100 px-6 py-12">
      <header className="max-w-4xl mx-auto text-center mb-10">
        <h1 className="text-3xl sm:text-4xl font-extrabold mb-4">
          GitHub AI Evaluator
        </h1>
        <p className="text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
          Analyze a GitHub user&apos;s repositories with AI to get per-project
          evaluations and actionable feedback.
        </p>

        <SearchBar
          username={username}
          onChange={setUsername}
          onAnalyze={handleAnalyze}
          isLoading={isLoading}
          onFocus={clearError}
        />
      </header>

      <main className="max-w-6xl mx-auto">
        {isLoading && <LoadingSpinner />}

        <ErrorState error={error} errorStatus={errorStatus} />

        <ResultsGrid data={data} />

        {data && !data.projects?.length && !isLoading && (
          <div className="max-w-3xl mx-auto mt-8 text-center text-gray-600 dark:text-gray-300">
            No repositories found or no evaluations returned for this user.
          </div>
        )}
      </main>
    </div>
  )
}