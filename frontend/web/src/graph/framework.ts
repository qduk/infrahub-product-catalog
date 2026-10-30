// The building blocks as the framework's reference diagram arranges them, without products.
// Diagram: https://reference.networkautomation.forum/Framework/images/naf-automation-framework-v1-dark.png
// The items inside each block are copied from that diagram.

import { byFrameworkOrder } from './blockStyle'

export type DiagramRow = 'top' | 'middle' | 'bottom'

export const FRAMEWORK_DIAGRAM: Record<string, { row: DiagramRow; items: string[] }> = {
  Presentation: { row: 'top', items: ['Dashboards · CLI · ITSM Integration · API Gateway · ChatOps'] },
  Observability: { row: 'middle', items: ['Observed State · Data Normalization', 'Observed Logic & Analytics'] },
  Orchestrator: { row: 'middle', items: ['Events', 'Workflows', 'Rollback', 'Scheduling'] },
  Intent: { row: 'middle', items: ['Intended State (SoT)', 'Intended Logic & Validation'] },
  Collector: { row: 'bottom', items: ['Read Operations', '▲ Read from infrastructure'] },
  Executor: { row: 'bottom', items: ['Write Operations · Idempotent · Dry-Run', '▼ Write to infrastructure'] },
}

export const INFRASTRUCTURE_ITEMS = 'Routers · Switches · Firewalls · Load Balancers · SD-WAN · Cloud Fabric · Compute · DPU'

// Top-left corner and size, in graph coordinates.
export interface Box {
  x: number
  y: number
  width: number
  height: number
}

const WIDTH = 1200
const GAP = 24
const ROW_HEIGHT: Record<DiagramRow | 'other' | 'infrastructure', number> = {
  top: 110,
  middle: 200,
  bottom: 185,
  other: 150,
  infrastructure: 90,
}

// Lays out boxes of equal width across the full width, or, for the bottom row, inset as in the diagram.
function row(names: string[], y: number, height: number, inset = 0): Record<string, Box> {
  const boxes: Record<string, Box> = {}
  const gap = inset ? WIDTH / 10 : GAP
  const width = (WIDTH - 2 * inset - gap * (names.length - 1)) / names.length
  names.forEach((name, index) => {
    boxes[name] = { x: inset + index * (width + gap), y, width, height }
  })
  return boxes
}

export function frameworkLayout(names: string[]) {
  const blockNames = [...names].sort(byFrameworkOrder)
  const inRow = (name: DiagramRow) => blockNames.filter((block) => FRAMEWORK_DIAGRAM[block]?.row === name)
  const others = blockNames.filter((block) => !FRAMEWORK_DIAGRAM[block])

  const blocks: Record<string, Box> = {}
  let y = 0
  const rows: [string[], number, number][] = [
    [inRow('top'), ROW_HEIGHT.top, 0],
    [inRow('middle'), ROW_HEIGHT.middle, 0],
    [inRow('bottom'), ROW_HEIGHT.bottom, inRow('bottom').length === 2 ? WIDTH / 20 : 0],
    [others, ROW_HEIGHT.other, 0],
  ]
  for (const [names, height, inset] of rows) {
    if (!names.length) continue
    Object.assign(blocks, row(names, y, height, inset))
    y += height + GAP
  }
  const infrastructure: Box = { x: 0, y, width: WIDTH, height: ROW_HEIGHT.infrastructure }
  const bounds: Box = { x: 0, y: 0, width: WIDTH, height: y + ROW_HEIGHT.infrastructure }
  return { blocks, infrastructure, bounds }
}
