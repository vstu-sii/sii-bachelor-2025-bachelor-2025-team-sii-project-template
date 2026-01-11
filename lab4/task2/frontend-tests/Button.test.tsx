import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import Button from '@/components/ui/Button'
import { Loader2 } from 'lucide-react'

describe('Button Component', () => {
  test('renders button with children', () => {
    render(<Button>Click me</Button>)
    expect(screen.getByText('Click me')).toBeInTheDocument()
  })

  test('handles click events', () => {
    const handleClick = jest.fn()
    render(<Button onClick={handleClick}>Click me</Button>)
    
    fireEvent.click(screen.getByText('Click me'))
    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  test('shows loading state', () => {
    render(<Button isLoading>Click me</Button>)
    
    expect(screen.getByRole('button')).toBeDisabled()
    expect(screen.getByRole('status')).toBeInTheDocument()
  })

  test('disables button when disabled prop is true', () => {
    render(<Button disabled>Click me</Button>)
    
    expect(screen.getByRole('button')).toBeDisabled()
  })

  test('renders with icon', () => {
    const { container } = render(
      <Button icon={<span data-testid="icon">🔍</span>}>
        Search
      </Button>
    )
    
    expect(screen.getByTestId('icon')).toBeInTheDocument()
  })

  test('applies correct variant classes', () => {
    const { rerender } = render(<Button variant="primary">Button</Button>)
    expect(screen.getByRole('button')).toHaveClass('bg-gradient-to-r from-orange-500 to-yellow-500')

    rerender(<Button variant="outline">Button</Button>)
    expect(screen.getByRole('button')).toHaveClass('border border-gray-300')

    rerender(<Button variant="danger">Button</Button>)
    expect(screen.getByRole('button')).toHaveClass('bg-red-500')
  })

  test('applies correct size classes', () => {
    const { rerender } = render(<Button size="sm">Button</Button>)
    expect(screen.getByRole('button')).toHaveClass('px-3 py-1.5')

    rerender(<Button size="lg">Button</Button>)
    expect(screen.getByRole('button')).toHaveClass('px-6 py-3')
  })

  test('applies fullWidth class', () => {
    render(<Button fullWidth>Button</Button>)
    expect(screen.getByRole('button')).toHaveClass('w-full')
  })

  test('passes additional props', () => {
    render(
      <Button data-testid="custom-button" aria-label="Custom label">
        Button
      </Button>
    )
    
    expect(screen.getByTestId('custom-button')).toBeInTheDocument()
    expect(screen.getByLabelText('Custom label')).toBeInTheDocument()
  })
})
