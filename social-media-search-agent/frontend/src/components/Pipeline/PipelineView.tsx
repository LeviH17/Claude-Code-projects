import React from 'react'
import { PipelineStep } from '../../types'
import PipelineNode from './PipelineNode'

interface Props {
  steps: PipelineStep[]
  pathTaken: 'direct' | 'refined' | null
  lowPerfMessage: string | null
}

export default function PipelineView({ steps, pathTaken, lowPerfMessage }: Props) {
  const get = (id: string) => steps.find(s => s.id === id)!

  const mainPath   = ['query_gen', 'data_fetch', 'scoring', 'evaluation']
  const refinePath = ['broadening', 'broader_fetch', 'filtering']
  const finalStep  = get('finalize')

  const refineActive = steps.some(
    s => s.path === 'refinement' && (s.status === 'active' || s.status === 'complete')
  )
  const refineSkipped = steps.every(
    s => s.path !== 'refinement' || s.status === 'skipped' || s.status === 'pending'
  )

  return (
    <div className="flex flex-col gap-4">
      {/* Main path */}
      <div className="flex items-center flex-wrap gap-1">
        {mainPath.map((id, i) => {
          const step = get(id)
          const isEval = id === 'evaluation'
          const isLast = i === mainPath.length - 1
          return (
            <PipelineNode
              key={id}
              step={step}
              showConnector={true}
            />
          )
        })}

        {/* Branch indicator */}
        {pathTaken === 'direct' && (
          <>
            <div className="text-emerald-400 text-sm font-semibold px-1">→</div>
            <PipelineNode step={finalStep} showConnector={false} />
          </>
        )}

        {pathTaken !== 'direct' && !refineActive && !refineSkipped && (
          <div className="text-gray-600 text-xs px-2 italic">
            evaluating…
          </div>
        )}
      </div>

      {/* Low performance alert */}
      {lowPerfMessage && (
        <div className="flex items-start gap-2 bg-amber-900/30 border border-amber-500/40 rounded-lg px-3 py-2 text-amber-300 text-xs max-w-2xl">
          <span className="text-amber-400 text-base">⚠</span>
          <span>{lowPerfMessage}</span>
        </div>
      )}

      {/* Refinement path */}
      {(refineActive || pathTaken === 'refined') && (
        <div className="flex items-center flex-wrap gap-1 pl-4 border-l-2 border-amber-500/40">
          <div className="text-amber-400 text-xs mr-1 font-semibold">REFINE</div>
          {refinePath.map((id) => (
            <PipelineNode key={id} step={get(id)} showConnector={true} />
          ))}
          <PipelineNode step={finalStep} showConnector={false} />
        </div>
      )}

      {/* Skipped refinement path (direct path taken) */}
      {pathTaken === 'direct' && (
        <div className="flex items-center gap-2 pl-4 border-l-2 border-gray-700/40 opacity-40">
          <div className="text-gray-600 text-xs italic">Refinement path skipped — query met threshold</div>
        </div>
      )}
    </div>
  )
}
