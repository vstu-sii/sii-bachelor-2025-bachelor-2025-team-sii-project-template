import React from 'react'
import { render, screen } from '@testing-library/react'
import LoadingSpinner from '@/components/ui/LoadingSpinner'

describe('LoadingSpinner Component', () => {
  test('renders spinner with default props', () => {
    render(<LoadingSpinner />)
    
    const spinner = screen.getByRole('status')
    expect(spinner).toBeInTheDocument()
    expect(spinner).toHaveClass('h-8 w-8')
    expect(spinner).toHaveClass('border-3')
    expect(spinner).toHaveClass('text-orange-500')
    expect(spinner).toHaveClass('animate-spin')
  })

  test('applies correct size classes', () => {
    const { rerender } = render(<LoadingSpinner size="sm" />)
    expect(screen.getByRole('status')).toHaveClass('h-4 w-4 border-2')

    rerender(<LoadingSpinner size="md" />)
    expect(screen.getByRole('status')).toHaveClass('h-8 w-8 border-3')

    rerender(<LoadingSpinner size="lg" />)
    expect(screen.getByRole('status')).toHaveClass('h-12 w-12 border-4')
  })

  test('applies custom color class', () => {
    render(<LoadingSpinner color="text-blue-500" />)
    expect(screen.getByRole('status')).toHaveClass('text-blue-500')
  })

  test('applies custom className', () => {
    render(<LoadingSpinner className="custom-class" />)
    expect(screen.getByRole('status').parentElement).toHaveClass('custom-class')
  })

  test('has accessible label', () => {
    render(<LoadingSpinner />)
    
    const status = screen.getByRole('status')
    expect(status).toHaveAttribute('aria-label', 'Загрузка...')
    
    const srOnly = screen.getByText('Загрузка...')
    expect(srOnly).toHaveClass('sr-only')
  })

  test('renders within parent container correctly', () => {
    const { container } = render(
      <div className="parent-container">
        <LoadingSpinner />
      </div>
    )
    
    const parent = container.firstChild
    const spinner = screen.getByRole('status')
    
    expect(parent).toContainElement(spinner)
    expect(spinner.parentElement).toHaveClass('flex items-center justify-center')
  })
})
