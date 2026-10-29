import { useQuery } from '@tanstack/react-query'
import { useEffect, useState } from 'react'
import { fetchCatalog } from './api'
import { FilterBar } from './components/FilterBar'
import { ProductDetails } from './components/ProductDetails'
import { parseFilters, serializeFilters, type Filters } from './filters'
import type { Focus } from './graph/buildGraph'
import { CatalogGraph } from './graph/CatalogGraph'
import { slugify } from './graph/logos'
import { MadeBy } from './components/MadeBy'
import { SubmitForm } from './submit/SubmitForm'

const isSubmitView = () => window.location.hash === '#submit'

export default function App() {
  const catalog = useQuery({ queryKey: ['catalog'], queryFn: fetchCatalog, staleTime: 60_000 })
  const [filters, setFilters] = useState<Filters>(() => parseFilters(window.location.search))
  const [focus, setFocus] = useState<Focus>(null)
  const [pendingProduct, setPendingProduct] = useState(() => new URLSearchParams(window.location.search).get('product'))

  // Open the product named in the page address once the catalog has loaded.
  useEffect(() => {
    if (!pendingProduct || !catalog.data) return
    const product = catalog.data.products.find((item) => slugify(item.full_name) === pendingProduct)
    if (product) setFocus({ kind: 'product', id: product.id })
    setPendingProduct(null)
  }, [pendingProduct, catalog.data])
  const [submitView, setSubmitView] = useState(isSubmitView)

  const selectedId = focus?.kind === 'product' ? focus.id : null
  const selected = catalog.data?.products.find((product) => product.id === selectedId) ?? null

  useEffect(() => {
    if (pendingProduct) return
    const params = new URLSearchParams(serializeFilters(filters))
    if (selected) params.set('product', slugify(selected.full_name))
    const search = params.toString()
    window.history.replaceState(null, '', `${window.location.pathname}${search ? `?${search}` : ''}${window.location.hash}`)
  }, [filters, selected, pendingProduct])

  useEffect(() => {
    const onHash = () => setSubmitView(isSubmitView())
    window.addEventListener('hashchange', onHash)
    return () => window.removeEventListener('hashchange', onHash)
  }, [])

  return (
    <div className="app">
      <header className="app-header">
        <div>
          <h1>Network Automation Product Catalog</h1>
          <p className="subtitle">Products mapped to the building blocks of the Network Automation Framework</p>
        </div>
        <nav>
          {submitView ? (
            <a className="button" href="#">
              ← Back to the catalog
            </a>
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
        <>
          <SubmitForm catalog={catalog.data} onDone={() => (window.location.hash = '')} />
          <div className="made-by-row">
            <MadeBy />
          </div>
        </>
      )}

      {catalog.data && !submitView && (
        <main>
          <FilterBar
            catalog={catalog.data}
            filters={filters}
            onChange={(next) => {
              setFilters(next)
              setFocus(null)
            }}
          />
          <p className="hint">
            Drag to move, scroll to zoom. Click a product or a building block to highlight its links. Solid lines
            are full coverage, dashed lines partial coverage.
          </p>
          <div className="graph-stage">
            <CatalogGraph catalog={catalog.data} filters={filters} focus={focus} onFocus={setFocus} />
            {selected && (
              <ProductDetails product={selected} requirements={catalog.data.requirements} onClose={() => setFocus(null)} />
            )}
          </div>
          <footer className="app-footer">
            <p className="footer-notes">
            Building blocks from the{' '}
            <a href="https://reference.networkautomation.forum/Framework/Framework/" target="_blank" rel="noopener noreferrer">
              Network Automation Framework
            </a>
            . Every fact links to its source.
            <br />
            Product names and logos are trademarks of their respective owners. They are used only to identify the
            products. Their use does not imply endorsement.
            </p>
            <MadeBy />
          </footer>
        </main>
      )}
    </div>
  )
}
