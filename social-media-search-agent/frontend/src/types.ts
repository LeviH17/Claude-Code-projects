// ── Pipeline step types ───────────────────────────────────────────────────────

export type StepId =
  | 'query_gen'
  | 'data_fetch'
  | 'scoring'
  | 'evaluation'
  | 'broadening'
  | 'broader_fetch'
  | 'filtering'
  | 'finalize'

export type StepStatus = 'pending' | 'active' | 'complete' | 'skipped' | 'error'
export type PipelinePath = 'main' | 'refinement'

export interface PipelineStep {
  id: StepId
  label: string
  path: PipelinePath
  status: StepStatus
  metric?: string      // e.g. "500 posts", "65% relevance"
  durationMs?: number
  startedAt?: number
}

// ── Agent event payloads ──────────────────────────────────────────────────────

export interface AgentEvent {
  type: string
  timestamp: number
  payload: Record<string, unknown>
}

// ── Post types ────────────────────────────────────────────────────────────────

export interface Post {
  id: string
  platform: string
  text: string
  author: string
  timestamp: string
  url: string
  engagement: Record<string, number>
  score: number | null
  reason: string | null
  kept_by_filter: boolean | null
}

// ── App state ─────────────────────────────────────────────────────────────────

export type AgentStatus = 'idle' | 'running' | 'complete' | 'error'

export interface QueryDisplay {
  booleanQueries: Record<string, string>
  intentPrompt: string
  broadenedQueries?: Record<string, string>
  broadeningStrategies?: string[]
  broadeningExplanation?: string
}

export interface AccuracyState {
  initial: number | null
  final: number | null
  scoringProgress: number   // 0-500
  filterProgress: number    // 0-750
}

export interface AppState {
  status: AgentStatus
  steps: PipelineStep[]
  query: QueryDisplay | null
  accuracy: AccuracyState
  posts: Post[]
  pathTaken: 'direct' | 'refined' | null
  lowPerfMessage: string | null
  errorMessage: string | null
}

// ── Helpers ───────────────────────────────────────────────────────────────────

export const PLATFORM_COLORS: Record<string, string> = {
  twitter:   'bg-sky-500/20 text-sky-300 border-sky-500/40',
  reddit:    'bg-orange-500/20 text-orange-300 border-orange-500/40',
  linkedin:  'bg-blue-500/20 text-blue-300 border-blue-500/40',
  instagram: 'bg-pink-500/20 text-pink-300 border-pink-500/40',
  tiktok:    'bg-purple-500/20 text-purple-300 border-purple-500/40',
  youtube:   'bg-red-500/20 text-red-300 border-red-500/40',
}

export const PLATFORM_ICONS: Record<string, string> = {
  twitter:   '𝕏',
  reddit:    '🔴',
  linkedin:  '💼',
  instagram: '📸',
  tiktok:    '🎵',
  youtube:   '▶',
}
