'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'

const menuItems = [
  { href: '/dashboard', label: 'ダッシュボード' },
  { href: '/upload', label: '契約書登録' },
  { href: '/contracts', label: '契約検索' },
  { href: '/rentroll', label: 'レントロール作成' },
  { href: '/analysis', label: 'AI契約分析' },
  { href: '/calendar', label: '期限管理' },
]

export default function Sidebar() {
  const pathname = usePathname()

  return (
    <aside className="w-60 bg-white border-r border-gray-200 min-h-screen">
      <nav className="p-4">
        <ul className="space-y-1">
          {menuItems.map((item) => {
            const isActive = pathname === item.href
            return (
              <li key={item.href}>
                <Link
                  href={item.href}
                  className={`block px-4 py-3 rounded-lg transition-colors ${
                    isActive
                      ? 'bg-blue-50 text-primary-dark border-l-4 border-primary font-semibold'
                      : 'text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  {item.label}
                </Link>
              </li>
            )
          })}
        </ul>

        <ul className="mt-6 pt-6 border-t border-gray-200">
          <li>
            <Link
              href="/settings"
              className="block px-4 py-3 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
            >
              設定
            </Link>
          </li>
        </ul>
      </nav>
    </aside>
  )
}
