import React, { useState } from 'react'

interface Props {
  onSubmit: (query: string) => void
  disabled: boolean
}

const EXAMPLES = [
  'AI regulation debates in financial services',
  'Gen Z attitudes toward homeownership',
  'climate tech startup funding announcements',
  'developer frustration with Kubernetes complexity',
  'remote work productivity research and opinions',
]

export default function SearchInput({ onSubmit, disabled }: Props) {
  const [value, setValue] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (value.trim() && !disabled) onSubmit(value.trim())
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-2">
      <div className="flex gap-2">
        <textarea
          value={value}
          onChange={e => setValue(e.target.value)}
          onKeyDown={e => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault()
              if (value.trim() && !disabled) onSubmit(value.trim())
            }
          }}
          placeholder="Describe what you want to find on social media…"
          rows={3}
          disabled={disabled}
          className={`
            flex-1 bg-gray-900 border border-gray-700 rounded-lg px-3 py-2
            text-sm text-gray-200 placeholder-gray-600 resize-none
            focus:outline-none focus:border-blue-500 transition-colors
            disabled:opacity-50 disabled:cursor-not-allowed
          `}
        />
        <button
          type="submit"
          disabled={disabled || !value.trim()}
          className={`
            px-4 py-2 rounded-lg text-sm font-semibold transition-all
            ${disabled || !value.trim()
              ? 'bg-gray-800 text-gray-600 cursor-not-allowed'
              : 'bg-blue-600 hover:bg-blue-500 text-white'}
          `}
        >
          {disabled ? (
            <span className="flex items-center gap-2">
              <span className="animate-spin">⟳</span> Running
            </span>
          ) : 'Search'}
        </button>
      </div>

      {/* Example queries */}
      <div className="flex flex-wrap gap-1">
        {EXAMPLES.map(ex => (
          <button
            key={ex}
            type="button"
            disabled={disabled}
            onClick={() => setValue(ex)}
            className="text-[10px] bg-gray-800 hover:bg-gray-700 text-gray-400 hover:text-gray-200
                       border border-gray-700 rounded px-2 py-0.5 transition-colors disabled:opacity-40"
          >
            {ex}
          </button>
        ))}
      </div>
    </form>
  )
}
