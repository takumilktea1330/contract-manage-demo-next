'use client'

import { useState } from 'react'
import DashboardLayout from '@/components/layout/DashboardLayout'
import Card from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import Link from 'next/link'

type FieldConfidence = 'high' | 'medium' | 'low'

interface FormField {
  label: string
  value: string
  confidence: number
  confidenceLevel: FieldConfidence
}

export default function VerifyPage({ params }: { params: { id: string } }) {
  const [activeField, setActiveField] = useState<string | null>(null)
  const [formData, setFormData] = useState({
    // 契約基本情報
    contractNumber: 'C-2025-001',
    contractType: '賃貸借契約',
    startDate: '2025-04-01',
    endDate: '2027-03-31',
    renewalCondition: '自動更新（2年間）',
    cancellationNotice: '3ヶ月前',

    // 物件情報
    propertyName: '東京オフィスビル 5F',
    address: '東京都千代田区丸の内1-1-1',
    area: '120.50 m²',
    usage: '事務所',

    // 貸主情報
    lessorName: '株式会社丸の内不動産',
    lessorAddress: '東京都千代田区丸の内2-2-2',
    lessorPhone: '03-1234-5678',

    // 借主情報
    lesseeName: '株式会社サンプル商事',
    lesseeAddress: '東京都港区赤坂1-1-1',
    lesseePhone: '03-9876-5432',

    // 金銭条件
    rent: '¥500,000',
    commonFee: '¥50,000',
    deposit: '¥1,500,000',
    keyMoney: '¥1,000,000',
    renewalFee: '¥500,000',
    paymentDate: '毎月末日',
  })

  const getConfidenceLevel = (confidence: number): FieldConfidence => {
    if (confidence >= 85) return 'high'
    if (confidence >= 70) return 'medium'
    return 'low'
  }

  const getConfidenceColor = (level: FieldConfidence) => {
    if (level === 'high') return 'text-green-600'
    if (level === 'medium') return 'text-yellow-600'
    return 'text-red-600'
  }

  const getInputStyle = (level: FieldConfidence) => {
    if (level === 'medium') return 'border-yellow-400 bg-yellow-50'
    if (level === 'low') return 'border-red-400 bg-red-50'
    return ''
  }

  const handleChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const handleSave = () => {
    alert('検証完了・保存しました')
  }

  const handleDraft = () => {
    alert('下書き保存しました')
  }

  const scrollToField = (fieldKey: string) => {
    const element = document.getElementById(`field-${fieldKey}`)
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'center' })
      setActiveField(fieldKey)
      // 3秒後にハイライト解除
      setTimeout(() => setActiveField(null), 3000)
    }
  }

  const HighlightText = ({ fieldKey, children }: { fieldKey: string; children: React.ReactNode }) => {
    const isActive = activeField === fieldKey
    return (
      <span
        onClick={() => scrollToField(fieldKey)}
        className={`cursor-pointer transition-all duration-300 ${
          isActive
            ? 'bg-blue-300 ring-2 ring-blue-500'
            : 'bg-yellow-100 hover:bg-yellow-200'
        }`}
        title="クリックして対応する入力欄へ移動"
      >
        {children}
      </span>
    )
  }

  const fields = {
    contract: [
      { key: 'contractNumber', label: '契約番号', confidence: 98 },
      { key: 'contractType', label: '契約種別', confidence: 95, type: 'select' },
      { key: 'startDate', label: '契約開始日', confidence: 99, type: 'date' },
      { key: 'endDate', label: '契約終了日', confidence: 99, type: 'date' },
      { key: 'renewalCondition', label: '更新条件', confidence: 88 },
      { key: 'cancellationNotice', label: '解約通知期限', confidence: 75 },
    ],
    property: [
      { key: 'propertyName', label: '物件名', confidence: 96 },
      { key: 'address', label: '所在地', confidence: 94 },
      { key: 'area', label: '面積', confidence: 92 },
      { key: 'usage', label: '用途', confidence: 90 },
    ],
    lessor: [
      { key: 'lessorName', label: '名称', confidence: 97 },
      { key: 'lessorAddress', label: '住所', confidence: 93 },
      { key: 'lessorPhone', label: '連絡先', confidence: 65 },
    ],
    lessee: [
      { key: 'lesseeName', label: '名称', confidence: 98 },
      { key: 'lesseeAddress', label: '住所', confidence: 95 },
      { key: 'lesseePhone', label: '連絡先', confidence: 88 },
    ],
    financial: [
      { key: 'rent', label: '月額賃料', confidence: 99 },
      { key: 'commonFee', label: '共益費', confidence: 96 },
      { key: 'deposit', label: '敷金', confidence: 98 },
      { key: 'keyMoney', label: '礼金', confidence: 98 },
      { key: 'renewalFee', label: '更新料', confidence: 94 },
      { key: 'paymentDate', label: '支払期日', confidence: 78 },
    ]
  }

  const overallConfidence = 92

  const renderField = (field: any) => {
    const confidenceLevel = getConfidenceLevel(field.confidence)
    const value = formData[field.key as keyof typeof formData]
    const isActive = activeField === field.key

    return (
      <div
        key={field.key}
        id={`field-${field.key}`}
        className={`mb-4 p-3 rounded-lg transition-all duration-300 ${
          isActive ? 'bg-blue-50 ring-2 ring-blue-400' : ''
        }`}
      >
        <label className="block text-sm font-medium text-gray-700 mb-1">
          {field.label}{' '}
          <span className={`${getConfidenceColor(confidenceLevel)} font-semibold`}>
            ({field.confidence}%)
          </span>
          {confidenceLevel !== 'high' && ' ⚠️'}
        </label>

        {field.type === 'select' ? (
          <select
            value={value}
            onChange={(e) => handleChange(field.key, e.target.value)}
            className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-primary ${getInputStyle(confidenceLevel)}`}
          >
            <option>賃貸借契約</option>
            <option>更新合意書</option>
            <option>覚書</option>
          </select>
        ) : (
          <input
            type={field.type || 'text'}
            value={value}
            onChange={(e) => handleChange(field.key, e.target.value)}
            className={`w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-primary ${getInputStyle(confidenceLevel)}`}
          />
        )}

        {confidenceLevel === 'low' && (
          <small className="text-red-700 text-xs">
            ※信頼度が低いため必ず確認してください
          </small>
        )}
        {confidenceLevel === 'medium' && (
          <small className="text-yellow-700 text-xs">
            ※信頼度が低いため確認してください
          </small>
        )}
      </div>
    )
  }

  return (
    <DashboardLayout>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900">抽出結果検証</h1>
        <div className="flex gap-3">
          <Link href="/upload">
            <Button variant="secondary">戻る</Button>
          </Link>
          <Button variant="success" onClick={handleSave}>検証完了・保存</Button>
        </div>
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
        <p className="text-sm text-blue-800">
          <strong>検証手順:</strong> 左側のPDF原本を確認しながら、右側の抽出結果を検証してください。信頼度が低い項目（黄色・赤色）は特に注意して確認してください。
        </p>
      </div>

      {/* サイドバイサイド表示 */}
      <div className="grid grid-cols-2 gap-6">
        {/* PDF表示エリア */}
        <div>
          <Card>
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">契約書原本</h3>
              <div className="flex gap-2">
                <Button variant="secondary" className="text-xs py-1 px-2">拡大</Button>
                <Button variant="secondary" className="text-xs py-1 px-2">縮小</Button>
                <Button variant="secondary" className="text-xs py-1 px-2">← 前</Button>
                <Button variant="secondary" className="text-xs py-1 px-2">次 →</Button>
              </div>
            </div>

            <div className="bg-gray-200 border border-gray-300 rounded p-4 min-h-[700px]">
              {/* PDF風の表示 */}
              <div className="bg-white shadow-lg p-8 text-sm leading-relaxed">
                <div className="text-center mb-8">
                  <h2 className="text-2xl font-bold mb-2">賃貸借契約書</h2>
                  <p className="text-sm text-gray-600">
                    契約番号: <HighlightText fieldKey="contractNumber">C-2025-001</HighlightText>
                  </p>
                </div>

                <div className="space-y-6">
                  <section>
                    <p className="mb-3">
                      貸主　<HighlightText fieldKey="lessorName">株式会社丸の内不動産</HighlightText>（以下「甲」という。）と<br />
                      借主　<HighlightText fieldKey="lesseeName">株式会社サンプル商事</HighlightText>（以下「乙」という。）は、<br />
                      本日、次の条件により賃貸借契約を締結した。
                    </p>
                  </section>

                  <section>
                    <h3 className="font-bold mb-2">第1条（物件の表示）</h3>
                    <div className="ml-4 space-y-1">
                      <p>所在地：<HighlightText fieldKey="address">東京都千代田区丸の内1-1-1</HighlightText></p>
                      <p>建物名：<HighlightText fieldKey="propertyName">東京オフィスビル 5F</HighlightText></p>
                      <p>面積：<HighlightText fieldKey="area">120.50 m²</HighlightText></p>
                      <p>用途：<HighlightText fieldKey="usage">事務所</HighlightText></p>
                    </div>
                  </section>

                  <section>
                    <h3 className="font-bold mb-2">第2条（契約期間）</h3>
                    <div className="ml-4">
                      <p>契約期間は、<HighlightText fieldKey="startDate">2025年4月1日</HighlightText>から<HighlightText fieldKey="endDate">2027年3月31日</HighlightText>までとする。</p>
                      <p className="mt-2">本契約は、期間満了の<HighlightText fieldKey="cancellationNotice">3ヶ月前</HighlightText>までに書面による解約の申し出がない場合、同一条件にて<HighlightText fieldKey="renewalCondition">2年間自動更新</HighlightText>されるものとする。</p>
                    </div>
                  </section>

                  <section>
                    <h3 className="font-bold mb-2">第3条（賃料等）</h3>
                    <div className="ml-4 space-y-1">
                      <p>月額賃料：<HighlightText fieldKey="rent">金500,000円</HighlightText></p>
                      <p>共益費：<HighlightText fieldKey="commonFee">金50,000円</HighlightText></p>
                      <p>敷金：<HighlightText fieldKey="deposit">金1,500,000円</HighlightText></p>
                      <p>礼金：<HighlightText fieldKey="keyMoney">金1,000,000円</HighlightText></p>
                      <p className="mt-2">賃料の支払いは、<HighlightText fieldKey="paymentDate">毎月末日</HighlightText>までに翌月分を甲の指定する口座に振り込むものとする。</p>
                      <p className="text-xs text-gray-500 mt-2">更新料は<HighlightText fieldKey="renewalFee">金500,000円</HighlightText>とする。</p>
                    </div>
                  </section>

                  <section>
                    <h3 className="font-bold mb-2">第4条（解約予告）</h3>
                    <div className="ml-4">
                      <p>乙が本契約を中途解約する場合は、解約希望日の<HighlightText fieldKey="cancellationNotice">3ヶ月前</HighlightText>までに書面にて甲に通知しなければならない。</p>
                    </div>
                  </section>

                  <section className="mt-8 pt-8 border-t border-gray-300">
                    <div className="grid grid-cols-2 gap-8">
                      <div>
                        <p className="font-bold mb-2">貸主（甲）</p>
                        <p><HighlightText fieldKey="lessorName">株式会社丸の内不動産</HighlightText></p>
                        <p className="text-sm"><HighlightText fieldKey="lessorAddress">東京都千代田区丸の内2-2-2</HighlightText></p>
                        <p className="text-sm">TEL: <HighlightText fieldKey="lessorPhone">03-1234-5678</HighlightText></p>
                      </div>
                      <div>
                        <p className="font-bold mb-2">借主（乙）</p>
                        <p><HighlightText fieldKey="lesseeName">株式会社サンプル商事</HighlightText></p>
                        <p className="text-sm"><HighlightText fieldKey="lesseeAddress">東京都港区赤坂1-1-1</HighlightText></p>
                        <p className="text-sm">TEL: <HighlightText fieldKey="lesseePhone">03-9876-5432</HighlightText></p>
                      </div>
                    </div>
                  </section>
                </div>

                <div className="mt-8 text-center text-xs text-gray-500">
                  <p>ページ 1 / 3</p>
                </div>
              </div>
            </div>

            <div className="mt-3 text-center">
              <p className="text-xs text-gray-600">賃貸借契約書_C-2025-001.pdf</p>
            </div>
          </Card>
        </div>

        {/* 抽出結果フォーム */}
        <div>
          <Card>
            <h3 className="text-lg font-semibold mb-4">
              抽出結果（全体信頼度: <span className="text-green-600 font-bold">{overallConfidence}%</span>）
            </h3>

            <div className="max-h-[600px] overflow-y-auto pr-2">
              {/* 契約基本情報 */}
              <div className="mb-6">
                <h4 className="text-sm font-semibold text-primary mb-3">契約基本情報</h4>
                {fields.contract.map(renderField)}
              </div>

              {/* 物件情報 */}
              <div className="mb-6">
                <h4 className="text-sm font-semibold text-primary mb-3">物件情報</h4>
                {fields.property.map(renderField)}
              </div>

              {/* 貸主情報 */}
              <div className="mb-6">
                <h4 className="text-sm font-semibold text-primary mb-3">貸主情報</h4>
                {fields.lessor.map(renderField)}
              </div>

              {/* 借主情報 */}
              <div className="mb-6">
                <h4 className="text-sm font-semibold text-primary mb-3">借主情報</h4>
                {fields.lessee.map(renderField)}
              </div>

              {/* 金銭条件 */}
              <div className="mb-6">
                <h4 className="text-sm font-semibold text-primary mb-3">金銭条件</h4>
                {fields.financial.map(renderField)}
              </div>
            </div>

            <div className="mt-6 pt-6 border-t-2 border-gray-200">
              <Button variant="success" className="w-full mb-3" onClick={handleSave}>
                検証完了・保存
              </Button>
              <Button variant="secondary" className="w-full" onClick={handleDraft}>
                下書き保存
              </Button>
            </div>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  )
}
