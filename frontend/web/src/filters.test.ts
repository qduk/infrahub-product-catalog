import { describe, expect, it } from 'vitest'
import { countBlockProducts, DEFAULT_FILTERS, parseFilters, serializeFilters } from './filters'
import { sampleCatalog } from './graph/fixtures'

describe('filters', () => {



  it('reads and writes the page address', () => {
    const filters = { statuses: ['active', 'discontinued'] as const, extents: ['full'] as const, block: 'Intent' }
    const search = serializeFilters({ ...filters, statuses: [...filters.statuses], extents: [...filters.extents] })
    expect(search).toBe('status=active%2Cdiscontinued&extent=full&block=Intent')
    expect(parseFilters(search)).toEqual({ statuses: ['active', 'discontinued'], extents: ['full'], block: 'Intent' })
  })

  it('leaves default filters out of the page address', () => {
    expect(serializeFilters(DEFAULT_FILTERS)).toBe('')
    expect(parseFilters('')).toEqual(DEFAULT_FILTERS)
  })

  it('ignores unknown values in the page address', () => {
    expect(parseFilters('status=bogus&extent=nope')).toEqual(DEFAULT_FILTERS)
  })

  it('counts the products that cover a block with the selected statuses and extents', () => {
    expect(countBlockProducts(sampleCatalog, DEFAULT_FILTERS, 'Collector')).toBe(1)
    expect(countBlockProducts(sampleCatalog, { ...DEFAULT_FILTERS, statuses: ['active', 'discontinued'] }, 'Collector')).toBe(2)
    expect(countBlockProducts(sampleCatalog, { ...DEFAULT_FILTERS, extents: ['full'] }, 'Observability')).toBe(0)
  })
})
