import DashboardLayout from '@/components/layout/DashboardLayout'
import Card from '@/components/ui/Card'
import Badge from '@/components/ui/Badge'
import Button from '@/components/ui/Button'

export default function ContractDetailPage({ params }: { params: { id: string } }) {
  return (
    <DashboardLayout>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900">契約詳細</h1>
        <div className="flex gap-3">
          <Button variant="primary">編集</Button>
          <Button variant="secondary">PDFを開く</Button>
        </div>
      </div>

      {/* 契約基本情報 */}
      <Card className="mb-6">
        <div className="flex justify-between items-start mb-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">東京オフィスビル 5F</h2>
            <p className="text-gray-600">契約番号: C-2025-001</p>
          </div>
          <Badge variant="success">有効契約</Badge>
        </div>

        <div className="grid grid-cols-2 gap-x-8 gap-y-4">
          <div className="flex border-b border-gray-100 pb-3">
            <div className="w-40 text-sm font-medium text-gray-600">契約種別</div>
            <div className="flex-1 text-sm text-gray-900">賃貸借契約</div>
          </div>
          <div className="flex border-b border-gray-100 pb-3">
            <div className="w-40 text-sm font-medium text-gray-600">契約期間</div>
            <div className="flex-1 text-sm text-gray-900">2025-04-01 ～ 2027-03-31</div>
          </div>
          <div className="flex border-b border-gray-100 pb-3">
            <div className="w-40 text-sm font-medium text-gray-600">更新条件</div>
            <div className="flex-1 text-sm text-gray-900">自動更新</div>
          </div>
          <div className="flex border-b border-gray-100 pb-3">
            <div className="w-40 text-sm font-medium text-gray-600">解約予告期限</div>
            <div className="flex-1 text-sm text-gray-900">3ヶ月前</div>
          </div>
        </div>
      </Card>

      <div className="grid grid-cols-2 gap-6 mb-6">
        {/* 物件情報 */}
        <Card>
          <h3 className="text-lg font-semibold mb-4">物件情報</h3>
          <div className="space-y-3">
            <div className="flex border-b border-gray-100 pb-2">
              <div className="w-32 text-sm font-medium text-gray-600">所在地</div>
              <div className="flex-1 text-sm text-gray-900">東京都千代田区丸の内1-1-1</div>
            </div>
            <div className="flex border-b border-gray-100 pb-2">
              <div className="w-32 text-sm font-medium text-gray-600">建物名</div>
              <div className="flex-1 text-sm text-gray-900">東京オフィスビル</div>
            </div>
            <div className="flex border-b border-gray-100 pb-2">
              <div className="w-32 text-sm font-medium text-gray-600">面積</div>
              <div className="flex-1 text-sm text-gray-900">120.50 m²</div>
            </div>
            <div className="flex border-b border-gray-100 pb-2">
              <div className="w-32 text-sm font-medium text-gray-600">用途</div>
              <div className="flex-1 text-sm text-gray-900">事務所</div>
            </div>
          </div>
        </Card>

        {/* 金銭条件 */}
        <Card>
          <h3 className="text-lg font-semibold mb-4">金銭条件</h3>
          <div className="space-y-3">
            <div className="flex border-b border-gray-100 pb-2">
              <div className="w-32 text-sm font-medium text-gray-600">月額賃料</div>
              <div className="flex-1 text-sm text-gray-900 font-semibold">¥500,000</div>
            </div>
            <div className="flex border-b border-gray-100 pb-2">
              <div className="w-32 text-sm font-medium text-gray-600">共益費</div>
              <div className="flex-1 text-sm text-gray-900">¥50,000</div>
            </div>
            <div className="flex border-b border-gray-100 pb-2">
              <div className="w-32 text-sm font-medium text-gray-600">敷金</div>
              <div className="flex-1 text-sm text-gray-900">¥1,500,000</div>
            </div>
            <div className="flex border-b border-gray-100 pb-2">
              <div className="w-32 text-sm font-medium text-gray-600">礼金</div>
              <div className="flex-1 text-sm text-gray-900">¥500,000</div>
            </div>
          </div>
        </Card>
      </div>

      <div className="grid grid-cols-2 gap-6">
        {/* 当事者情報 */}
        <Card>
          <h3 className="text-lg font-semibold mb-4">貸主情報</h3>
          <div className="space-y-3">
            <div className="flex border-b border-gray-100 pb-2">
              <div className="w-32 text-sm font-medium text-gray-600">名称</div>
              <div className="flex-1 text-sm text-gray-900">株式会社丸の内不動産</div>
            </div>
            <div className="flex border-b border-gray-100 pb-2">
              <div className="w-32 text-sm font-medium text-gray-600">住所</div>
              <div className="flex-1 text-sm text-gray-900">東京都千代田区...</div>
            </div>
          </div>

          <h3 className="text-lg font-semibold mt-6 mb-4">借主情報</h3>
          <div className="space-y-3">
            <div className="flex border-b border-gray-100 pb-2">
              <div className="w-32 text-sm font-medium text-gray-600">名称</div>
              <div className="flex-1 text-sm text-gray-900">株式会社サンプル商事</div>
            </div>
            <div className="flex border-b border-gray-100 pb-2">
              <div className="w-32 text-sm font-medium text-gray-600">住所</div>
              <div className="flex-1 text-sm text-gray-900">東京都港区...</div>
            </div>
          </div>
        </Card>

        {/* AI抽出情報 */}
        <Card>
          <h3 className="text-lg font-semibold mb-4">AI抽出情報</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between pb-2 border-b border-gray-100">
              <span className="text-sm text-gray-600">全体信頼度</span>
              <span className="text-lg font-bold text-green-600">95%</span>
            </div>
            <div className="flex items-center justify-between pb-2 border-b border-gray-100">
              <span className="text-sm text-gray-600">検証ステータス</span>
              <Badge variant="success">検証済み</Badge>
            </div>
            <div className="flex items-center justify-between pb-2 border-b border-gray-100">
              <span className="text-sm text-gray-600">最終更新日</span>
              <span className="text-sm text-gray-900">2025-10-01 14:30</span>
            </div>
          </div>

          <div className="mt-6 p-4 bg-blue-50 rounded-lg">
            <p className="text-sm text-blue-800">
              この契約は自動抽出され、手動で検証済みです。
            </p>
          </div>
        </Card>
      </div>
    </DashboardLayout>
  )
}
