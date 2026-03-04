import React, { useState } from 'react'
import { QueryDisplay as QueryDisplayType } from '../types'

interface Props {
  query: QueryDisplayType | null
}

const PLATFORM_TAB_COLORS: Record<string, string> = {
  twitter:   'border-sky-500 text-sky-300',
  reddit:    'border-orange-500 text-orange-300',
  linkedin:  'border-blue-500 text-blue-300',
  instagram: 'border-pink-500 text-pink-300',
  tiktok:    'border-purple-500 text-purple-300',
  youtube:   'border-red-500 text-red-300',
}

const PLATFORM_ICONS: Record<string, string> = {
  twitter: '𝕏', reddit: '🔴', linkedin: '💼',
  instagram: '📸', tiktok: '🎵', youtube: '▶',
}

export default function QueryDisplay({ query }: Props) {
  const [activeTab, setActiveTab] = useState('twitter')
  const [showBroadened, setShowBroadened] = useState(false)

  if (!query) {
    return (
      <div className="bg-gray-900 border border-gray-700 rounded-xl p-4 text-gray-600 text-xs italic">
        Query will appear here once generated…
      </div>
    )
  }

  const platforms = Object.keys(query.booleanQueries)
  const hasBroadened = !!query.broadenedQueries

  const activeQueries = showBroadened && hasBroadened
    ? query.broadenedQueries!
    : query.booleanQueries

  return (
    <div className="flex flex-col gap-3">
      {/* Intent prompt */}
      <div className="bg-gray-900 border border-gray-700 rounded-xl p-4">
        <div className="text-[10px] text-gray-500 uppercase tracking-wider mb-2 font-semibold">
          Intent Prompt
        </div>
        <p className="text-xs text-gray-300 leading-relaxed">{query.intentPrompt}</p>
      </div>

      {/* Boolean queries */}
      <div className="bg-gray-900 border border-gray-700 rounded-xl overflow-hidden">
        {/* Toggle */}
        {hasBroadened && (
          <div className="flex border-b border-gray-700">
            <button
              onClick={() => setShowBroadened(false)}
              className={`flex-1 py-1.5 text-[10px] font-semibold transition-colors ${
                !showBroadened
                  ? 'bg-gray-800 text-gray-200'
                  : 'text-gray-500 hover:text-gray-300'
              }`}
            >
              Original
            </button>
            <button
              onClick={() => setShowBroadened(true)}
              className={`flex-1 py-1.5 text-[10px] font-semibold transition-colors ${
                showBroadened
                  ? 'bg-amber-900/40 text-amber-300'
                  : 'text-gray-500 hover:text-gray-300'
              }`}
            >
              Broadened ✦
            </button>
          </div>
        )}

        {/* Platform tabs */}
        <div className="flex overflow-x-auto border-b border-gray-700 px-1 pt-1 gap-0.5">
          {platforms.map(p => (
            <button
              key={p}
              onClick={() => setActiveTab(p)}
              className={`
                flex items-center gap-1 px-2 py-1 text-[10px] font-semibold rounded-t whitespace-nowrap
                border-b-2 transition-colors
                ${activeTab === p
                  ? PLATFORM_TAB_COLORS[p] + ' bg-gray-800'
                  : 'border-transparent text-gray-500 hover:text-gray-400'
                }
              `}
            >
              <span>{PLATFORM_ICONS[p]}</span>
              <span className="capitalize">{p}</span>
            </button>
          ))}
        </div>

        {/* Query content */}
        <div className="p-3">
          <code className="text-[11px] text-green-300 leading-relaxed break-all whitespace-pre-wrap font-mono">
            {activeQueries[activeTab] || '—'}
          </code>
        </div>
      </div>

      {/* Broadening explanation */}
      {hasBroadened && showBroadened && query.broadeningExplanation && (
        <div className="bg-amber-900/20 border border-amber-500/30 rounded-xl p-3">
          <div className="text-[10px] text-amber-400 font-semibold uppercase tracking-wider mb-2">
            Broadening Applied
          </div>
          <p className="text-xs text-amber-200/80 mb-2 leading-relaxed">
            {query.broadeningExplanation}
          </p>
          {query.broadeningStrategies && query.broadeningStrategies.length > 0 && (
            <ul className="flex flex-col gap-0.5">
              {query.broadeningStrategies.map((s, i) => (
                <li key={i} className="text-[10px] text-amber-300/70 flex items-start gap-1">
                  <span className="mt-0.5">•</span>
                  <span>{s}</span>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  )
}
