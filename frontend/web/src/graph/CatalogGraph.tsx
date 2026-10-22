import { Background, Controls, MiniMap, ReactFlow, ReactFlowProvider, useReactFlow } from '@xyflow/react'
import { useEffect, useMemo } from 'react'
import type { Catalog } from '../api'
import type { Filters } from '../filters'
import { blockStyle } from './blockStyle'
import { buildGraph, type Focus, type GraphNode } from './buildGraph'
import { edgeTypes, nodeTypes } from './nodes'

interface Props {
  catalog: Catalog
  filters: Filters
  focus: Focus
  onFocus: (focus: Focus) => void
}

function Graph({ catalog, filters, focus, onFocus }: Props) {
  const { nodes, edges } = useMemo(() => buildGraph(catalog, filters, focus), [catalog, filters, focus])
  const { fitView } = useReactFlow()

  // Refit when the set of blocks changes (all blocks or a single block).
  useEffect(() => {
    const timer = window.setTimeout(() => fitView({ padding: 0.08, duration: 300 }), 50)
    return () => window.clearTimeout(timer)
  }, [filters.block, fitView])

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') onFocus(null)
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [onFocus])

  const onNodeClick = (_: unknown, node: GraphNode) =>
    onFocus(node.type === 'block' ? { kind: 'block', name: node.data.name } : { kind: 'product', id: node.id })

  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      nodeTypes={nodeTypes}
      edgeTypes={edgeTypes}
      onNodeClick={onNodeClick}
      onPaneClick={() => onFocus(null)}
      fitView
      fitViewOptions={{ padding: 0.08 }}
      minZoom={0.1}
      maxZoom={2.5}
      nodesConnectable={false}
      edgesFocusable={false}
      proOptions={{ hideAttribution: false }}
      colorMode="dark"
    >
      <Background gap={24} size={1} color="#1f2937" />
      <Controls showInteractive={false} position="bottom-left" />
      <MiniMap
        pannable
        zoomable
        position="bottom-right"
        nodeColor={(node) => (node.type === 'block' ? blockStyle(String(node.data.name)).color : '#4b5563')}
        maskColor="rgba(5, 7, 13, 0.7)"
      />
    </ReactFlow>
  )
}

export function CatalogGraph(props: Props) {
  return (
    <div className="graph-canvas" aria-label="Catalog graph">
      <ReactFlowProvider>
        <Graph {...props} />
      </ReactFlowProvider>
    </div>
  )
}
