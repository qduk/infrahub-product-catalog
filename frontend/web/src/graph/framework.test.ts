import { describe, expect, it } from 'vitest'
import { frameworkLayout } from './framework'

const blocks = ['Intent', 'Observability', 'Orchestrator', 'Executor', 'Collector', 'Presentation']

describe('frameworkLayout', () => {
  it('arranges the blocks as the framework diagram does', () => {
    const { blocks: boxes, infrastructure } = frameworkLayout(blocks)
    expect(boxes.Presentation.y).toBeLessThan(boxes.Orchestrator.y)
    expect(boxes.Observability.y).toBe(boxes.Orchestrator.y)
    expect(boxes.Intent.y).toBe(boxes.Orchestrator.y)
    expect(boxes.Observability.x).toBeLessThan(boxes.Orchestrator.x)
    expect(boxes.Orchestrator.x).toBeLessThan(boxes.Intent.x)
    expect(boxes.Collector.y).toBeGreaterThan(boxes.Orchestrator.y)
    expect(boxes.Collector.x).toBeLessThan(boxes.Executor.x)
    expect(boxes.Collector.x).toBeGreaterThan(boxes.Observability.x)
    expect(infrastructure.y).toBeGreaterThan(boxes.Executor.y)
  })

  it('puts a block that is not in the diagram in an extra row above the infrastructure', () => {
    const { blocks: boxes, infrastructure } = frameworkLayout([...blocks, 'Something new'])
    expect(boxes['Something new'].y).toBeGreaterThan(boxes.Executor.y)
    expect(infrastructure.y).toBeGreaterThan(boxes['Something new'].y)
  })

  it('keeps the boxes apart', () => {
    const list = Object.values(frameworkLayout(blocks).blocks)
    for (let i = 0; i < list.length; i++) {
      for (let j = i + 1; j < list.length; j++) {
        const [a, b] = [list[i], list[j]]
        const apart = a.x + a.width <= b.x || b.x + b.width <= a.x || a.y + a.height <= b.y || b.y + b.height <= a.y
        expect(apart).toBe(true)
      }
    }
  })
})
