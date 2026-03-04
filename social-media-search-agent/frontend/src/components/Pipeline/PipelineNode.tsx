import React from 'react'
import { PipelineStep } from '../../types'

interface Props {
  step: PipelineStep
  isLast?: boolean
  showConnector?: boolean
}

const STATUS_STYLES: Record<string, string> = {
  pending:  'bg-gray-800 border-gray-600 text-gray-500',
  active:   'bg-blue-900/60 border-blue-400 text-blue-300 animate-pulse',
  complete: 'bg-emerald-900/50 border-emerald-500 text-emerald-300',
  skipped:  'bg-gray-900 border-gray-700 text-gray-600 opacity-40',
  error:    'bg-red-900/50 border-red-500 text-red-300',
}

const STATUS_ICONS: Record<string, string> = {
  pending:  '○',
  active:   '◉',
  complete: '✓',
  skipped:  '—',
  error:    '✗',
}

export default function PipelineNode({ step, showConnector = true }: Props) {
  return (
    <div className="flex items-center gap-1">
      <div className={`
        flex flex-col items-center justify-center
        w-28 min-h-[80px] rounded-lg border px-2 py-2
        text-center text-xs transition-all duration-500
        ${STATUS_STYLES[step.status]}
      `}>
        <span className="text-lg leading-none mb-1">
          {STATUS_ICONS[step.status]}
        </span>
        <span className="font-semibold leading-tight">{step.label}</span>
        {step.metric && (
          <span className="mt-1 text-[10px] opacity-80 leading-tight">
            {step.metric}
          </span>
        )}
        {step.durationMs && (
          <span className="mt-0.5 text-[10px] opacity-50">
            {(step.durationMs / 1000).toFixed(1)}s
          </span>
        )}
      </div>

      {showConnector && (
        <div className={`
          text-lg leading-none transition-colors duration-300
          ${step.status === 'complete' ? 'text-emerald-500' : 'text-gray-700'}
        `}>
          →
        </div>
      )}
    </div>
  )
}
