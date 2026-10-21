import { describe, expect, it } from 'vitest'
import type { Catalog } from './api'
import { DEFAULT_FILTERS, applyFilters, parseFilters, serializeFilters } from './filters'

const catalog: Catalog = {
  blocks: [
    { name: 'Collector', description: '', definition_url: '' },
    { name: 'Intent', description: '', definition_url: '' },
  ],
  publishers: [],
  products: [
    product('a', 'active', [['Collector', 'full'], ['Intent', 'partial']]),
    product('b', 'discontinued', [['Collector', 'partial']]),
    product('c', 'acquired', [['Intent', 'full']]),
  ],
}

function product(id: string, status: 'active' | 'discontinued' | 'acquired', claims: [string, 'full' | 'partial'][]) {
  return {
    id,
    name: id,
    full_name: `Publisher ${id}`,
    publisher: 'Publisher',
    description: '',
    homepage_url: '',
    license_model: null,
    status,
    status_date: null,
    sources: { publisher: [], description: [], license_model: [], status: [] },
    claims: claims.map(([block, extent]) => ({ block, extent, note: null, sources: [] })),
  }
}

const ids = (view: ReturnType<typeof applyFilters>, block: string) =>
  (view.find((entry) => entry.block.name === block)?.entries ?? []).map((entry) => entry.product.id)

describe('filters', () => {
  it('shows active products, both extents and all blocks by default', () => {
    const view = applyFilters(catalog, DEFAULT_FILTERS)
    expect(view.map((entry) => entry.block.name)).toEqual(['Collector', 'Intent'])
    expect(ids(view, 'Collector')).toEqual(['a'])
    expect(ids(view, 'Intent')).toEqual(['a'])
  })

  it('combines status and extent', () => {
    const view = applyFilters(catalog, { statuses: ['active', 'discontinued'], extents: ['partial'], block: null })
    expect(ids(view, 'Collector')).toEqual(['b'])
    expect(ids(view, 'Intent')).toEqual(['a'])
  })

  it('shows a single block', () => {
    const view = applyFilters(catalog, { ...DEFAULT_FILTERS, statuses: ['acquired'], block: 'Intent' })
    expect(view.map((entry) => entry.block.name)).toEqual(['Intent'])
    expect(ids(view, 'Intent')).toEqual(['c'])
  })

  it('reads and writes the page address', () => {
    const filters = { statuses: ['active', 'acquired'] as const, extents: ['full'] as const, block: 'Intent' }
    const search = serializeFilters({ ...filters, statuses: [...filters.statuses], extents: [...filters.extents] })
    expect(search).toBe('status=active%2Cacquired&extent=full&block=Intent')
    expect(parseFilters(search)).toEqual({ statuses: ['active', 'acquired'], extents: ['full'], block: 'Intent' })
  })

  it('leaves default filters out of the page address', () => {
    expect(serializeFilters(DEFAULT_FILTERS)).toBe('')
    expect(parseFilters('')).toEqual(DEFAULT_FILTERS)
  })

  it('ignores unknown values in the page address', () => {
    expect(parseFilters('status=bogus&extent=nope')).toEqual(DEFAULT_FILTERS)
  })
})
