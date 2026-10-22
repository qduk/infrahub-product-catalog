import { BaseEdge, getBezierPath, Handle, Position, type EdgeProps, type NodeProps } from '@xyflow/react'
import type { CSSProperties } from 'react'
import { STATUS_LABELS } from '../api'
import { blockStyle } from './blockStyle'
import type { BlockNode as BlockNodeType, CoverageEdge, ProductNode as ProductNodeType } from './buildGraph'
import { Logo } from './Logo'

// Edges attach to the centre of each node, so lines can arrive from any side.
const centreHandles = (
  <>
    <Handle type="target" position={Position.Top} className="centre-handle" isConnectable={false} />
    <Handle type="source" position={Position.Top} className="centre-handle" isConnectable={false} />
  </>
)

export function BlockNode({ data }: NodeProps<BlockNodeType>) {
  const style = blockStyle(data.name)
  return (
    <div className={`graph-block${data.faded ? ' faded' : ''}`} style={{ '--block-color': style.color } as CSSProperties}>
      {centreHandles}
      <div className="graph-block-name">{data.name}</div>
      {style.tagline && <div className="graph-block-tagline">{style.tagline}</div>}
    </div>
  )
}

export function ProductNode({ data }: NodeProps<ProductNodeType>) {
  const { product } = data
  return (
    <div
      className={`graph-product status-${product.status}${data.faded ? ' faded' : ''}`}
      title={product.full_name}
    >
      {centreHandles}
      <Logo fullName={product.full_name} />
      <span className="graph-product-text">
        <span className="graph-product-name">{product.name}</span>
        {product.status !== 'active' && <span className="graph-product-status">{STATUS_LABELS[product.status]}</span>}
      </span>
    </div>
  )
}

export function CoverageEdgeView({ sourceX, sourceY, targetX, targetY, data }: EdgeProps<CoverageEdge>) {
  const [path] = getBezierPath({ sourceX, sourceY, targetX, targetY })
  const color = blockStyle(data?.block ?? '').color
  return (
    <BaseEdge
      path={path}
      style={{
        stroke: color,
        strokeWidth: data?.extent === 'full' ? 2.2 : 1.6,
        strokeDasharray: data?.extent === 'partial' ? '6 5' : undefined,
        opacity: data?.faded ? 0.08 : 0.75,
      }}
    />
  )
}

export const nodeTypes = { block: BlockNode, product: ProductNode }
export const edgeTypes = { coverage: CoverageEdgeView }
