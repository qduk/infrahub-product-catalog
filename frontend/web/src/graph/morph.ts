// Blends the product graph into the framework diagram. At progress 0 the graph is unchanged; at 1 the
// blocks sit in the diagram and the products and lines are hidden. Products and lines fade out in the
// first half, so the blocks move without them.

import type { BlockNode, CoverageEdge, GraphNode, InfrastructureNode } from './buildGraph'
import { blockNodeId } from './buildGraph'
import type { Box } from './framework'

export const INFRASTRUCTURE_ID = 'infrastructure'

const lerp = (from: number, to: number, t: number) => from + (to - from) * t
const clamp = (value: number) => Math.min(1, Math.max(0, value))

export function graphBounds(nodes: GraphNode[]): Box {
  if (!nodes.length) return { x: 0, y: 0, width: 1, height: 1 }
  const left = Math.min(...nodes.map((node) => node.position.x))
  const top = Math.min(...nodes.map((node) => node.position.y))
  const right = Math.max(...nodes.map((node) => node.position.x + (node.width ?? 0)))
  const bottom = Math.max(...nodes.map((node) => node.position.y + (node.height ?? 0)))
  return { x: left, y: top, width: right - left, height: bottom - top }
}

interface Framework {
  blocks: Record<string, Box>
  infrastructure: Box
}

interface Options {
  counts: Record<string, number>
  selectedBlock: string | null
}

export function morphGraph(
  graph: { nodes: GraphNode[]; edges: CoverageEdge[] },
  framework: Framework,
  progress: number,
  { counts, selectedBlock }: Options,
) {
  const linkVisibility = clamp(1 - progress * 2)
  const inFramework = progress >= 1

  const graphBlocks = new Map(
    graph.nodes.filter((node): node is BlockNode => node.type === 'block').map((node) => [node.data.name, node]),
  )

  // Every block of the diagram. A block hidden by the block filter fades in where the diagram puts it.
  const blocks = Object.entries(framework.blocks).map(([name, box]): BlockNode => {
    const from = graphBlocks.get(name)
    const start = from
      ? { x: from.position.x, y: from.position.y, width: from.width ?? box.width, height: from.height ?? box.height }
      : box
    return {
      id: blockNodeId(name),
      type: 'block',
      position: { x: lerp(start.x, box.x, progress), y: lerp(start.y, box.y, progress) },
      width: lerp(start.width, box.width, progress),
      height: lerp(start.height, box.height, progress),
      draggable: false,
      hidden: !from && progress === 0,
      style: from ? undefined : { opacity: progress },
      data: {
        name,
        faded: progress === 0 ? (from?.data.faded ?? false) : false,
        morph: progress,
        count: counts[name] ?? 0,
        selected: inFramework && selectedBlock === name,
      },
    }
  })

  const products = graph.nodes
    .filter((node) => node.type === 'product')
    .map((node) => ({ ...node, hidden: linkVisibility === 0, style: { opacity: linkVisibility } }))

  const infrastructure: InfrastructureNode = {
    id: INFRASTRUCTURE_ID,
    type: 'infrastructure',
    position: { x: framework.infrastructure.x, y: framework.infrastructure.y },
    width: framework.infrastructure.width,
    height: framework.infrastructure.height,
    draggable: false,
    selectable: false,
    hidden: progress <= 0.5,
    style: { opacity: clamp(progress * 2 - 1) },
    data: {},
  }

  const edges = graph.edges.map((edge) => ({
    ...edge,
    hidden: linkVisibility === 0,
    data: edge.data && { ...edge.data, visibility: linkVisibility },
  }))

  const nodes: GraphNode[] = progress === 0 ? graph.nodes : [...products, ...blocks, infrastructure]
  return { nodes, edges }
}
