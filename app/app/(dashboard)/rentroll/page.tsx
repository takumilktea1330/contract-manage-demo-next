import DashboardLayout from '@/components/layout/DashboardLayout'
import Card from '@/components/ui/Card'
import Button from '@/components/ui/Button'

export default function RentrollPage() {
  const previewData = [
    { id: 'C-2025-001', property: '東京オフィスビル 5F', address: '東京都千代田区丸の内1-1-1', area: 120.50, rent: '¥500,000', deposit: '¥1,500,000', period: '2025-04-01 ～ 2027-03-31' },
    { id: 'C-2025-002', property: '渋谷店舗 1F', address: '東京都渋谷区渋谷1-1-1', area: 85.30, rent: '¥800,000', deposit: '¥2,400,000', period: '2025-03-15 ～ 2026-03-14' },
  ]

  return (
    <DashboardLayout>
      <h1 className="text-3xl font-bold text-gray-900 mb-6">レントロール作成</h1>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
        <p className="text-sm text-blue-800">
          <strong>レントロールとは:</strong> 賃貸物件の一覧表で、物件情報・賃料・契約状況などを一覧化したレポートです。
        </p>
      </div>

      {/* 出力条件設定 */}
      <Card className="mb-6">
        <h3 className="text-lg font-semibold mb-4">出力条件設定</h3>

        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">対象期間（開始）</label>
            <input
              type="date"
              defaultValue="2025-01-01"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-primary"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">対象期間（終了）</label>
            <input
              type="date"
              defaultValue="2025-12-31"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-primary"
            />
          </div>
        </div>

        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">契約ステータス</label>
          <div className="flex gap-6">
            <label className="flex items-center gap-2">
              <input type="checkbox" defaultChecked className="rounded" />
              <span className="text-sm">有効契約</span>
            </label>
            <label className="flex items-center gap-2">
              <input type="checkbox" className="rounded" />
              <span className="text-sm">終了契約</span>
            </label>
            <label className="flex items-center gap-2">
              <input type="checkbox" defaultChecked className="rounded" />
              <span className="text-sm">未検証契約</span>
            </label>
          </div>
        </div>

        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">出力項目</label>
          <div className="grid grid-cols-3 gap-4">
            <label className="flex items-center gap-2">
              <input type="checkbox" defaultChecked className="rounded" />
              <span className="text-sm">契約番号</span>
            </label>
            <label className="flex items-center gap-2">
              <input type="checkbox" defaultChecked className="rounded" />
              <span className="text-sm">物件名</span>
            </label>
            <label className="flex items-center gap-2">
              <input type="checkbox" defaultChecked className="rounded" />
              <span className="text-sm">所在地</span>
            </label>
            <label className="flex items-center gap-2">
              <input type="checkbox" defaultChecked className="rounded" />
              <span className="text-sm">面積</span>
            </label>
            <label className="flex items-center gap-2">
              <input type="checkbox" defaultChecked className="rounded" />
              <span className="text-sm">賃料</span>
            </label>
            <label className="flex items-center gap-2">
              <input type="checkbox" defaultChecked className="rounded" />
              <span className="text-sm">敷金</span>
            </label>
          </div>
        </div>

        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">ソート順</label>
          <select className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-primary">
            <option>契約番号（昇順）</option>
            <option>契約番号（降順）</option>
            <option>物件名（昇順）</option>
            <option>賃料（高い順）</option>
            <option>賃料（低い順）</option>
          </select>
        </div>

        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">出力形式</label>
          <div className="flex gap-6">
            <label className="flex items-center gap-2">
              <input type="radio" name="format" defaultChecked />
              <span className="text-sm">Excel (xlsx)</span>
            </label>
            <label className="flex items-center gap-2">
              <input type="radio" name="format" />
              <span className="text-sm">CSV</span>
            </label>
            <label className="flex items-center gap-2">
              <input type="radio" name="format" />
              <span className="text-sm">PDF</span>
            </label>
          </div>
        </div>

        <div className="flex gap-3">
          <Button variant="primary">プレビュー</Button>
          <Button variant="success">ダウンロード</Button>
          <Button variant="secondary">条件をクリア</Button>
        </div>
      </Card>

      {/* プレビュー */}
      <Card className="mb-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">レントロールプレビュー</h2>
          <span className="text-sm text-gray-600">対象件数: 987件</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-3 py-2 text-left font-semibold">契約番号</th>
                <th className="px-3 py-2 text-left font-semibold">物件名</th>
                <th className="px-3 py-2 text-left font-semibold">所在地</th>
                <th className="px-3 py-2 text-left font-semibold">面積(m²)</th>
                <th className="px-3 py-2 text-left font-semibold">賃料</th>
                <th className="px-3 py-2 text-left font-semibold">敷金</th>
                <th className="px-3 py-2 text-left font-semibold">契約期間</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {previewData.map((row) => (
                <tr key={row.id} className="hover:bg-gray-50">
                  <td className="px-3 py-2">{row.id}</td>
                  <td className="px-3 py-2">{row.property}</td>
                  <td className="px-3 py-2">{row.address}</td>
                  <td className="px-3 py-2">{row.area}</td>
                  <td className="px-3 py-2 font-medium">{row.rent}</td>
                  <td className="px-3 py-2">{row.deposit}</td>
                  <td className="px-3 py-2">{row.period}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <p className="text-center text-sm text-gray-600 mt-4">
          ※上記は最初の5件のプレビューです。全件出力するにはダウンロードしてください。
        </p>
      </Card>

      {/* サマリー */}
      <Card>
        <h2 className="text-xl font-semibold mb-6">サマリー情報</h2>
        <div className="grid grid-cols-4 gap-6">
          <div className="text-center">
            <div className="text-sm text-gray-600 mb-2">総契約件数</div>
            <div className="text-3xl font-bold text-primary">987件</div>
          </div>
          <div className="text-center">
            <div className="text-sm text-gray-600 mb-2">月額賃料合計</div>
            <div className="text-3xl font-bold text-primary">¥125,450,000</div>
          </div>
          <div className="text-center">
            <div className="text-sm text-gray-600 mb-2">平均賃料</div>
            <div className="text-3xl font-bold text-primary">¥127,088</div>
          </div>
          <div className="text-center">
            <div className="text-sm text-gray-600 mb-2">総面積</div>
            <div className="text-3xl font-bold text-primary">125,340 m²</div>
          </div>
        </div>
      </Card>
    </DashboardLayout>
  )
}
