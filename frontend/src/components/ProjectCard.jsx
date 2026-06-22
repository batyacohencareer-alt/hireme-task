import { ExternalLink } from 'lucide-react'

const BADGE_CLASSES = {
  advanced:
    'inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800',
  intermediate:
    'inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-yellow-100 text-yellow-800',
  beginner:
    'inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800',
}

const DEFAULT_BADGE =
  'inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-gray-100 text-gray-800'

function getBadgeClasses(level) {
  return BADGE_CLASSES[String(level || '').toLowerCase()] || DEFAULT_BADGE
}

/**
 * Card displaying a single project evaluation result.
 */
export default function ProjectCard({ project }) {
  const level = project?.evaluation?.level || 'Unknown'
  const assessment = project?.evaluation?.assessment || 'No assessment available.'

  return (
    <article className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <a
          href={project.html_url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-lg font-semibold text-indigo-600 hover:underline inline-flex items-center gap-2"
        >
          {project.name}
          <ExternalLink className="w-4 h-4" />
        </a>
        <span className={getBadgeClasses(level)}>{level}</span>
      </div>
      <p className="mt-3 text-sm text-gray-700 dark:text-gray-200">{assessment}</p>
    </article>
  )
}