import DashboardLayout from '@/components/layout/DashboardLayout'
import Card from '@/components/ui/Card'
import Badge from '@/components/ui/Badge'
import Link from 'next/link'

export default function DashboardPage() {
  const quickActions = [
    { href: '/upload', label: '契約書登録', sublabel: 'PDF契約書をアップロード', tag: 'UPLOAD' },
    { href: '/contracts', label: '契約検索', sublabel: '通常検索・AI検索で契約を検索', tag: 'SEARCH' },
    { href: '/rentroll', label: 'レントロール作成', sublabel: '賃料台帳を出力', tag: 'REPORT' },
    { href: '/analysis', label: 'AI契約分析', sublabel: '対話形式でデータ分析', tag: 'ANALYSIS' },
    { href: '/calendar', label: '期限管理', sublabel: '契約期限をカレンダーで管理', tag: 'CALENDAR' },
  ]

  const recentContracts = [
    { id: 'C-2025-001', name: '東京オフィスビル 5F', date: '2025-10-01', status: '検証済み' },
    { id: 'C-2025-002', name: '渋谷店舗 1F', date: '2025-09-28', status: '未検証' },
    { id: 'C-2024-125', name: '品川オフィス 3F', date: '2025-09-25', status: '検証済み' },
  ]

  return (
    <DashboardLayout>
      <h1 className="text-3xl font-bold text-gray-900 mb-6">ダッシュボード</h1>

      {/* アラート */}
      <div className="space-y-4 mb-8">
        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-yellow-700">
                <strong>未検証の契約情報が23件あります。</strong> 検証を完了してください。
              </p>
            </div>
          </div>
        </div>

        <div className="bg-red-50 border-l-4 border-red-400 p-4 rounded">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-red-700">
                <strong>30日以内に満了する契約が12件あります。</strong> 更新手続きを確認してください。
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* クイックアクション */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">主要機能</h2>
        <div className="grid grid-cols-2 gap-5">
          {quickActions.map((action) => (
            <Link key={action.href} href={action.href}>
              <Card className="hover:shadow-lg transition-shadow cursor-pointer border-l-4 border-primary-dark">
                <div className="text-primary-dark text-xs font-semibold tracking-wider mb-2">
                  {action.tag}
                </div>
                <div className="text-xl font-semibold text-gray-900 mb-2">{action.label}</div>
                <div className="text-sm text-gray-600">{action.sublabel}</div>
              </Card>
            </Link>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-6">
        {/* 最近追加された契約 */}
        <Card>
          <h2 className="text-lg font-semibold mb-4">最近追加された契約</h2>
          <div className="space-y-3">
            {recentContracts.map((contract) => (
              <div key={contract.id} className="flex justify-between items-center p-3 bg-gray-50 rounded">
                <div>
                  <div className="font-medium text-gray-900">{contract.id}</div>
                  <div className="text-sm text-gray-600">{contract.name}</div>
                </div>
                <div className="text-right">
                  <div className="text-sm text-gray-600">{contract.date}</div>
                  <Badge variant={contract.status === '検証済み' ? 'success' : 'warning'}>
                    {contract.status}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
          <button className="mt-4 w-full text-center text-sm text-primary hover:underline">
            すべて表示 →
          </button>
        </Card>

        {/* 簡易カレンダー */}
        <Card>
          <h2 className="text-lg font-semibold mb-4">今月の契約イベント</h2>
          <div className="space-y-2">
            <div className="flex items-center p-2 hover:bg-gray-50 rounded">
              <div className="w-16 text-sm text-gray-600">10/15</div>
              <div className="flex-1">
                <div className="text-sm font-medium">C-2024-089 契約満了</div>
                <div className="text-xs text-gray-600">渋谷店舗 1F</div>
              </div>
              <Badge variant="danger">満了</Badge>
            </div>
            <div className="flex items-center p-2 hover:bg-gray-50 rounded">
              <div className="w-16 text-sm text-gray-600">10/20</div>
              <div className="flex-1">
                <div className="text-sm font-medium">C-2025-010 契約開始</div>
                <div className="text-xs text-gray-600">品川オフィス 7F</div>
              </div>
              <Badge variant="success">開始</Badge>
            </div>
            <div className="flex items-center p-2 hover:bg-gray-50 rounded">
              <div className="w-16 text-sm text-gray-600">10/25</div>
              <div className="flex-1">
                <div className="text-sm font-medium">C-2024-102 更新期限</div>
                <div className="text-xs text-gray-600">横浜倉庫A棟</div>
              </div>
              <Badge variant="info">更新</Badge>
            </div>
          </div>
          <Link href="/calendar" className="mt-4 block w-full text-center text-sm text-primary hover:underline">
            カレンダーを見る →
          </Link>
        </Card>
      </div>
    </DashboardLayout>
  )
}
