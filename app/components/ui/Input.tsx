import React from 'react'

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string
}

export default function Input({ label, className = '', ...props }: InputProps) {
  return (
    <div className="mb-4">
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {label}
        </label>
      )}
      <input
        className={`w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all ${className}`}
        {...props}
      />
    </div>
  )
}
