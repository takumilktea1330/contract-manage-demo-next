'use client'

import { useState, useEffect, useRef } from 'react'
import DashboardLayout from '@/components/layout/DashboardLayout'
import Card from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import Badge from '@/components/ui/Badge'
import Link from 'next/link'

export default function ContractsPage() {
  const [activeTab, setActiveTab] = useState<'normal' | 'ai'>('normal')
  const [aiQuery, setAiQuery] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [isSearching, setIsSearching] = useState(false)
  const [showResults, setShowResults] = useState(false)
  const [aiResponse, setAiResponse] = useState('')
  const [isTypingResponse, setIsTypingResponse] = useState(false)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const contracts = [
    { id: 'C-2025-001', property: '東京オフィスビル 5F', period: '2025-04-01 ～ 2027-03-31', rent: '¥500,000', status: '有効' },
    { id: 'C-2025-002', property: '渋谷店舗 1F', period: '2025-03-15 ～ 2026-03-14', rent: '¥800,000', status: '有効' },
    { id: 'C-2024-125', property: '品川オフィス 3F', period: '2024-11-01 ～ 2025-10-31', rent: '¥450,000', status: '有効' },
    { id: 'C-2024-089', property: '横浜倉庫', period: '2024-04-01 ～ 2026-03-31', rent: '¥350,000', status: '有効' },
  ]

  const aiResults = [
    { id: 'C-2024-089', property: '渋谷店舗 1F', endDate: '2026-03-31', rent: '¥800,000', relevance: 98 },
    { id: 'C-2024-102', property: '品川オフィス 7F', endDate: '2026-03-31', rent: '¥620,000', relevance: 96 },
    { id: 'C-2024-115', property: '横浜倉庫A棟', endDate: '2026-03-31', rent: '¥450,000', relevance: 95 },
  ]

  const exampleQueries = [
    '来年3月末に満了する賃貸契約を教えて',
    '敷金が賃料の3ヶ月分以上の契約はどれですか？',
    '渋谷エリアの物件で賃料が50万円以上の契約を教えて',
  ]

  // タイピングアニメーション
  const typeText = async (text: string) => {
    setIsTyping(true)
    setAiQuery('')

    for (let i = 0; i <= text.length; i++) {
      setAiQuery(text.slice(0, i))
      await new Promise(resolve => setTimeout(resolve, 50))
    }

    setIsTyping(false)
  }

  // テキストエリアクリック時に例文をタイピング
  const handleTextareaClick = () => {
    if (!aiQuery && !isTyping) {
      const randomQuery = exampleQueries[Math.floor(Math.random() * exampleQueries.length)]
      typeText(randomQuery)
    }
  }

  // AI回答をタイピング表示
  const typeResponse = async (text: string) => {
    setIsTypingResponse(true)
    setAiResponse('')

    for (let i = 0; i <= text.length; i++) {
      setAiResponse(text.slice(0, i))
      await new Promise(resolve => setTimeout(resolve, 30))
    }

    setIsTypingResponse(false)
  }

  // 検索ボタンクリック
  const handleSearch = async () => {
    if (!aiQuery) {
      alert('質問を入力してください')
      return
    }

    setIsSearching(true)
    setShowResults(false)
    setAiResponse('')

    // 検索中のアニメーション
    await new Promise(resolve => setTimeout(resolve, 1500))

    setIsSearching(false)
    setShowResults(true)

    // AI回答をタイピング表示
    const responseText = '2026年3月末（2026-03-31）に満了する賃貸契約は5件見つかりました。以下がその一覧です：\n• C-2024-089: 渋谷店舗 1F（賃料: ¥800,000）\n• C-2024-102: 品川オフィス 7F（賃料: ¥620,000）\n• C-2024-115: 横浜倉庫A棟（賃料: ¥450,000）'
    await typeResponse(responseText)
  }

  // クリアボタン
  const handleClear = () => {
    setAiQuery('')
    setShowResults(false)
    setIsSearching(false)
    setAiResponse('')
    setIsTypingResponse(false)
  }

  // 質問例ボタンクリック
  const handleExampleClick = (query: string) => {
    typeText(query)
  }

  return (
    <DashboardLayout>
      <h1 className="text-3xl font-bold text-gray-900 mb-6">契約検索</h1>

      {/* タブ */}
      <div className="border-b-2 border-gray-200 mb-6">
        <div className="flex gap-2">
          <button
            onClick={() => setActiveTab('normal')}
            className={`px-6 py-3 font-semibold transition-colors ${
              activeTab === 'normal'
                ? 'text-primary border-b-4 border-primary -mb-0.5'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            通常検索
          </button>
          <button
            onClick={() => setActiveTab('ai')}
            className={`px-6 py-3 font-semibold transition-colors ${
              activeTab === 'ai'
                ? 'text-primary border-b-4 border-primary -mb-0.5'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            AI検索
          </button>
        </div>
      </div>

      {activeTab === 'normal' ? (
        <>
          {/* 通常検索 */}
          <Card className="mb-6">
            <h3 className="font-semibold mb-4">検索条件</h3>

            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">キーワード</label>
                <input
                  type="text"
                  placeholder="契約番号、物件名など"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-primary"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">契約種別</label>
                <select className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-primary">
                  <option>すべて</option>
                  <option>賃貸借契約</option>
                  <option>更新合意書</option>
                  <option>覚書</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">契約開始日（From）</label>
                <input
                  type="date"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-primary"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">契約開始日（To）</label>
                <input
                  type="date"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-primary"
                />
              </div>
            </div>

            <div className="flex gap-3">
              <Button variant="primary" className="flex-1">検索</Button>
              <Button variant="secondary">クリア</Button>
            </div>
          </Card>

          {/* 検索結果 */}
          <Card>
            <h2 className="text-xl font-semibold mb-4">検索結果 ({contracts.length}件)</h2>

            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">契約番号</th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">物件名</th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">契約期間</th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">賃料</th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">ステータス</th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700"></th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {contracts.map((contract) => (
                    <tr key={contract.id} className="hover:bg-gray-50">
                      <td className="px-4 py-3 text-sm">{contract.id}</td>
                      <td className="px-4 py-3 text-sm">{contract.property}</td>
                      <td className="px-4 py-3 text-sm">{contract.period}</td>
                      <td className="px-4 py-3 text-sm font-medium">{contract.rent}</td>
                      <td className="px-4 py-3 text-sm">
                        <Badge variant="success">{contract.status}</Badge>
                      </td>
                      <td className="px-4 py-3 text-sm">
                        <Link href={`/contracts/${contract.id}`} className="text-primary hover:underline">
                          詳細
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="flex gap-3 mt-6">
              <Button variant="secondary">CSV出力</Button>
              <Button variant="secondary">Excel出力</Button>
            </div>
          </Card>
        </>
      ) : (
        <>
          {/* AI検索 */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <p className="text-sm text-blue-800">
              <strong>AI検索とは:</strong> 自然言語で質問すると、AIが契約書の内容を理解して関連する契約情報を検索・回答します。
            </p>
          </div>

          <Card className="mb-6">
            <h3 className="font-semibold mb-4">質問を入力してください</h3>

            <div className="relative">
              <textarea
                ref={textareaRef}
                rows={4}
                value={aiQuery}
                onChange={(e) => setAiQuery(e.target.value)}
                onClick={handleTextareaClick}
                placeholder="クリックすると例文が自動入力されます... または直接入力してください"
                className={`w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-primary resize-none ${
                  isTyping ? 'cursor-wait' : ''
                }`}
                disabled={isTyping}
              />
              {isTyping && (
                <div className="absolute bottom-3 right-3">
                  <div className="flex gap-1">
                    <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                    <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                    <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                  </div>
                </div>
              )}
            </div>

            <div className="flex gap-3 mt-4">
              <Button
                variant="primary"
                className="flex-1"
                onClick={handleSearch}
                disabled={isTyping || isSearching || !aiQuery}
              >
                {isSearching ? (
                  <span className="flex items-center justify-center gap-2">
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    検索中...
                  </span>
                ) : (
                  '検索'
                )}
              </Button>
              <Button variant="secondary" onClick={handleClear}>クリア</Button>
            </div>

            <div className="mt-6">
              <h4 className="text-sm text-gray-600 mb-3">よく使う質問例:</h4>
              <div className="flex flex-wrap gap-2">
                <Button
                  variant="secondary"
                  className="text-sm py-2"
                  onClick={() => handleExampleClick('来年3月末に満了する賃貸契約を教えて')}
                  disabled={isTyping || isSearching}
                >
                  来年満了する契約
                </Button>
                <Button
                  variant="secondary"
                  className="text-sm py-2"
                  onClick={() => handleExampleClick('敷金が賃料の3ヶ月分以上の契約はどれですか？')}
                  disabled={isTyping || isSearching}
                >
                  敷金が高い契約
                </Button>
                <Button
                  variant="secondary"
                  className="text-sm py-2"
                  onClick={() => handleExampleClick('渋谷エリアの物件で賃料が50万円以上の契約を教えて')}
                  disabled={isTyping || isSearching}
                >
                  渋谷エリアの高額契約
                </Button>
              </div>
            </div>
          </Card>

          {/* AI回答 */}
          {showResults && (
            <>
              <Card className="mb-6 animate-fadeIn">
                <div className="bg-gray-50 border-l-4 border-primary p-5 rounded">
                  <h3 className="text-primary font-semibold mb-3">💬 AIの回答</h3>
                  <div className="text-gray-800 space-y-3">
                    <p><strong>質問:</strong> 「{aiQuery}」</p>
                    <div className="whitespace-pre-wrap">
                      {aiResponse}
                      {isTypingResponse && (
                        <span className="inline-block w-2 h-4 ml-1 bg-primary animate-pulse"></span>
                      )}
                    </div>
                  </div>
                </div>
              </Card>

              {/* 関連契約一覧 */}
              {!isTypingResponse && (
                <Card className="animate-fadeIn" style={{ animationDelay: '200ms' }}>
                  <h3 className="font-semibold mb-4">関連する契約（{aiResults.length}件）</h3>

                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">関連度</th>
                        <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">契約番号</th>
                        <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">物件名</th>
                        <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">満了日</th>
                        <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">賃料</th>
                        <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700"></th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {aiResults.map((result) => (
                        <tr key={result.id} className="hover:bg-gray-50">
                          <td className="px-4 py-3 text-sm">
                            <span className="text-green-600 font-bold">{result.relevance}%</span>
                          </td>
                          <td className="px-4 py-3 text-sm">{result.id}</td>
                          <td className="px-4 py-3 text-sm">{result.property}</td>
                          <td className="px-4 py-3 text-sm">{result.endDate}</td>
                          <td className="px-4 py-3 text-sm font-medium">{result.rent}</td>
                          <td className="px-4 py-3 text-sm">
                            <Link href={`/contracts/${result.id}`} className="text-primary hover:underline">
                              詳細
                            </Link>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                </Card>
              )}
            </>
          )}
        </>
      )}
    </DashboardLayout>
  )
}
