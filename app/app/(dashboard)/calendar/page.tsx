import DashboardLayout from '@/components/layout/DashboardLayout'
import Card from '@/components/ui/Card'
import Badge from '@/components/ui/Badge'

export default function CalendarPage() {
  const events = [
    { date: '10/15', id: 'C-2024-089', type: '契約満了', property: '渋谷店舗 1F', variant: 'danger' as const },
    { date: '10/20', id: 'C-2025-010', type: '契約開始', property: '品川オフィス 7F', variant: 'success' as const },
    { date: '10/25', id: 'C-2024-102', type: '更新期限', property: '横浜倉庫A棟', variant: 'info' as const },
    { date: '10/28', id: 'C-2024-115', type: '契約満了', property: '新宿ビル 3F', variant: 'danger' as const },
  ]

  // 簡易カレンダーデータ（実際はDate APIで生成）
  const days = Array.from({ length: 31 }, (_, i) => i + 1)

  return (
    <DashboardLayout>
      <h1 className="text-3xl font-bold text-gray-900 mb-6">期限管理</h1>

      <div className="grid grid-cols-3 gap-6">
        {/* カレンダー */}
        <div className="col-span-2">
          <Card>
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold">2025年10月</h2>
              <div className="flex gap-2">
                <button className="px-3 py-1 border border-gray-300 rounded hover:bg-gray-50">←</button>
                <button className="px-3 py-1 border border-gray-300 rounded hover:bg-gray-50">今日</button>
                <button className="px-3 py-1 border border-gray-300 rounded hover:bg-gray-50">→</button>
              </div>
            </div>

            {/* カレンダーグリッド */}
            <div className="grid grid-cols-7 gap-1">
              {/* 曜日ヘッダー */}
              {['日', '月', '火', '水', '木', '金', '土'].map((day) => (
                <div key={day} className="text-center text-sm font-semibold text-gray-600 py-2">
                  {day}
                </div>
              ))}

              {/* 空白（月初の曜日調整） */}
              {Array.from({ length: 2 }, (_, i) => (
                <div key={`empty-${i}`} className="aspect-square" />
              ))}

              {/* 日付 */}
              {days.map((day) => {
                const hasEvent = [15, 20, 25, 28].includes(day)
                const isToday = day === 5

                return (
                  <div
                    key={day}
                    className={`aspect-square border rounded p-2 hover:bg-gray-50 cursor-pointer relative ${
                      isToday ? 'bg-blue-50 border-primary' : 'border-gray-200'
                    }`}
                  >
                    <div className={`text-sm font-medium ${isToday ? 'text-primary' : 'text-gray-700'}`}>
                      {day}
                    </div>
                    {hasEvent && (
                      <div className="absolute bottom-1 left-1/2 transform -translate-x-1/2 flex gap-0.5">
                        <div className="w-1.5 h-1.5 rounded-full bg-red-500" />
                        {day === 20 && <div className="w-1.5 h-1.5 rounded-full bg-green-500" />}
                      </div>
                    )}
                  </div>
                )
              })}
            </div>

            {/* 凡例 */}
            <div className="flex gap-6 mt-6 pt-4 border-t border-gray-200">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-blue-500" />
                <span className="text-sm text-gray-600">契約開始</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-green-500" />
                <span className="text-sm text-gray-600">契約更新</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-red-500" />
                <span className="text-sm text-gray-600">契約満了</span>
              </div>
            </div>
          </Card>
        </div>

        {/* 今月のイベント */}
        <div className="col-span-1">
          <Card>
            <h2 className="text-xl font-semibold mb-4">今月のイベント</h2>

            <div className="space-y-3">
              {events.map((event, idx) => (
                <div
                  key={idx}
                  className="p-3 border border-gray-200 rounded hover:bg-gray-50 cursor-pointer"
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-semibold text-gray-700">{event.date}</span>
                    <Badge variant={event.variant}>{event.type}</Badge>
                  </div>
                  <div className="text-sm font-medium text-gray-900">{event.id}</div>
                  <div className="text-xs text-gray-600">{event.property}</div>
                </div>
              ))}
            </div>

            <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded">
              <p className="text-sm text-red-800">
                <strong>注意:</strong> 30日以内に満了する契約が12件あります。
              </p>
            </div>
          </Card>

          <Card className="mt-6">
            <h3 className="font-semibold mb-4">期限別契約数</h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center pb-2 border-b border-gray-200">
                <span className="text-sm text-gray-600">7日以内</span>
                <span className="text-lg font-bold text-red-600">3件</span>
              </div>
              <div className="flex justify-between items-center pb-2 border-b border-gray-200">
                <span className="text-sm text-gray-600">30日以内</span>
                <span className="text-lg font-bold text-orange-600">12件</span>
              </div>
              <div className="flex justify-between items-center pb-2 border-b border-gray-200">
                <span className="text-sm text-gray-600">90日以内</span>
                <span className="text-lg font-bold text-yellow-600">45件</span>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  )
}
