import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: '契約管理APP',
  description: '不動産契約管理システム',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ja">
      <body>{children}</body>
    </html>
  )
}
