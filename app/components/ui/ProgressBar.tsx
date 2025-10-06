import React from 'react'

interface ProgressBarProps {
  progress: number
  label?: string
  className?: string
}

export default function ProgressBar({ progress, label, className = '' }: ProgressBarProps) {
  return (
    <div className={className}>
      {label && (
        <div className="flex justify-between mb-2">
          <span className="text-sm text-gray-700 font-medium">{label}</span>
          <span className="text-sm text-gray-700 font-semibold">{progress}%</span>
        </div>
      )}
      <div className="bg-gray-200 h-2 rounded-full overflow-hidden">
        <div
          className="h-full bg-gradient-to-r from-primary to-primary-dark transition-all duration-300"
          style={{ width: `${progress}%` }}
        />
      </div>
    </div>
  )
}
