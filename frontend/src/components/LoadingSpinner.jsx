import { Loader2 } from 'lucide-react'

/**
 * Full-page loading spinner shown during analysis.
 */
export default function LoadingSpinner() {
  return (
    <div className="flex flex-col items-center justify-center py-16">
      <Loader2 className="w-12 h-12 text-indigo-600 animate-spin" />
      <p className="mt-4 text-gray-600 dark:text-gray-300">
        Analyzing repositories with AI…
      </p>
    </div>
  )
}
