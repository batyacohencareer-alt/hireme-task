import { UserX } from 'lucide-react'

/**
 * Displays error states — a friendly "not found" card for 404/400,
 * or a generic error banner for other errors.
 */
export default function ErrorState({ error, errorStatus }) {
  if (!error) return null

  if (errorStatus === 404 || errorStatus === 400) {
    return (
      <div className="max-w-3xl mx-auto mb-6 flex flex-col items-center justify-center rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50 p-12">
        <UserX className="w-16 h-16 text-gray-400 dark:text-gray-500 mb-4" />
        <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-2">
          User Not Found
        </h3>
        <p className="text-gray-600 dark:text-gray-400 text-center max-w-md">
          We couldn&apos;t find a GitHub user with that name. Please check the spelling and try
          again.
        </p>
      </div>
    )
  }

  return (
    <div className="max-w-3xl mx-auto mb-6 rounded-lg border border-red-200 bg-red-50 dark:bg-red-900/40 p-4">
      <p className="text-sm text-red-800 dark:text-red-200">{error}</p>
    </div>
  )
}
