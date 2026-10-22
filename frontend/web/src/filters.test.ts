import { describe, expect, it } from 'vitest'
import { DEFAULT_FILTERS, parseFilters, serializeFilters } from './filters'

describe('filters', () => {



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
