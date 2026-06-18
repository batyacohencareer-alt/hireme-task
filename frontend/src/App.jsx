import React, { useState } from 'react'
import { Search, Loader2, ExternalLink } from 'lucide-react'

function getBadgeClasses(level) {
	const key = String(level || '').toLowerCase()
	switch (key) {
		case 'advanced':
			return 'inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800'
		case 'intermediate':
			return 'inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-yellow-100 text-yellow-800'
		case 'beginner':
			return 'inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800'
		default:
			return 'inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-gray-100 text-gray-800'
	}
}

export default function App() {
	const [username, setUsername] = useState('')
	const [isLoading, setIsLoading] = useState(false)
	const [data, setData] = useState(null)
	const [error, setError] = useState(null)

	const analyze = async () => {
		if (!username) return
		setIsLoading(true)
		setError(null)
		setData(null)

		try {
			const url = `http://localhost:8000/api/evaluate/${encodeURIComponent(username)}`
			const res = await fetch(url)

			if (!res.ok) {
				let message = `Request failed with status ${res.status}`
				try {
					const body = await res.json()
					if (body?.error) message = body.error
					else if (body?.message) message = body.message
				} catch (_) {
					// fallback to text
					try {
						const txt = await res.text()
						if (txt) message = txt
					} catch (_) {}
				}
				setError(message)
				setIsLoading(false)
				return
			}

			const json = await res.json()
			setData(json)
		} catch (err) {
			setError(err?.message || 'Network error')
		} finally {
			setIsLoading(false)
		}
	}

	return (
		<div className="min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-800 dark:text-gray-100 px-6 py-12">
			<header className="max-w-4xl mx-auto text-center mb-10">
				<div className="flex items-center justify-center gap-3 mb-4">
					<span className="text-xl font-bold font-mono">GH</span>
					<h1 className="text-3xl sm:text-4xl font-extrabold">GitHub AI Evaluator</h1>
				</div>
				<p className="text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
					Analyze a GitHub user's repositories with AI to get per-project evaluations and actionable feedback.
				</p>

				<div className="mt-6 flex items-center justify-center gap-3">
					<div className="w-full max-w-xl flex items-center gap-2">
						<input
							value={username}
							onChange={(e) => setUsername(e.target.value)}
							onKeyDown={(e) => e.key === 'Enter' && analyze()}
							placeholder="Enter GitHub username (e.g. octocat)"
							className="flex-1 px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
						/>
						<button
							onClick={analyze}
							disabled={!username || isLoading}
							className="inline-flex items-center gap-2 px-4 py-3 rounded-lg bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white font-semibold"
						>
							<Search className="w-4 h-4" />
							Analyze
						</button>
					</div>
				</div>
			</header>

			<main className="max-w-6xl mx-auto">
				{isLoading && (
					<div className="flex flex-col items-center justify-center py-16">
						<Loader2 className="w-12 h-12 text-indigo-600 animate-spin" />
						<p className="mt-4 text-gray-600 dark:text-gray-300">Analyzing repositories with AI...</p>
					</div>
				)}

				{error && (
					<div className="max-w-3xl mx-auto mb-6 rounded-lg border border-red-200 bg-red-50 dark:bg-red-900/40 p-4">
						<p className="text-sm text-red-800 dark:text-red-200">{error}</p>
					</div>
				)}

				{data?.projects && data.projects.length > 0 && (
					<section>
						<div className="mb-6 flex items-center justify-between">
							<h2 className="text-xl font-semibold">Results</h2>
							<p className="text-sm text-gray-500">{data.projects.length} project(s) evaluated</p>
						</div>

						<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
							{data.projects.map((project) => (
								<article
									key={project.id || project.name}
									className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 shadow-sm"
								>
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
										<span className={getBadgeClasses(project?.evaluation?.level)}>
											{project?.evaluation?.level || 'Unknown'}
										</span>
									</div>

									<p className="mt-3 text-sm text-gray-700 dark:text-gray-200">
										{project?.evaluation?.assessment || 'No assessment available.'}
									</p>
								</article>
							))}
						</div>
					</section>
				)}

				{data && !data.projects?.length && !isLoading && (
					<div className="max-w-3xl mx-auto mt-8 text-center text-gray-600 dark:text-gray-300">
						No repositories found or no evaluations returned for this user.
					</div>
				)}
			</main>
		</div>
	)
}
