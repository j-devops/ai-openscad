import { useState } from 'react'
import Editor from '@monaco-editor/react'
import { submitRenderJob, getPreviewUrl } from '../../services/api'
import './CodeEditor.css'

interface CodeEditorProps {
  code: string
  onChange: (code: string) => void
  onRenderComplete: (jobId: string | null) => void
  onLog?: (type: 'info' | 'warning' | 'error' | 'success', message: string) => void
}

export default function CodeEditor({ code, onChange, onRenderComplete, onLog }: CodeEditorProps) {
  const [isRendering, setIsRendering] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleRender = async () => {
    setIsRendering(true)
    setError(null)
    onLog?.('info', 'Starting OpenSCAD compilation and render...')

    try {
      const result = await submitRenderJob(code)
      onLog?.('info', `Render job queued: ${result.job_id}`)

      // Poll for completion
      const pollInterval = setInterval(async () => {
        try {
          const response = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/render/${result.job_id}`)
          const data = await response.json()

          if (data.status === 'completed') {
            clearInterval(pollInterval)
            // Check if we have STL file available
            if (data.stl_url) {
              onRenderComplete(result.job_id)
              onLog?.('success', 'OpenSCAD compilation successful - STL file ready')
            } else if (data.error) {
              const errorMsg = `Rendering failed: ${data.error}`
              setError(errorMsg)
              onLog?.('error', errorMsg)
              onRenderComplete(null)
            } else {
              const errorMsg = 'Rendering completed but no STL was generated'
              setError(errorMsg)
              onLog?.('warning', errorMsg)
              onRenderComplete(null)
            }
            setIsRendering(false)
          } else if (data.status === 'failed') {
            clearInterval(pollInterval)
            const errorMsg = data.error || 'Rendering failed'
            setError(errorMsg)
            onLog?.('error', `Compilation failed: ${errorMsg}`)
            onRenderComplete(null)
            setIsRendering(false)
          }
        } catch (err) {
          clearInterval(pollInterval)
          setError('Failed to check render status')
          onLog?.('error', 'Failed to check render status')
          setIsRendering(false)
        }
      }, 1000)

      // Timeout after 2 minutes
      setTimeout(() => {
        clearInterval(pollInterval)
        if (isRendering) {
          setIsRendering(false)
          setError('Rendering timeout')
          onLog?.('error', 'Rendering timeout (120s exceeded)')
        }
      }, 120000)

    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 'Failed to submit render job'
      setError(errorMsg)
      onLog?.('error', `Failed to submit render job: ${errorMsg}`)
      setIsRendering(false)
    }
  }

  return (
    <div className="code-editor">
      <div className="editor-toolbar">
        <h3>OpenSCAD Code</h3>
        <button
          onClick={handleRender}
          disabled={isRendering || !code.trim()}
          className="render-button"
        >
          {isRendering ? 'Rendering...' : 'Render'}
        </button>
      </div>
      <div className="editor-container">
        <Editor
          height="100%"
          defaultLanguage="cpp"
          value={code}
          onChange={(value) => onChange(value || '')}
          theme="vs-dark"
          options={{
            minimap: { enabled: false },
            fontSize: 14,
            lineNumbers: 'on',
            scrollBeyondLastLine: false,
          }}
        />
      </div>
      {error && <div className="editor-error">{error}</div>}
    </div>
  )
}
