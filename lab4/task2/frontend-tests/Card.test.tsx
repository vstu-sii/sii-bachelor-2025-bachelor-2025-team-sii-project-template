import React from 'react'
import { render, screen } from '@testing-library/react'
import Card from '@/components/ui/Card'

describe('Card Component', () => {
  test('renders children correctly', () => {
    render(
      <Card>
        <div data-testid="child">Card Content</div>
      </Card>
    )
    
    expect(screen.getByTestId('child')).toBeInTheDocument()
    expect(screen.getByText('Card Content')).toBeInTheDocument()
  })

  test('applies default classes', () => {
    const { container } = render(<Card>Content</Card>)
    const card = container.firstChild
    
    expect(card).toHaveClass('bg-white')
    expect(card).toHaveClass('rounded-xl')
    expect(card).toHaveClass('shadow-sm')
    expect(card).toHaveClass('border')
    expect(card).toHaveClass('border-gray-200')
    expect(card).toHaveClass('p-6')
  })

  test('applies custom className', () => {
    const { container } = render(
      <Card className="custom-class">Content</Card>
    )
    
    expect(container.firstChild).toHaveClass('custom-class')
  })

  test('applies hover class when hover prop is true', () => {
    const { container } = render(<Card hover>Content</Card>)
    
    expect(container.firstChild).toHaveClass('hover:shadow-lg')
    expect(container.firstChild).toHaveClass('transition-shadow')
  })

  test('does not apply hover class when hover prop is false', () => {
    const { container } = render(<Card hover={false}>Content</Card>)
    
    expect(container.firstChild).not.toHaveClass('hover:shadow-lg')
  })

  test('applies correct padding classes', () => {
    const { rerender, container } = render(<Card padding="none">Content</Card>)
    expect(container.firstChild).toHaveClass('p-0')

    rerender(<Card padding="sm">Content</Card>)
    expect(container.firstChild).toHaveClass('p-3')

    rerender(<Card padding="md">Content</Card>)
    expect(container.firstChild).toHaveClass('p-6')

    rerender(<Card padding="lg">Content</Card>)
    expect(container.firstChild).toHaveClass('p-8')
  })

  test('renders with different content types', () => {
    const { rerender } = render(
      <Card>
        <button>Button inside card</button>
      </Card>
    )
    expect(screen.getByRole('button')).toBeInTheDocument()

    rerender(
      <Card>
        <input type="text" placeholder="Input inside card" />
      </Card>
    )
    expect(screen.getByPlaceholderText('Input inside card')).toBeInTheDocument()

    rerender(
      <Card>
        <h1>Heading</h1>
        <p>Paragraph</p>
        <ul>
          <li>List item</li>
        </ul>
      </Card>
    )
    expect(screen.getByRole('heading')).toBeInTheDocument()
    expect(screen.getByText('Paragraph')).toBeInTheDocument()
    expect(screen.getByText('List item')).toBeInTheDocument()
  })
})
