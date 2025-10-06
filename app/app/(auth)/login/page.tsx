'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Input from '@/components/ui/Input'
import Button from '@/components/ui/Button'

export default function LoginPage() {
  const router = useRouter()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault()
    // デモなので認証処理はスキップしてダッシュボードに遷移
    router.push('/dashboard')
  }

  return (
    <div className="min-h-screen flex">
      {/* 左側: ブランディングエリア */}
      <div className="flex-1 bg-gradient-to-br from-primary-darker via-primary-dark to-primary flex items-center justify-center p-16 relative overflow-hidden">
        <div className="absolute inset-0 opacity-30">
          <div className="absolute top-[-50%] right-[-50%] w-[200%] h-[200%] bg-radial-gradient from-white/10 to-transparent animate-pulse" />
        </div>

        <div className="relative z-10 text-white text-center max-w-lg">
          <h1 className="text-5xl font-bold mb-6">契約管理APP</h1>
          <p className="text-lg mb-12 opacity-95">
            不動産契約管理をスマートに。<br />
            AIとクラウドで、契約業務を効率化します。
          </p>

          <div className="grid grid-cols-2 gap-5 mt-12">
            <div className="bg-white/10 backdrop-blur-sm p-5 rounded-lg text-left">
              <div className="text-base font-semibold mb-2">📄 AI自動抽出</div>
              <div className="text-sm opacity-90">PDFから契約情報を自動抽出</div>
            </div>
            <div className="bg-white/10 backdrop-blur-sm p-5 rounded-lg text-left">
              <div className="text-base font-semibold mb-2">🔍 高度な検索</div>
              <div className="text-sm opacity-90">自然言語で契約を検索</div>
            </div>
            <div className="bg-white/10 backdrop-blur-sm p-5 rounded-lg text-left">
              <div className="text-base font-semibold mb-2">📊 レポート作成</div>
              <div className="text-sm opacity-90">レントロールを自動生成</div>
            </div>
            <div className="bg-white/10 backdrop-blur-sm p-5 rounded-lg text-left">
              <div className="text-base font-semibold mb-2">📅 期限管理</div>
              <div className="text-sm opacity-90">更新期限を可視化</div>
            </div>
          </div>
        </div>
      </div>

      {/* 右側: ログインフォーム */}
      <div className="flex-1 bg-white flex items-center justify-center p-16">
        <div className="w-full max-w-md">
          <div className="mb-10">
            <h2 className="text-4xl font-bold text-primary-darker mb-3">ログイン</h2>
            <p className="text-gray-600">アカウント情報を入力してください</p>
          </div>

          <form onSubmit={handleLogin}>
            <Input
              label="メールアドレス"
              type="email"
              placeholder="example@company.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />

            <Input
              label="パスワード"
              type="password"
              placeholder="パスワードを入力"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />

            <Button
              type="submit"
              variant="primary"
              className="w-full py-4 text-lg mt-2"
            >
              ログイン
            </Button>

            <div className="text-center mt-6">
              <a href="#" className="text-primary text-sm hover:underline">
                パスワードを忘れた場合
              </a>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}
