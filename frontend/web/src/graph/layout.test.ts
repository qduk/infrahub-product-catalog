import { describe, expect, it } from 'vitest'
import { BLOCK_SIZE, PRODUCT_SIZE, layoutGraph } from './layout'

const overlap = (a: { x: number; y: number }, b: { x: number; y: number }) =>
  Math.abs(a.x - b.x) < PRODUCT_SIZE.width && Math.abs(a.y - b.y) < PRODUCT_SIZE.height

describe('layoutGraph', () => {
  const blocks = ['Presentation', 'Observability', 'Orchestrator', 'Intent', 'Collector', 'Executor']

  it('places blocks in the framework arrangement', () => {
    const { blocks: positions } = layoutGraph(blocks, [])
    expect(positions.Presentation.y).toBeLessThan(positions.Orchestrator.y)
    expect(positions.Observability.y).toBe(positions.Orchestrator.y)
    expect(positions.Observability.x).toBeLessThan(positions.Orchestrator.x)
    expect(positions.Intent.x).toBeGreaterThan(positions.Orchestrator.x)
    expect(positions.Collector.y).toBeGreaterThan(positions.Orchestrator.y)
    expect(positions.Collector.x).toBeLessThan(positions.Executor.x)
  })

  it('puts unknown blocks in an extra row', () => {
    const { blocks: positions } = layoutGraph([...blocks, 'Something new'], [])
    expect(positions['Something new'].y).toBeGreaterThan(positions.Executor.y)
  })

  it('keeps product nodes apart from each other and from blocks', () => {
    const products = Array.from({ length: 40 }, (_, index) => ({
      id: `p${index}`,
      blocks: [blocks[index % 6], ...(index % 5 === 0 ? [blocks[(index + 2) % 6]] : [])],
    }))
    const { blocks: blockPositions, products: positions } = layoutGraph(blocks, products)
    const list = Object.values(positions)
    for (let i = 0; i < list.length; i++) {
      for (let j = i + 1; j < list.length; j++) expect(overlap(list[i], list[j])).toBe(false)
      for (const block of Object.values(blockPositions)) {
        const hits =
          Math.abs(list[i].x - block.x) < (PRODUCT_SIZE.width + BLOCK_SIZE.width) / 2 &&
          Math.abs(list[i].y - block.y) < (PRODUCT_SIZE.height + BLOCK_SIZE.height) / 2
        expect(hits).toBe(false)
      }
    }
  })

  it('places a product with two blocks between them', () => {
    const { blocks: positions, products } = layoutGraph(blocks, [{ id: 'x', blocks: ['Collector', 'Executor'] }])
    expect(products.x.x).toBeGreaterThan(positions.Collector.x)
    expect(products.x.x).toBeLessThan(positions.Executor.x)
  })

  it('gives the same positions for the same input', () => {
    const products = [{ id: 'a', blocks: ['Intent'] }, { id: 'b', blocks: ['Intent', 'Orchestrator'] }]
    expect(layoutGraph(blocks, products)).toEqual(layoutGraph(blocks, products))
  })
})
