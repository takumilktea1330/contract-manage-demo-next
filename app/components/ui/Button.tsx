import React from 'react'

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'success' | 'danger'
  children: React.ReactNode
}

export default function Button({
  variant = 'primary',
  children,
  className = '',
  ...props
}: ButtonProps) {
  const baseStyles = 'px-4 py-2 rounded-lg font-medium transition-all duration-200'

  const variants = {
    primary: 'bg-primary hover:bg-primary-dark text-white hover:shadow-md',
    secondary: 'bg-gray-500 hover:bg-gray-600 text-white hover:shadow-md',
    success: 'bg-green-600 hover:bg-green-700 text-white hover:shadow-md',
    danger: 'bg-red-600 hover:bg-red-700 text-white hover:shadow-md',
  }

  return (
    <button
      className={`${baseStyles} ${variants[variant]} ${className}`}
      {...props}
    >
      {children}
    </button>
  )
}
