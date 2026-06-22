import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'
import ErrorState from '../components/ErrorState'

describe('ErrorState', () => {
  it('renders nothing when no error', () => {
    const { container } = render(<ErrorState error={null} errorStatus={null} />)
    expect(container.firstChild).toBeNull()
  })

  it('renders "User Not Found" for 404', () => {
    render(<ErrorState error="Not found" errorStatus={404} />)
    expect(screen.getByText('User Not Found')).toBeInTheDocument()
  })

  it('renders "User Not Found" for 400', () => {
    render(<ErrorState error="Bad request" errorStatus={400} />)
    expect(screen.getByText('User Not Found')).toBeInTheDocument()
  })

  it('renders generic error for other statuses', () => {
    render(<ErrorState error="Server error" errorStatus={500} />)
    expect(screen.getByText('Server error')).toBeInTheDocument()
  })

  it('renders generic error when status is null', () => {
    render(<ErrorState error="Network error" errorStatus={null} />)
    expect(screen.getByText('Network error')).toBeInTheDocument()
  })
})