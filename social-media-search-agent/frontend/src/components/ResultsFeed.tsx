import React, { useState } from 'react'
import { Post, PLATFORM_COLORS, PLATFORM_ICONS } from '../types'

interface Props {
  posts: Post[]
  pathTaken: 'direct' | 'refined' | null
}

const PLATFORMS = ['all', 'twitter', 'reddit', 'linkedin', 'instagram', 'tiktok', 'youtube']

function scoreColor(score: number | null): string {
  if (score === null) return 'text-gray-500'
  if (score >= 8) return 'text-emerald-400'
  if (score >= 6) return 'text-yellow-400'
  return 'text-red-400'
}

function formatEngagement(engagement: Record<string, number>): string {
  const [key, val] = Object.entries(engagement)[0] ?? []
  if (!key) return ''
  const label = key === 'views' ? 'views' : key === 'upvotes' ? 'upvotes' : key
  return `${val.toLocaleString()} ${label}`
}

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime()
  const h = Math.floor(diff / 3600000)
  const d = Math.floor(h / 24)
  if (d > 0) return `${d}d ago`
  if (h > 0) return `${h}h ago`
  return 'just now'
}

export default function ResultsFeed({ posts, pathTaken }: Props) {
  const [filter, setFilter] = useState('all')
  const [sortBy, setSortBy] = useState<'score' | 'time'>('score')

  const visible = posts
    .filter(p => filter === 'all' || p.platform === filter)
    .sort((a, b) => {
      if (sortBy === 'score') return (b.score ?? 0) - (a.score ?? 0)
      return new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
    })

  return (
    <div className="flex flex-col gap-3 h-full">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
          Results
          {posts.length > 0 && (
            <span className="ml-2 text-gray-500 normal-case font-normal">
              ({posts.length} posts)
            </span>
          )}
        </div>
        {pathTaken && (
          <span className={`text-[10px] px-2 py-0.5 rounded-full border font-semibold ${
            pathTaken === 'refined'
              ? 'bg-amber-900/30 border-amber-500/40 text-amber-300'
              : 'bg-emerald-900/30 border-emerald-500/40 text-emerald-300'
          }`}>
            {pathTaken === 'refined' ? '✦ Refined' : '✓ Direct'}
          </span>
        )}
      </div>

      {/* Controls */}
      {posts.length > 0 && (
        <div className="flex flex-col gap-2">
          {/* Platform filter */}
          <div className="flex flex-wrap gap-1">
            {PLATFORMS.map(p => (
              <button
                key={p}
                onClick={() => setFilter(p)}
                className={`
                  text-[10px] px-2 py-0.5 rounded border transition-colors capitalize
                  ${filter === p
                    ? 'bg-blue-900/40 border-blue-500/60 text-blue-300'
                    : 'bg-gray-800 border-gray-700 text-gray-500 hover:text-gray-300'
                  }
                `}
              >
                {p === 'all' ? 'All' : `${PLATFORM_ICONS[p]} ${p}`}
              </button>
            ))}
          </div>
          {/* Sort */}
          <div className="flex gap-2 items-center">
            <span className="text-[10px] text-gray-600">Sort:</span>
            {(['score', 'time'] as const).map(s => (
              <button
                key={s}
                onClick={() => setSortBy(s)}
                className={`text-[10px] px-2 py-0.5 rounded border transition-colors ${
                  sortBy === s
                    ? 'border-blue-500/60 text-blue-300 bg-blue-900/30'
                    : 'border-gray-700 text-gray-500 hover:text-gray-300'
                }`}
              >
                {s === 'score' ? 'Relevance' : 'Recency'}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Feed */}
      <div className="flex flex-col gap-2 overflow-y-auto flex-1 pr-1">
        {posts.length === 0 ? (
          <div className="text-gray-600 text-xs italic text-center pt-8">
            Results will appear here…
          </div>
        ) : (
          visible.map(post => (
            <div
              key={post.id}
              className="bg-gray-900 border border-gray-800 hover:border-gray-700
                         rounded-lg p-3 flex flex-col gap-2 transition-colors"
            >
              {/* Top row */}
              <div className="flex items-center justify-between gap-2">
                <span className={`
                  text-[10px] px-2 py-0.5 rounded border font-semibold capitalize
                  ${PLATFORM_COLORS[post.platform] ?? 'bg-gray-700 text-gray-300 border-gray-600'}
                `}>
                  {PLATFORM_ICONS[post.platform] ?? ''} {post.platform}
                </span>

                {post.score !== null && (
                  <span className={`text-sm font-bold ${scoreColor(post.score)}`}>
                    {post.score}/10
                  </span>
                )}
              </div>

              {/* Author + time */}
              <div className="flex items-center gap-2 text-[10px] text-gray-500">
                <span className="font-semibold text-gray-400">{post.author}</span>
                <span>·</span>
                <span>{timeAgo(post.timestamp)}</span>
                {post.engagement && (
                  <>
                    <span>·</span>
                    <span>{formatEngagement(post.engagement)}</span>
                  </>
                )}
              </div>

              {/* Post text */}
              <p className="text-xs text-gray-300 leading-relaxed line-clamp-4 whitespace-pre-line">
                {post.text}
              </p>

              {/* Reason */}
              {post.reason && (
                <div className="text-[10px] text-gray-500 italic border-t border-gray-800 pt-1.5">
                  {post.reason}
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  )
}
