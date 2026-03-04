import React from 'react'
import { useAgentSocket } from './hooks/useAgentSocket'
import SearchInput from './components/SearchInput'
import PipelineView from './components/Pipeline/PipelineView'
import QueryDisplay from './components/QueryDisplay'
import AccuracyMeter from './components/AccuracyMeter'
import ResultsFeed from './components/ResultsFeed'

export default function App() {
  const { state, run } = useAgentSocket()

  return (
    <div className="min-h-screen bg-gray-950 flex flex-col">
      {/* Header */}
      <header className="border-b border-gray-800 px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-xl">🔍</span>
          <div>
            <h1 className="text-sm font-bold text-gray-100 leading-none">
              Social Media Search Agent
            </h1>
            <p className="text-[10px] text-gray-500 mt-0.5">
              LLM-powered boolean search with adaptive refinement
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className={`w-2 h-2 rounded-full ${
            state.status === 'running' ? 'bg-blue-400 animate-pulse' :
            state.status === 'complete' ? 'bg-emerald-400' :
            state.status === 'error' ? 'bg-red-400' :
            'bg-gray-600'
          }`} />
          <span className="text-[10px] text-gray-500 capitalize">{state.status}</span>
        </div>
      </header>

      {/* Main layout */}
      <div className="flex-1 flex flex-col overflow-hidden p-4 gap-4">

        {/* Search bar */}
        <div className="bg-gray-900 border border-gray-700 rounded-xl p-4">
          <SearchInput
            onSubmit={run}
            disabled={state.status === 'running'}
          />
        </div>

        {/* Pipeline visualization */}
        {state.status !== 'idle' && (
          <div className="bg-gray-900 border border-gray-700 rounded-xl p-4">
            <div className="text-[10px] text-gray-500 uppercase tracking-wider font-semibold mb-3">
              Agent Pipeline
            </div>
            <PipelineView
              steps={state.steps}
              pathTaken={state.pathTaken}
              lowPerfMessage={state.lowPerfMessage}
            />
          </div>
        )}

        {/* Error */}
        {state.status === 'error' && state.errorMessage && (
          <div className="bg-red-900/30 border border-red-500/40 rounded-xl px-4 py-3 text-red-300 text-sm">
            ✗ {state.errorMessage}
          </div>
        )}

        {/* Bottom 3-column layout */}
        {state.status !== 'idle' && (
          <div className="flex-1 grid grid-cols-[320px_1fr_360px] gap-4 min-h-0">

            {/* Left: Query + Accuracy */}
            <div className="flex flex-col gap-4 overflow-y-auto">
              <AccuracyMeter accuracy={state.accuracy} status={state.status} />
              <QueryDisplay query={state.query} />
            </div>

            {/* Center: empty / placeholder for future extensions */}
            <div className="hidden xl:block" />

            {/* Right: Results feed */}
            <div className="overflow-hidden flex flex-col">
              <ResultsFeed posts={state.posts} pathTaken={state.pathTaken} />
            </div>
          </div>
        )}

        {/* Idle state */}
        {state.status === 'idle' && (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center text-gray-600 flex flex-col items-center gap-4">
              <div className="text-6xl opacity-30">🔍</div>
              <div className="text-sm">
                Enter a search intent above to start the agent
              </div>
              <div className="text-xs text-gray-700 max-w-md leading-relaxed">
                The agent will generate platform-specific boolean queries, score 500 posts for
                relevance, and automatically refine the query if accuracy falls below 80%.
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
