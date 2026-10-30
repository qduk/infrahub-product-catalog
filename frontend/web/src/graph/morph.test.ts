import { describe, expect, it } from 'vitest'
import { DEFAULT_FILTERS } from '../filters'
import { buildGraph } from './buildGraph'
import { sampleCatalog } from './fixtures'
import { frameworkLayout } from './framework'
import { INFRASTRUCTURE_ID, morphGraph } from './morph'

const graph = buildGraph(sampleCatalog, DEFAULT_FILTERS, null)
const diagram = frameworkLayout(sampleCatalog.blocks.map((block) => block.name))
const options = { counts: { Intent: 1 }, selectedBlock: 'Intent' }
const node = (nodes: { id: string }[], id: string) => nodes.find((item) => item.id === id)!

describe('morphGraph', () => {
  it('leaves the graph unchanged at the start', () => {
    expect(morphGraph(graph, diagram, 0, options).nodes).toBe(graph.nodes)
  })

  it('puts every block in the diagram at the end and hides the products and lines', () => {
    const { nodes, edges } = morphGraph(graph, diagram, 1, options)
    const intent = node(nodes, 'block:Intent') as (typeof nodes)[number] & { data: { count: number; selected: boolean } }
    expect(intent.position).toEqual({ x: diagram.blocks.Intent.x, y: diagram.blocks.Intent.y })
    expect(intent.width).toBe(diagram.blocks.Intent.width)
    expect(intent.data).toMatchObject({ count: 1, selected: true, morph: 1 })
    expect(nodes.filter((item) => item.type === 'product').every((item) => item.hidden)).toBe(true)
    expect(edges.every((edge) => edge.hidden)).toBe(true)
    expect(node(nodes, INFRASTRUCTURE_ID).hidden).toBe(false)
  })

  it('moves blocks part of the way, with products fading out', () => {
    const start = node(graph.nodes, 'block:Intent')!.position
    const { nodes, edges } = morphGraph(graph, diagram, 0.25, options)
    const position = node(nodes, 'block:Intent').position as { x: number; y: number }
    expect(position.x).toBeCloseTo(start.x + (diagram.blocks.Intent.x - start.x) * 0.25)
    expect(node(nodes, 'a')).toMatchObject({ hidden: false, style: { opacity: 0.5 } })
    expect(edges[0].data?.visibility).toBe(0.5)
    expect(node(nodes, INFRASTRUCTURE_ID).hidden).toBe(true)
  })

  it('fades in, where the diagram puts them, blocks the block filter hides', () => {
    const single = buildGraph(sampleCatalog, { ...DEFAULT_FILTERS, block: 'Collector' }, null)
    expect(node(morphGraph(single, diagram, 0.5, options).nodes, 'block:Intent')).toMatchObject({
      position: { x: diagram.blocks.Intent.x, y: diagram.blocks.Intent.y },
      style: { opacity: 0.5 },
    })
  })
})
