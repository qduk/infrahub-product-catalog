import { cleanup, render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'
import type { Requirement } from '../api'
import { BlockDetails } from './BlockDetails'

afterEach(cleanup)

const requirement = (identifier: string, level: Requirement['level'], block: string | null, position: number): Requirement => ({
  identifier,
  level,
  position,
  summary: `Summary ${identifier}`,
  statement: `Statement ${identifier}`,
  reference_url: 'https://reference.networkautomation.forum/Framework/Framework/',
  block,
})

const requirements = [
  requirement('intent-must-2', 'must', 'Intent', 4),
  requirement('intent-must-1', 'must', 'Intent', 3),
  requirement('intent-should-1', 'should', 'Intent', 5),
  requirement('intent-may-1', 'may', 'Intent', 6),
  requirement('executor-must-1', 'must', 'Executor', 7),
  requirement('framework-should-1', 'should', null, 1),
]

const block = { name: 'Intent', description: 'Desired state.', definition_url: 'https://example.org/#intent' }

const renderDetails = (overrides: Partial<Parameters<typeof BlockDetails>[0]> = {}) =>
  render(
    <BlockDetails block={block} requirements={requirements} productCount={2} onShowProducts={() => {}} onClose={() => {}} {...overrides} />,
  )

const summaries = (label: string) =>
  within(screen.getByRole('list', { name: label }))
    .getAllByRole('listitem')
    .map((item) => item.querySelector('.requirement-summary')?.textContent)

describe('BlockDetails', () => {
  it("lists the block's MUST and SHOULD requirements in framework order, without MAY requirements", () => {
    renderDetails()
    expect(summaries('MUST requirements of Intent')).toEqual(['Summary intent-must-1', 'Summary intent-must-2'])
    expect(summaries('SHOULD requirements of Intent')).toEqual(['Summary intent-should-1'])
    expect(screen.queryByText('Summary intent-may-1')).toBeNull()
    expect(screen.queryByText('Summary executor-must-1')).toBeNull()
  })

  it('shows the requirements for every block only when asked', async () => {
    renderDetails()
    expect(screen.queryByText('Summary framework-should-1')).toBeNull()
    await userEvent.click(screen.getByRole('button', { name: /for every building block/ }))
    expect(summaries('Requirements for every building block')).toEqual(['Summary framework-should-1'])
  })

  it('opens the products of the block and closes', async () => {
    const onShowProducts = vi.fn()
    const onClose = vi.fn()
    renderDetails({ onShowProducts, onClose })
    await userEvent.click(screen.getByRole('button', { name: 'View the 2 products that cover Intent' }))
    await userEvent.click(screen.getByRole('button', { name: 'Close details' }))
    expect(onShowProducts).toHaveBeenCalledOnce()
    expect(onClose).toHaveBeenCalledOnce()
  })
})
