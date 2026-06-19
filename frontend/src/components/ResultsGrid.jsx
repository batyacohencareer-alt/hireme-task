import ProjectCard from './ProjectCard'

/**
 * Grid of project evaluation results.
 */
export default function ResultsGrid({ data }) {
  if (!data?.projects?.length) return null

  return (
    <section>
      <div className="mb-6 flex items-center justify-between">
        <h2 className="text-xl font-semibold">Results</h2>
        <p className="text-sm text-gray-500">
          {data.total_evaluated} of {data.projects.length} project(s) evaluated
        </p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {data.projects.map((project) => (
          <ProjectCard key={project.name} project={project} />
        ))}
      </div>
    </section>
  )
}
