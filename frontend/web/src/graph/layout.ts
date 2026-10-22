// Positions for the graph. Blocks sit where the Network Automation Framework diagram puts them;
// products are placed near, or between, the blocks they cover. Positions are node centres.

export interface Point {
  x: number
  y: number
}

export interface ProductLink {
  id: string
  blocks: string[]
}

export const BLOCK_SIZE = { width: 280, height: 110 }
export const PRODUCT_SIZE = { width: 200, height: 56 }

const GAP = 16

// The framework diagram: Presentation on top, three blocks in the middle, two below.
const BLOCK_POSITIONS: Record<string, Point> = {
  Presentation: { x: 0, y: -900 },
  Observability: { x: -1000, y: 0 },
  Orchestrator: { x: 0, y: 0 },
  Intent: { x: 1000, y: 0 },
  Collector: { x: -500, y: 900 },
  Executor: { x: 500, y: 900 },
}

const RING_START = 210
const RING_STEP = 80

function placeBlocks(blockNames: string[]): Record<string, Point> {
  const positions: Record<string, Point> = {}
  const unknown = blockNames.filter((name) => !BLOCK_POSITIONS[name])
  for (const name of blockNames) {
    if (BLOCK_POSITIONS[name]) positions[name] = { ...BLOCK_POSITIONS[name] }
  }
  unknown.forEach((name, index) => {
    positions[name] = { x: (index - (unknown.length - 1) / 2) * 900, y: 1800 }
  })
  return positions
}

function overlaps(a: Point, b: Point, aSize: typeof PRODUCT_SIZE, bSize: typeof PRODUCT_SIZE) {
  const dx = (aSize.width + bSize.width) / 2 + GAP - Math.abs(a.x - b.x)
  const dy = (aSize.height + bSize.height) / 2 + GAP - Math.abs(a.y - b.y)
  return dx > 0 && dy > 0 ? { dx, dy } : null
}

export function layoutGraph(blockNames: string[], products: ProductLink[]) {
  const blocks = placeBlocks(blockNames)
  const positions: Record<string, Point> = {}

  // Products with one block go on rings around it; products with several sit between them.
  const ringCount: Record<string, number> = {}
  const sorted = [...products].sort((a, b) => a.id.localeCompare(b.id))
  for (const product of sorted) {
    const linked = product.blocks.filter((name) => blocks[name])
    if (!linked.length) continue
    if (linked.length === 1) {
      const centre = blocks[linked[0]]
      const index = ringCount[linked[0]] ?? 0
      ringCount[linked[0]] = index + 1
      let ring = 0
      let slot = index
      let slots = Math.floor((2 * Math.PI * RING_START) / (PRODUCT_SIZE.width * 0.75))
      while (slot >= slots) {
        slot -= slots
        ring += 1
        slots = Math.floor((2 * Math.PI * (RING_START + ring * RING_STEP)) / (PRODUCT_SIZE.width * 0.75))
      }
      const radius = RING_START + ring * RING_STEP
      const angle = (2 * Math.PI * slot) / slots + ring * 0.35
      positions[product.id] = {
        x: centre.x + Math.cos(angle) * radius * 1.6,
        y: centre.y + Math.sin(angle) * radius,
      }
    } else {
      const x = linked.reduce((sum, name) => sum + blocks[name].x, 0) / linked.length
      const y = linked.reduce((sum, name) => sum + blocks[name].y, 0) / linked.length
      positions[product.id] = { x, y: y + 40 }
    }
  }

  // Push overlapping nodes apart. Fixed passes and a fixed order keep the result the same each time.
  const ids = Object.keys(positions).sort()
  for (let pass = 0; pass < 300; pass++) {
    let moved = false
    for (let i = 0; i < ids.length; i++) {
      const a = positions[ids[i]]
      for (const block of Object.values(blocks)) {
        const hit = overlaps(a, block, PRODUCT_SIZE, BLOCK_SIZE)
        if (hit) {
          if (hit.dx < hit.dy) a.x += a.x >= block.x ? hit.dx : -hit.dx
          else a.y += a.y >= block.y ? hit.dy : -hit.dy
          moved = true
        }
      }
      for (let j = i + 1; j < ids.length; j++) {
        const b = positions[ids[j]]
        const hit = overlaps(a, b, PRODUCT_SIZE, PRODUCT_SIZE)
        if (!hit) continue
        moved = true
        if (hit.dx < hit.dy) {
          const shift = hit.dx / 2 + 0.5
          const sign = a.x < b.x || (a.x === b.x && i < j) ? -1 : 1
          a.x += sign * shift
          b.x -= sign * shift
        } else {
          const shift = hit.dy / 2 + 0.5
          const sign = a.y < b.y || (a.y === b.y && i < j) ? -1 : 1
          a.y += sign * shift
          b.y -= sign * shift
        }
      }
    }
    if (!moved) break
  }

  return { blocks, products: positions }
}
