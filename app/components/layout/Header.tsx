import Link from 'next/link'

export default function Header() {
  return (
    <header className="bg-primary-darker text-white shadow-md">
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        <h1 className="text-xl font-bold">契約管理APP</h1>
        <nav className="flex gap-6">
          <Link href="/dashboard" className="hover:text-blue-200 transition-colors">
            ダッシュボード
          </Link>
          <Link href="/login" className="hover:text-blue-200 transition-colors">
            ログアウト
          </Link>
        </nav>
      </div>
    </header>
  )
}
