import { render } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { Logo } from './Logo'

describe('Logo', () => {
  it('shows the initials of the product name, not the publisher, when no logo is on file', () => {
    const { container } = render(<Logo fullName="Example Test Publisher Submission Test Tool" name="Submission Test Tool" />)
    expect(container.textContent).toBe('ST')
    expect(container.querySelector('img')).toBeNull()
  })

  it('shows the logo on file, looked up by full name', () => {
    const { container } = render(<Logo fullName="OpsMill Infrahub" name="Infrahub" />)
    expect(container.querySelector('img')).not.toBeNull()
  })
})
