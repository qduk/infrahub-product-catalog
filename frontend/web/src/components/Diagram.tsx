import type { BlockView } from '../filters'
import { Block } from './Block'
import { BLOCK_LAYOUT } from './layout'

interface Props {
  views: BlockView[]
  filtered: boolean
  singleBlock: boolean
  onSelectProduct: (productId: string) => void
  onShowOnly: (block: string) => void
}

export function Diagram({ views, filtered, singleBlock, onSelectProduct, onShowOnly }: Props) {
  const known = views.filter((view) => BLOCK_LAYOUT[view.block.name])
  const other = views.filter((view) => !BLOCK_LAYOUT[view.block.name])
  return (
    <div className={singleBlock ? 'diagram diagram-single' : 'diagram'}>
      {known.map((view) => (
        <Block key={view.block.name} view={view} filtered={filtered} onSelectProduct={onSelectProduct} onShowOnly={onShowOnly} />
      ))}
      {other.map((view) => (
        <Block key={view.block.name} view={view} filtered={filtered} onSelectProduct={onSelectProduct} onShowOnly={onShowOnly} />
      ))}
      {!singleBlock && (
        <div className="infrastructure" aria-label="Infrastructure">
          <strong>Infrastructure</strong>
          <span>Routers · Switches · Firewalls · Load balancers · SD-WAN · Cloud fabric · Compute</span>
        </div>
      )}
    </div>
  )
}
