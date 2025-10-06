'use client'

import { useState, useEffect, useRef } from 'react'
import DashboardLayout from '@/components/layout/DashboardLayout'
import Card from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import Badge from '@/components/ui/Badge'
import ProgressBar from '@/components/ui/ProgressBar'
import Link from 'next/link'

type FileStatus = {
  id: number
  name: string
  size: string
  status: string
  progress: number
  steps: Array<{ name: string; status: string }>
  startedAt?: number
}

export default function UploadPage() {
  const [files, setFiles] = useState<FileStatus[]>([])
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  // ファイル処理の自動進行
  useEffect(() => {
    const interval = setInterval(() => {
      setFiles(prevFiles =>
        prevFiles.map(file => {
          if (file.progress >= 100) return file

          const newProgress = Math.min(file.progress + Math.random() * 8, 100)

          let newStatus = file.status
          let newSteps = [...file.steps]

          // ステータス更新ロジック
          if (newProgress < 25) {
            newStatus = 'アップロード中'
            newSteps = [
              { name: 'アップロード中', status: 'processing' },
              { name: 'OCR処理', status: 'waiting' },
              { name: 'AI抽出', status: 'waiting' },
              { name: '検証', status: 'waiting' },
            ]
          } else if (newProgress < 50) {
            newStatus = 'OCR処理中'
            newSteps = [
              { name: 'アップロード完了', status: 'completed' },
              { name: 'OCR処理中', status: 'processing' },
              { name: 'AI抽出', status: 'waiting' },
              { name: '検証', status: 'waiting' },
            ]
          } else if (newProgress < 90) {
            newStatus = 'AI抽出中'
            newSteps = [
              { name: 'アップロード完了', status: 'completed' },
              { name: 'OCR完了', status: 'completed' },
              { name: 'AI抽出中', status: 'processing' },
              { name: '検証', status: 'waiting' },
            ]
          } else {
            newStatus = '抽出完了'
            newSteps = [
              { name: 'アップロード完了', status: 'completed' },
              { name: 'OCR完了', status: 'completed' },
              { name: 'AI抽出完了', status: 'completed' },
              { name: '検証待ち', status: 'warning' },
            ]
          }

          return {
            ...file,
            progress: newProgress,
            status: newStatus,
            steps: newSteps
          }
        })
      )
    }, 500)

    return () => clearInterval(interval)
  }, [])

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setSelectedFile(file)
    }
  }

  const handleUpload = () => {
    if (!selectedFile) {
      alert('ファイルを選択してください')
      return
    }

    const newFile: FileStatus = {
      id: Date.now(),
      name: selectedFile.name,
      size: (selectedFile.size / (1024 * 1024)).toFixed(2) + ' MB',
      status: 'アップロード中',
      progress: 0,
      steps: [
        { name: 'アップロード中', status: 'processing' },
        { name: 'OCR処理', status: 'waiting' },
        { name: 'AI抽出', status: 'waiting' },
        { name: '検証', status: 'waiting' },
      ],
      startedAt: Date.now()
    }

    setFiles(prev => [newFile, ...prev])
    setSelectedFile(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    const file = e.dataTransfer.files[0]
    if (file && file.type === 'application/pdf') {
      setSelectedFile(file)
    } else {
      alert('PDFファイルのみ対応しています')
    }
  }

  return (
    <DashboardLayout>
      <h1 className="text-3xl font-bold text-gray-900 mb-6">契約書アップロード</h1>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
        <p className="text-sm text-blue-800">
          <strong>対応形式:</strong> PDF形式のみ対応しています。1ファイル最大20MB、最大10ファイルまで同時アップロード可能です。
        </p>
      </div>

      {/* アップロードエリア */}
      <Card className="mb-6">
        <div
          onDragOver={handleDragOver}
          onDrop={handleDrop}
          className="border-2 border-dashed border-primary rounded-lg p-12 text-center bg-blue-50/30 hover:bg-blue-50/50 transition-colors cursor-pointer"
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf"
            onChange={handleFileSelect}
            className="hidden"
            id="file-input"
          />
          <svg className="mx-auto h-16 w-16 text-primary mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
          <p className="text-lg font-semibold text-primary mb-2">ファイルをドラッグ&ドロップ</p>
          <p className="text-gray-600 mb-4">または</p>
          <label htmlFor="file-input">
            <Button variant="primary" type="button" onClick={() => fileInputRef.current?.click()}>
              ファイルを選択
            </Button>
          </label>
          {selectedFile && (
            <div className="mt-4 p-3 bg-white rounded-lg border border-green-300">
              <p className="text-sm text-gray-700">
                <span className="font-semibold text-green-600">選択済み:</span> {selectedFile.name}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                サイズ: {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
              </p>
            </div>
          )}
        </div>

        <div className="mt-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            契約書種別（任意）
          </label>
          <select className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-primary">
            <option>自動判定</option>
            <option>賃貸借契約書</option>
            <option>更新合意書</option>
            <option>覚書</option>
          </select>
          <p className="text-xs text-gray-500 mt-2">
            ※AIが自動判定しますが、事前に指定することで精度が向上します
          </p>
        </div>

        <Button
          variant="success"
          className="w-full mt-6"
          onClick={handleUpload}
          disabled={!selectedFile}
        >
          {selectedFile ? 'アップロード開始' : 'ファイルを選択してください'}
        </Button>
      </Card>

      {/* 処理中のファイル */}
      <Card>
        <h2 className="text-xl font-semibold mb-6">処理中のファイル</h2>

        {files.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <p>アップロードされたファイルはありません</p>
            <p className="text-sm mt-2">上のエリアからファイルをアップロードしてください</p>
          </div>
        ) : (
          <div className="space-y-6">
            {files.map((file) => (
              <div key={file.id} className="border border-gray-200 rounded-lg p-5 bg-white shadow-sm">
                <div className="flex justify-between items-center mb-4">
                  <div>
                    <div className="font-semibold text-gray-900">{file.name}</div>
                    <div className="text-sm text-gray-500">ファイルサイズ: {file.size}</div>
                  </div>
                  <Badge
                    variant={
                      file.status === '抽出完了' ? 'success' :
                      file.status.includes('処理中') || file.status.includes('抽出中') || file.status.includes('アップロード中') ? 'info' :
                      'warning'
                    }
                  >
                    {file.status}
                  </Badge>
                </div>

                <ProgressBar
                  progress={Math.round(file.progress)}
                  label={file.status}
                  className="mb-4"
                />

                {/* ステップ表示 */}
                <div className="grid grid-cols-4 gap-2">
                  {file.steps.map((step, idx) => (
                    <div
                      key={idx}
                      className={`text-center py-2 px-3 rounded text-xs font-medium transition-all duration-300 ${
                        step.status === 'completed'
                          ? 'bg-green-100 text-green-800'
                          : step.status === 'processing'
                          ? 'bg-blue-100 text-blue-800 animate-pulse'
                          : step.status === 'warning'
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-gray-100 text-gray-600'
                      }`}
                    >
                      {step.status === 'completed' && '✓ '}
                      {step.status === 'processing' && '▶ '}
                      {step.status === 'warning' && '⚠ '}
                      {step.name}
                    </div>
                  ))}
                </div>

                {file.status === '抽出完了' && (
                  <div className="flex gap-3 mt-4">
                    <Link href={`/contracts/${file.id}/verify`} className="flex-1">
                      <Button variant="primary" className="w-full">検証画面へ</Button>
                    </Link>
                    <Link href={`/contracts/${file.id}`}>
                      <Button variant="secondary">詳細を見る</Button>
                    </Link>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </Card>
    </DashboardLayout>
  )
}
