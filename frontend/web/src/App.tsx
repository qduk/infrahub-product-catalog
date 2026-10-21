import { useQuery } from '@tanstack/react-query'
import { useEffect, useMemo, useState } from 'react'
import { fetchCatalog } from './api'
import { Diagram } from './components/Diagram'
import { FilterBar } from './components/FilterBar'
import { ProductDetails } from './components/ProductDetails'
import { applyFilters, DEFAULT_FILTERS, parseFilters, serializeFilters, type Filters } from './filters'
import { SubmitForm } from './submit/SubmitForm'

const isSubmitView = () => window.location.hash === '#submit'

export default function App() {
  const catalog = useQuery({ queryKey: ['catalog'], queryFn: fetchCatalog, staleTime: 60_000 })
  const [filters, setFilters] = useState<Filters>(() => parseFilters(window.location.search))
  const [selectedId, setSelectedId] = useState<string | null>(null)
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

  const views = useMemo(() => (catalog.data ? applyFilters(catalog.data, filters) : []), [catalog.data, filters])
  const selected = catalog.data?.products.find((product) => product.id === selectedId) ?? null
  const filtered = serializeFilters({ ...filters, block: null }) !== serializeFilters({ ...DEFAULT_FILTERS })

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
          <FilterBar filters={filters} onChange={setFilters} />
          <div className="layout">
            <Diagram
              views={views}
              filtered={filtered}
              singleBlock={Boolean(filters.block)}
              onSelectProduct={setSelectedId}
              onShowOnly={(block) => setFilters({ ...filters, block })}
            />
            {selected && <ProductDetails product={selected} onClose={() => setSelectedId(null)} />}
          </div>
          <footer className="app-footer">
            Building blocks from the{' '}
            <a href="https://reference.networkautomation.forum/Framework/Framework/" target="_blank" rel="noopener noreferrer">
              Network Automation Framework
            </a>
            . Every fact links to its source.
          </footer>
        </main>
      )}
    </div>
  )
}
