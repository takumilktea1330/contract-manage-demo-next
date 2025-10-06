'use client'

import { useState, useRef } from 'react'
import DashboardLayout from '@/components/layout/DashboardLayout'
import Card from '@/components/ui/Card'
import Button from '@/components/ui/Button'

export default function AnalysisPage() {
  const [query, setQuery] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [showResults, setShowResults] = useState(false)
  const [aiResponse, setAiResponse] = useState('')
  const [isTypingResponse, setIsTypingResponse] = useState(false)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const exampleQueries = [
    'A社がオーナーの物件の、一店舗あたりの賃料平均を計算して',
    '2024年に契約した物件の敷金平均は？',
    '渋谷エリアの物件の平均賃料を教えて',
  ]

  // タイピングアニメーション（質問）
  const typeText = async (text: string) => {
    setIsTyping(true)
    setQuery('')

    for (let i = 0; i <= text.length; i++) {
      setQuery(text.slice(0, i))
      await new Promise(resolve => setTimeout(resolve, 50))
    }

    setIsTyping(false)
  }

  // タイピングアニメーション（回答）
  const typeResponse = async (text: string) => {
    setIsTypingResponse(true)
    setAiResponse('')

    for (let i = 0; i <= text.length; i++) {
      setAiResponse(text.slice(0, i))
      await new Promise(resolve => setTimeout(resolve, 30))
    }

    setIsTypingResponse(false)
  }

  // テキストエリアクリック
  const handleTextareaClick = () => {
    if (!query && !isTyping) {
      const randomQuery = exampleQueries[Math.floor(Math.random() * exampleQueries.length)]
      typeText(randomQuery)
    }
  }

  // 分析実行
  const handleAnalyze = async () => {
    if (!query) {
      alert('分析内容を入力してください')
      return
    }

    setIsAnalyzing(true)
    setShowResults(false)
    setAiResponse('')

    // 分析中
    await new Promise(resolve => setTimeout(resolve, 1500))

    setIsAnalyzing(false)
    setShowResults(true)

    // AI回答をタイピング表示
    const responseText = 'A社がオーナーの物件は23件あり、平均賃料は¥584,348です。賃料合計は月額¥13,440,000となっています。'
    await typeResponse(responseText)
  }

  // クリア
  const handleClear = () => {
    setQuery('')
    setShowResults(false)
    setIsAnalyzing(false)
    setAiResponse('')
    setIsTypingResponse(false)
  }

  // 質問例クリック
  const handleExampleClick = (text: string) => {
    typeText(text)
  }

  return (
    <DashboardLayout>
      <h1 className="text-3xl font-bold text-gray-900 mb-6">AI契約分析</h1>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
        <p className="text-sm text-blue-800">
          <strong>AI分析とは:</strong> 自然言語で質問すると、AIが契約データを分析して統計情報やグラフを生成します。
        </p>
      </div>

      {/* 質問入力 */}
      <Card className="mb-6">
        <h3 className="font-semibold mb-4">分析したい内容を入力してください</h3>

        <div className="relative">
          <textarea
            ref={textareaRef}
            rows={4}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
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
            onClick={handleAnalyze}
            disabled={isTyping || isAnalyzing || !query}
          >
            {isAnalyzing ? (
              <span className="flex items-center justify-center gap-2">
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                分析中...
              </span>
            ) : (
              '分析を実行'
            )}
          </Button>
          <Button variant="secondary" onClick={handleClear}>クリア</Button>
        </div>

        <div className="mt-6">
          <h4 className="text-sm text-gray-600 mb-3">よく使う分析例:</h4>
          <div className="flex flex-wrap gap-2">
            <Button
              variant="secondary"
              className="text-sm py-2"
              onClick={() => handleExampleClick('A社がオーナーの物件の、一店舗あたりの賃料平均を計算して')}
              disabled={isTyping || isAnalyzing}
            >
              エリア別の平均賃料
            </Button>
            <Button
              variant="secondary"
              className="text-sm py-2"
              onClick={() => handleExampleClick('2024年に契約した物件の敷金平均は？')}
              disabled={isTyping || isAnalyzing}
            >
              契約期間の分布
            </Button>
            <Button
              variant="secondary"
              className="text-sm py-2"
              onClick={() => handleExampleClick('渋谷エリアの物件の平均賃料を教えて')}
              disabled={isTyping || isAnalyzing}
            >
              エリア別平均賃料
            </Button>
          </div>
        </div>
      </Card>

      {/* 分析結果 */}
      {showResults && (
        <Card className="mb-6 animate-fadeIn">
          <div className="bg-gray-50 border-l-4 border-primary p-5 rounded mb-6">
            <h3 className="text-primary font-semibold mb-3">💬 AIの分析結果</h3>
            <div className="text-gray-800 space-y-3">
              <p><strong>質問:</strong> 「{query}」</p>
              <div className="whitespace-pre-wrap">
                {aiResponse}
                {isTypingResponse && (
                  <span className="inline-block w-2 h-4 ml-1 bg-primary animate-pulse"></span>
                )}
              </div>
            </div>
          </div>

          {/* 統計カード */}
          {!isTypingResponse && (
            <>
              <div className="grid grid-cols-3 gap-6 mb-6 animate-fadeIn" style={{ animationDelay: '200ms' }}>
                <div className="border border-gray-200 rounded-lg p-6 text-center">
                  <div className="text-sm text-gray-600 mb-2">対象物件数</div>
                  <div className="text-4xl font-bold text-primary">23件</div>
                </div>
                <div className="border border-gray-200 rounded-lg p-6 text-center border-l-4 border-l-green-500">
                  <div className="text-sm text-gray-600 mb-2">賃料平均</div>
                  <div className="text-4xl font-bold text-green-600">¥584,348</div>
                </div>
                <div className="border border-gray-200 rounded-lg p-6 text-center">
                  <div className="text-sm text-gray-600 mb-2">賃料合計（月額）</div>
                  <div className="text-4xl font-bold text-gray-700">¥13,440,000</div>
                </div>
              </div>

              {/* 詳細データ */}
              <div className="animate-fadeIn" style={{ animationDelay: '400ms' }}>
                <h4 className="font-semibold mb-3">詳細データ</h4>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-2 text-left font-semibold">契約番号</th>
                        <th className="px-4 py-2 text-left font-semibold">物件名</th>
                        <th className="px-4 py-2 text-left font-semibold">面積</th>
                        <th className="px-4 py-2 text-left font-semibold">賃料</th>
                        <th className="px-4 py-2 text-left font-semibold">坪単価</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      <tr className="hover:bg-gray-50">
                        <td className="px-4 py-2">C-2024-089</td>
                        <td className="px-4 py-2">渋谷店舗 1F</td>
                        <td className="px-4 py-2">85.30 m²</td>
                        <td className="px-4 py-2 font-medium">¥800,000</td>
                        <td className="px-4 py-2">¥30,987</td>
                      </tr>
                      <tr className="hover:bg-gray-50">
                        <td className="px-4 py-2">C-2024-102</td>
                        <td className="px-4 py-2">品川オフィス 7F</td>
                        <td className="px-4 py-2">120.50 m²</td>
                        <td className="px-4 py-2 font-medium">¥620,000</td>
                        <td className="px-4 py-2">¥17,009</td>
                      </tr>
                    </tbody>
                  </table>
                </div>

                <div className="flex gap-3 mt-6">
                  <Button variant="secondary">CSV出力</Button>
                  <Button variant="secondary">グラフ表示</Button>
                </div>
              </div>
            </>
          )}
        </Card>
      )}

      {/* 分析履歴 */}
      <Card>
        <h2 className="text-xl font-semibold mb-4">最近の分析履歴</h2>
        <div className="space-y-3">
          <div className="flex justify-between items-center p-3 bg-gray-50 rounded hover:bg-gray-100 cursor-pointer">
            <div>
              <div className="font-medium text-gray-900">A社がオーナーの物件の平均賃料</div>
              <div className="text-sm text-gray-600">2025-10-05 15:30</div>
            </div>
            <Button variant="secondary" className="text-sm">再実行</Button>
          </div>
          <div className="flex justify-between items-center p-3 bg-gray-50 rounded hover:bg-gray-100 cursor-pointer">
            <div>
              <div className="font-medium text-gray-900">渋谷エリアの物件一覧</div>
              <div className="text-sm text-gray-600">2025-10-04 10:15</div>
            </div>
            <Button variant="secondary" className="text-sm">再実行</Button>
          </div>
        </div>
      </Card>
    </DashboardLayout>
  )
}
