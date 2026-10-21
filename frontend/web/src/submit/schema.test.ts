import { describe, expect, it } from 'vitest'
import { emptyForm, submissionSchema, toPayload, type SubmissionForm } from './schema'

function validForm(): SubmissionForm {
  const form = emptyForm()
  form.product = {
    name: 'Example Tool',
    description: 'Collects interface counters.',
    homepage_url: 'https://example.org/tool',
    license_model: 'open_source',
    status: 'active',
    status_date: '',
  }
  form.publisherMode = 'new'
  form.publisherNew = { name: 'Example Corp', homepage_url: 'https://example.org/' }
  form.sources = [
    { key: 's1', title: 'Docs', url: 'https://example.org/docs' },
    { key: 's2', title: 'License', url: 'https://example.org/license' },
  ]
  form.factSources = { publisher: ['s1'], description: ['s1'], license_model: ['s2'], status: [] }
  form.claims = [{ block: 'Collector', extent: 'full', note: '', sources: ['s1'] }]
  return form
}

const issuePaths = (form: SubmissionForm) => {
  const result = submissionSchema.safeParse(form)
  return result.success ? [] : result.error.issues.map((issue) => issue.path.join('.'))
}

describe('submission form rules', () => {
  it('accepts a complete form', () => {
    expect(issuePaths(validForm())).toEqual([])
  })

  it('requires a license model source when a license model is set', () => {
    const form = validForm()
    form.factSources.license_model = []
    expect(issuePaths(form)).toContain('factSources.license_model')
  })

  it('requires a status source when the status is not active', () => {
    const form = validForm()
    form.product.status = 'discontinued'
    expect(issuePaths(form)).toContain('factSources.status')
  })

  it('allows only one claim per building block', () => {
    const form = validForm()
    form.claims.push({ block: 'Collector', extent: 'partial', note: '', sources: ['s1'] })
    expect(issuePaths(form)).toContain('claims.1.block')
  })

  it('requires sources for the publisher, the description and each claim', () => {
    const form = validForm()
    form.factSources.publisher = []
    form.factSources.description = []
    form.claims[0].sources = []
    expect(issuePaths(form)).toEqual(
      expect.arrayContaining(['factSources.publisher', 'factSources.description', 'claims.0.sources']),
    )
  })

  it('accepts only http and https links', () => {
    const form = validForm()
    form.sources[0].url = 'javascript:alert(1)'
    expect(issuePaths(form)).toContain('sources.0.url')
  })

  it('limits field sizes', () => {
    const form = validForm()
    form.product.name = 'x'.repeat(101)
    form.product.description = 'x'.repeat(1001)
    expect(issuePaths(form)).toEqual(expect.arrayContaining(['product.name', 'product.description']))
  })

  it('requires an existing publisher when that option is chosen', () => {
    const form = validForm()
    form.publisherMode = 'existing'
    form.publisherExisting = ''
    expect(issuePaths(form)).toContain('publisherExisting')
  })

  it('builds the service payload', () => {
    const payload = toPayload(validForm())
    expect(payload.publisher).toEqual({ new: { name: 'Example Corp', homepage_url: 'https://example.org/' } })
    expect(payload.product.license_model).toBe('open_source')
    expect(payload.product.status_date).toBeNull()
    expect(payload.claims[0].note).toBeNull()
  })
})
