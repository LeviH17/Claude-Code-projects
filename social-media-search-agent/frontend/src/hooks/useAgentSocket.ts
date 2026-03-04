import { useState, useRef, useCallback } from 'react'
import { AppState, AgentEvent, PipelineStep, StepId } from '../types'

const INITIAL_STEPS: PipelineStep[] = [
  { id: 'query_gen',     label: 'Generate Queries',   path: 'main',        status: 'pending' },
  { id: 'data_fetch',    label: 'Fetch Posts',         path: 'main',        status: 'pending' },
  { id: 'scoring',       label: 'Score Posts',         path: 'main',        status: 'pending' },
  { id: 'evaluation',    label: 'Evaluate',            path: 'main',        status: 'pending' },
  { id: 'broadening',    label: 'Broaden Query',       path: 'refinement',  status: 'pending' },
  { id: 'broader_fetch', label: 'Fetch Broader Data',  path: 'refinement',  status: 'pending' },
  { id: 'filtering',     label: 'LLM Filter',          path: 'refinement',  status: 'pending' },
  { id: 'finalize',      label: 'Finalize',            path: 'main',        status: 'pending' },
]

const INITIAL_STATE: AppState = {
  status: 'idle',
  steps: INITIAL_STEPS,
  query: null,
  accuracy: { initial: null, final: null, scoringProgress: 0, filterProgress: 0 },
  posts: [],
  pathTaken: null,
  lowPerfMessage: null,
  errorMessage: null,
}

function updateStep(
  steps: PipelineStep[],
  id: StepId,
  patch: Partial<PipelineStep>,
): PipelineStep[] {
  return steps.map(s => (s.id === id ? { ...s, ...patch } : s))
}

export function useAgentSocket() {
  const [state, setState] = useState<AppState>(INITIAL_STATE)
  const wsRef = useRef<WebSocket | null>(null)

  const handleEvent = useCallback((event: AgentEvent) => {
    const p = event.payload as Record<string, any>

    setState(prev => {
      let next = { ...prev }

      switch (event.type) {

        case 'step_started': {
          const id = p.step as StepId
          next.steps = updateStep(prev.steps, id, {
            status: 'active',
            startedAt: event.timestamp,
          })
          break
        }

        case 'step_completed': {
          const id = p.step as StepId
          const step = prev.steps.find(s => s.id === id)
          const durationMs = step?.startedAt
            ? event.timestamp - step.startedAt
            : undefined

          let metric: string | undefined
          if (id === 'data_fetch')    metric = `${p.count} posts`
          if (id === 'scoring')       metric = `${p.relevance_pct}% relevant`
          if (id === 'evaluation')    metric = p.passed ? '✓ Pass' : '✗ Fail'
          if (id === 'broader_fetch') metric = `${p.count} posts`
          if (id === 'filtering')     metric = `${p.kept} kept`
          if (id === 'finalize')      metric = 'Done'

          next.steps = updateStep(prev.steps, id, {
            status: 'complete',
            metric,
            durationMs,
          })
          break
        }

        case 'query_generated': {
          next.query = {
            booleanQueries: p.boolean_queries as Record<string, string>,
            intentPrompt: p.intent_prompt as string,
          }
          break
        }

        case 'scoring_progress': {
          next.accuracy = {
            ...prev.accuracy,
            scoringProgress: p.scored as number,
            initial: p.current_relevance_pct as number,
          }
          break
        }

        case 'scoring_complete': {
          next.accuracy = {
            ...prev.accuracy,
            initial: p.relevance_pct as number,
            scoringProgress: p.total as number,
          }
          break
        }

        case 'performance_evaluated': {
          next.accuracy = {
            ...prev.accuracy,
            initial: p.relevance_pct as number,
          }
          break
        }

        case 'low_performance_detected': {
          next.lowPerfMessage = p.message as string
          // Skip refinement steps → make them visible (not skipped yet)
          break
        }

        case 'query_broadened': {
          if (next.query) {
            next.query = {
              ...next.query,
              broadenedQueries: p.broadened_queries as Record<string, string>,
              broadeningStrategies: p.strategies_used as string[],
              broadeningExplanation: p.explanation as string,
            }
          }
          break
        }

        case 'filter_progress': {
          next.accuracy = {
            ...prev.accuracy,
            filterProgress: p.processed as number,
          }
          break
        }

        case 'filter_complete': {
          next.accuracy = {
            ...prev.accuracy,
            final: p.final_relevance_pct as number,
            filterProgress: p.total_processed as number,
          }
          break
        }

        case 'results_ready': {
          const pathTaken = p.path_taken as 'direct' | 'refined'
          next.posts = (p.posts as any[]) ?? []
          next.pathTaken = pathTaken
          next.accuracy = {
            ...prev.accuracy,
            final: p.final_relevance_pct as number,
            initial: p.initial_relevance_pct as number ?? prev.accuracy.initial,
          }

          // Mark skipped steps if direct path
          if (pathTaken === 'direct') {
            next.steps = next.steps.map(s =>
              s.path === 'refinement' ? { ...s, status: 'skipped' } : s
            )
          }
          break
        }

        case 'error': {
          next.status = 'error'
          next.errorMessage = p.message as string
          break
        }
      }

      return next
    })

    // Terminal events
    if (event.type === 'results_ready') {
      setState(prev => ({ ...prev, status: 'complete' }))
    }
    if (event.type === 'error') {
      setState(prev => ({ ...prev, status: 'error' }))
    }
  }, [])

  const run = useCallback((query: string) => {
    if (wsRef.current) {
      wsRef.current.close()
    }

    setState({
      ...INITIAL_STATE,
      steps: INITIAL_STEPS.map(s => ({ ...s })),
      status: 'running',
    })

    const ws = new WebSocket(`ws://${window.location.hostname}:8000/ws`)
    wsRef.current = ws

    ws.onopen = () => {
      ws.send(JSON.stringify({ query }))
    }

    ws.onmessage = (msg) => {
      try {
        const event: AgentEvent = JSON.parse(msg.data)
        handleEvent(event)
      } catch {
        // ignore parse errors
      }
    }

    ws.onerror = () => {
      setState(prev => ({
        ...prev,
        status: 'error',
        errorMessage: 'WebSocket connection failed. Is the backend running?',
      }))
    }

    ws.onclose = () => {
      wsRef.current = null
    }
  }, [handleEvent])

  return { state, run }
}
