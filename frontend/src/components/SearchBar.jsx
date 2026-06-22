import { Search, Loader2 } from 'lucide-react'

/**
 * Search bar with username input and analyze button.
 */
export default function SearchBar({ username, onChange, onAnalyze, isLoading, onFocus }) {
  return (
    <div className="mt-6 flex items-center justify-center gap-3">
      <div className="w-full max-w-xl flex items-center gap-2">
        <input
          value={username}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && onAnalyze()}
          onFocus={onFocus}
          placeholder="Enter GitHub username (e.g. octocat)"
          className="flex-1 px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          aria-label="GitHub username"
        />
        <button
          onClick={onAnalyze}
          disabled={!username || isLoading}
          className="inline-flex items-center gap-2 px-4 py-3 rounded-lg bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white font-semibold transition-colors"
        >
          {isLoading ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Search className="w-4 h-4" />
          )}
          {isLoading ? 'Analyzing…' : 'Analyze'}
        </button>
      </div>
    </div>
  )
}