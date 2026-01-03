import { useState } from 'react'
import { generateCode } from '../../services/api'
import { useSettingsStore } from '../../store/settingsStore'
import './PromptInput.css'

interface PromptInputProps {
  onCodeGenerated: (code: string) => void
  onLog?: (type: 'info' | 'warning' | 'error' | 'success', message: string) => void
}

export default function PromptInput({ onCodeGenerated, onLog }: PromptInputProps) {
  const [prompt, setPrompt] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const { llm } = useSettingsStore()

  const handleGenerate = async () => {
    if (!prompt.trim()) return

    setIsGenerating(true)
    setError(null)
    onLog?.('info', `Generating new OpenSCAD code: "${prompt}"`)

    try {
      const code = await generateCode(prompt, llm)
      onCodeGenerated(code)
      setPrompt('')
      onLog?.('success', `Generated ${code.length} characters of OpenSCAD code`)
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 'Failed to generate code'
      setError(errorMsg)
      onLog?.('error', `Generation failed: ${errorMsg}`)
    } finally {
      setIsGenerating(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleGenerate()
    }
  }

  return (
    <div className="prompt-input">
      <div className="prompt-controls">
        <input
          type="text"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Describe the 3D model you want to create... (e.g., 'a gear with 20 teeth')"
          disabled={isGenerating}
          className="prompt-field"
        />
        <button
          onClick={handleGenerate}
          disabled={isGenerating || !prompt.trim()}
          className="generate-button"
        >
          {isGenerating ? 'Generating...' : 'Generate New'}
        </button>
      </div>
      {error && <div className="error-message">{error}</div>}
    </div>
  )
}
