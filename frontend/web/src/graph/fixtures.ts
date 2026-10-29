import type { Catalog, Extent, Product, Status } from '../api'

export function product(id: string, status: Status, claims: [string, Extent][]): Product {
  return {
    id,
    name: id,
    full_name: `Publisher ${id}`,
    publisher: 'Publisher',
    description: '',
    homepage_url: 'https://example.org/',
    license_model: null,
    status,
    status_date: null,
    sources: { publisher: [], description: [], license_model: [], status: [] },
    claims: claims.map(([block, extent]) => ({ block, extent, assessed: true, note: null, sources: [], verdicts: [] })),
  }
}

const block = (name: string) => ({ name, description: '', definition_url: '' })

export const SIX_BLOCKS = ['Presentation', 'Observability', 'Orchestrator', 'Intent', 'Collector', 'Executor'].map(block)

export const sampleCatalog: Catalog = {
  blocks: SIX_BLOCKS,
  publishers: [],
  requirements: [],
  products: [
    product('a', 'active', [['Collector', 'full'], ['Observability', 'partial']]),
    product('b', 'discontinued', [['Collector', 'partial']]),
    product('c', 'active', [['Intent', 'full']]),
    product('d', 'active', []),
  ],
}
