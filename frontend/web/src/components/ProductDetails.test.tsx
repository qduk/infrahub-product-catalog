import { render } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import type { Product } from '../api'
import { ProductDetails } from './ProductDetails'

const hostile = '<script>alert("x")</script><img src=x onerror=alert(1)>'

const product: Product = {
  id: 'p1',
  name: hostile,
  full_name: `Example ${hostile}`,
  publisher: 'Example',
  description: hostile,
  homepage_url: 'https://example.org/',
  license_model: null,
  status: 'active',
  status_date: null,
  sources: { publisher: [{ title: hostile, url: 'https://example.org/a' }], description: [], license_model: [], status: [] },
  claims: [{ block: 'Intent', extent: 'full', note: hostile, sources: [] }],
}

describe('ProductDetails', () => {
  it('shows submitted text as plain text, never as markup', () => {
    const { container } = render(<ProductDetails product={product} onClose={() => {}} />)
    expect(container.querySelector('script')).toBeNull()
    expect(container.querySelector('img')).toBeNull()
    expect(container.textContent).toContain('<script>alert("x")</script>')
  })
})
