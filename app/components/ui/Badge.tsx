import React from 'react'

interface BadgeProps {
  children: React.ReactNode
  variant?: 'info' | 'success' | 'warning' | 'danger'
  className?: string
}

export default function Badge({ children, variant = 'info', className = '' }: BadgeProps) {
  const variants = {
    info: 'bg-blue-100 text-blue-800',
    success: 'bg-green-100 text-green-800',
    warning: 'bg-yellow-100 text-yellow-800',
    danger: 'bg-red-100 text-red-800',
  }

  return (
    <span className={`px-3 py-1 rounded-full text-xs font-semibold ${variants[variant]} ${className}`}>
      {children}
    </span>
  )
}
