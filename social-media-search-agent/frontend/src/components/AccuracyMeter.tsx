import React from 'react'
import { AccuracyState } from '../types'

interface Props {
  accuracy: AccuracyState
  status: string
}

export default function AccuracyMeter({ accuracy, status }: Props) {
  const { initial, final, scoringProgress, filterProgress } = accuracy

  const displayPct = final ?? initial ?? null
  const isRefining = filterProgress > 0 && final === null

  return (
    <div className="bg-gray-900 border border-gray-700 rounded-xl p-4 flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
          Accuracy
        </span>
        {displayPct !== null && (
          <span className={`text-lg font-bold ${
            displayPct >= 80 ? 'text-emerald-400' : 'text-amber-400'
          }`}>
            {displayPct.toFixed(1)}%
          </span>
        )}
      </div>

      {/* Scoring progress bar */}
      {scoringProgress > 0 && (
        <div className="flex flex-col gap-1">
          <div className="flex justify-between text-[10px] text-gray-500">
            <span>Scoring posts</span>
            <span>{scoringProgress} / 500</span>
          </div>
          <div className="w-full bg-gray-800 rounded-full h-2">
            <div
              className="bg-blue-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${(scoringProgress / 500) * 100}%` }}
            />
          </div>
        </div>
      )}

      {/* Filter progress bar */}
      {filterProgress > 0 && (
        <div className="flex flex-col gap-1">
          <div className="flex justify-between text-[10px] text-gray-500">
            <span>Filtering posts</span>
            <span>{filterProgress} / 750</span>
          </div>
          <div className="w-full bg-gray-800 rounded-full h-2">
            <div
              className="bg-purple-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${Math.min((filterProgress / 750) * 100, 100)}%` }}
            />
          </div>
        </div>
      )}

      {/* Relevance bar */}
      {displayPct !== null && (
        <div className="flex flex-col gap-1">
          <div className="relative w-full bg-gray-800 rounded-full h-4">
            {/* Threshold marker */}
            <div
              className="absolute top-0 bottom-0 w-0.5 bg-gray-400 z-10"
              style={{ left: '80%' }}
            />
            <div
              className={`h-4 rounded-full transition-all duration-700 ${
                displayPct >= 80 ? 'bg-emerald-500' : 'bg-amber-500'
              }`}
              style={{ width: `${Math.min(displayPct, 100)}%` }}
            />
            <div
              className="absolute top-[-16px] text-[9px] text-gray-400"
              style={{ left: '78%' }}
            >
              80%
            </div>
          </div>
        </div>
      )}

      {/* Before / After */}
      {initial !== null && final !== null && initial !== final && (
        <div className="flex items-center gap-2 text-xs">
          <span className="text-amber-400">{initial.toFixed(1)}%</span>
          <span className="text-gray-600">→</span>
          <span className="text-emerald-400 font-bold">{final.toFixed(1)}%</span>
          <span className="text-gray-500 text-[10px]">after refinement</span>
        </div>
      )}

      {/* Status label */}
      <div className="text-[10px] text-gray-600">
        {status === 'idle' && 'Waiting for query…'}
        {status === 'running' && displayPct === null && 'Running…'}
        {status === 'running' && displayPct !== null && isRefining && 'Refining…'}
        {status === 'complete' && final !== null && final >= 80 && '✓ Above 80% threshold'}
        {status === 'complete' && final !== null && final < 80 && '⚠ Below threshold'}
        {status === 'complete' && final === null && initial !== null && (
          initial >= 80 ? '✓ Above 80% threshold — direct path' : ''
        )}
      </div>
    </div>
  )
}
