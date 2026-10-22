import { useQuery } from '@tanstack/react-query'
import { useEffect, useState } from 'react'
import { fetchCatalog } from './api'
import { FilterBar } from './components/FilterBar'
import { ProductDetails } from './components/ProductDetails'
import { parseFilters, serializeFilters, type Filters } from './filters'
import type { Focus } from './graph/buildGraph'
import { CatalogGraph } from './graph/CatalogGraph'
import { SubmitForm } from './submit/SubmitForm'

const isSubmitView = () => window.location.hash === '#submit'

export default function App() {
  const catalog = useQuery({ queryKey: ['catalog'], queryFn: fetchCatalog, staleTime: 60_000 })
  const [filters, setFilters] = useState<Filters>(() => parseFilters(window.location.search))
  const [focus, setFocus] = useState<Focus>(null)
  const [submitView, setSubmitView] = useState(isSubmitView)

  useEffect(() => {
    const search = serializeFilters(filters)
    const url = `${window.location.pathname}${search ? `?${search}` : ''}${window.location.hash}`
    window.history.replaceState(null, '', url)
  }, [filters])

  useEffect(() => {
    const onHash = () => setSubmitView(isSubmitView())
    window.addEventListener('hashchange', onHash)
    return () => window.removeEventListener('hashchange', onHash)
  }, [])

  const selectedId = focus?.kind === 'product' ? focus.id : null
  const selected = catalog.data?.products.find((product) => product.id === selectedId) ?? null

  return (
    <div className="app">
      <header className="app-header">
        <div>
          <h1>Network Automation Product Catalog</h1>
          <p className="subtitle">Products mapped to the building blocks of the Network Automation Framework</p>
        </div>
        <nav>
          {submitView ? (
            <a href="#">Back to the catalog</a>
          ) : (
            <a className="button" href="#submit">
              Submit a product
            </a>
          )}
        </nav>
      </header>

      {catalog.isPending && <p className="notice">Loading the catalog…</p>}
      {catalog.isError && (
        <p className="notice notice-error" role="alert">
          The catalog is not available right now. Try again later.
        </p>
      )}

      {catalog.data && submitView && (
        <SubmitForm catalog={catalog.data} onDone={() => (window.location.hash = '')} />
      )}

      {catalog.data && !submitView && (
        <main>
          <FilterBar
            filters={filters}
            blocks={catalog.data.blocks.map((block) => block.name)}
            onChange={(next) => {
              setFilters(next)
              setFocus(null)
            }}
          />
          <p className="hint">
            Drag to move, scroll to zoom. Click a product or a building block to highlight its links. Solid lines
            are full coverage, dashed lines partial coverage.
          </p>
          <div className="layout">
            <CatalogGraph catalog={catalog.data} filters={filters} focus={focus} onFocus={setFocus} />
            {selected && <ProductDetails product={selected} onClose={() => setFocus(null)} />}
          </div>
          <footer className="app-footer">
            Building blocks from the{' '}
            <a href="https://reference.networkautomation.forum/Framework/Framework/" target="_blank" rel="noopener noreferrer">
              Network Automation Framework
            </a>
            . Every fact links to its source.
            <br />
            Product names and logos are trademarks of their respective owners. They are used only to identify the
            products. Their use does not imply endorsement.
          </footer>
        </main>
      )}
    </div>
  )
}
