import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'
import type { Catalog } from '../api'
import { SubmitForm } from './SubmitForm'

const catalog: Catalog = {
  blocks: [
    { name: 'Collector', description: '', definition_url: '' },
    { name: 'Intent', description: '', definition_url: '' },
  ],
  publishers: [{ name: 'OpsMill', homepage_url: 'https://opsmill.com/' }],
  products: [],
}

afterEach(() => vi.restoreAllMocks())

describe('SubmitForm', () => {
  it('sends the filled-in product to the service', async () => {
    const fetchMock = vi.fn(async () => new Response(JSON.stringify({ reference: 'submission-test' }), { status: 201 }))
    vi.stubGlobal('fetch', fetchMock)
    const user = userEvent.setup()
    render(<SubmitForm catalog={catalog} onDone={() => {}} />)

    await user.type(screen.getByPlaceholderText('e.g. NetBox'), 'Example Tool')
    await user.type(screen.getAllByPlaceholderText('https://')[0], 'https://example.org/tool')
    await user.type(screen.getByLabelText('What the product does, in neutral words'), 'Collects device state.')
    await user.selectOptions(screen.getByLabelText('Publisher', { selector: 'select' }), 'OpsMill')
    await user.type(screen.getByLabelText('Source title'), 'Docs')
    await user.type(screen.getByLabelText('Source link'), 'https://example.org/docs')
    for (const chip of screen.getAllByRole('button', { name: 'Docs' })) await user.click(chip)
    await user.selectOptions(screen.getByLabelText('Building block'), 'Collector')
    await user.click(screen.getByRole('button', { name: 'Submit for review' }))

    await waitFor(() => expect(screen.getByText(/submission-test/)).toBeTruthy())
    const body = JSON.parse((fetchMock.mock.calls[0] as unknown as [string, RequestInit])[1].body as string)
    expect(body.product).toMatchObject({ name: 'Example Tool', homepage_url: 'https://example.org/tool', status: 'active' })
    expect(body.publisher).toEqual({ existing: 'OpsMill' })
    expect(body.sources).toHaveLength(1)
    const key = body.sources[0].key
    expect(body.fact_sources.publisher).toEqual([key])
    expect(body.fact_sources.description).toEqual([key])
    expect(body.claims).toEqual([{ block: 'Collector', note: null, sources: [key] }])
    expect(screen.queryByText('Partial')).toBeNull()
  })

  it('shows errors and sends nothing when required facts are missing', async () => {
    const fetchMock = vi.fn()
    vi.stubGlobal('fetch', fetchMock)
    const user = userEvent.setup()
    render(<SubmitForm catalog={catalog} onDone={() => {}} />)
    await user.click(screen.getByRole('button', { name: 'Submit for review' }))
    expect(await screen.findByText('Enter the product name.')).toBeTruthy()
    expect(fetchMock).not.toHaveBeenCalled()
  })
})
