import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'
import ProjectCard from '../components/ProjectCard'

describe('ProjectCard', () => {
  const baseProject = {
    name: 'test-repo',
    html_url: 'https://github.com/user/test-repo',
    evaluation: {
      level: 'Advanced',
      assessment: 'Well-structured project.',
    },
  }

  it('renders project name as a link', () => {
    render(<ProjectCard project={baseProject} />)
    const link = screen.getByRole('link', { name: /test-repo/i })
    expect(link).toHaveAttribute('href', 'https://github.com/user/test-repo')
    expect(link).toHaveAttribute('target', '_blank')
  })

  it('renders evaluation level badge', () => {
    render(<ProjectCard project={baseProject} />)
    expect(screen.getByText('Advanced')).toBeInTheDocument()
  })

  it('renders assessment text', () => {
    render(<ProjectCard project={baseProject} />)
    expect(screen.getByText('Well-structured project.')).toBeInTheDocument()
  })

  it('renders fallback when evaluation is missing', () => {
    const project = { name: 'empty', html_url: '#', evaluation: null }
    render(<ProjectCard project={project} />)
    expect(screen.getByText('Unknown')).toBeInTheDocument()
    expect(screen.getByText('No assessment available.')).toBeInTheDocument()
  })
})
