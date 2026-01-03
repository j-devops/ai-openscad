import { useState, useCallback } from 'react'
import PromptInput from './components/prompt/PromptInput'
import CodeEditor from './components/editor/CodeEditor'
import Preview3D from './components/preview/Preview3D'
import Console, { ConsoleMessage } from './components/console/Console'
import ChatInterface from './components/chat/ChatInterface'
import { SettingsPanel } from './components/settings/SettingsPanel'
import './App.css'

function App() {
  const [code, setCode] = useState<string>('// Your OpenSCAD code will appear here\n')
  const [jobId, setJobId] = useState<string | null>(null)
  const [consoleMessages, setConsoleMessages] = useState<ConsoleMessage[]>([])

  const addConsoleMessage = useCallback((
    type: 'info' | 'warning' | 'error' | 'success',
    message: string
  ) => {
    const newMessage: ConsoleMessage = {
      id: `${Date.now()}-${Math.random()}`,
      timestamp: new Date(),
      type,
      message
    }
    setConsoleMessages(prev => [...prev, newMessage])
  }, [])

  const clearConsole = useCallback(() => {
    setConsoleMessages([])
  }, [])

  const handleCodeGenerated = useCallback((generatedCode: string) => {
    setCode(generatedCode)
    addConsoleMessage('success', 'AI code generation completed')
  }, [addConsoleMessage])

  const handleCodeModified = useCallback((modifiedCode: string) => {
    setCode(modifiedCode)
    addConsoleMessage('success', 'Code modified via chat')
  }, [addConsoleMessage])

  const handleRenderComplete = useCallback((completedJobId: string | null) => {
    setJobId(completedJobId)
    if (completedJobId) {
      addConsoleMessage('success', `Render completed successfully: ${completedJobId}`)
    }
  }, [addConsoleMessage])

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-left">
          <h1>AI-OpenSCAD</h1>
          <p>AI-Powered 3D Modeling Platform</p>
        </div>
        <div className="header-right">
          <SettingsPanel />
        </div>
      </header>

      <main className="app-main">
        <div className="prompt-section">
          <PromptInput
            onCodeGenerated={handleCodeGenerated}
            onLog={addConsoleMessage}
          />
        </div>

        <div className="workspace">
          <div className="editor-panel">
            <CodeEditor
              code={code}
              onChange={setCode}
              onRenderComplete={handleRenderComplete}
              onLog={addConsoleMessage}
            />
          </div>

          <div className="preview-panel">
            <Preview3D jobId={jobId} />
          </div>
        </div>

        <div className="bottom-panels">
          <div className="chat-panel">
            <ChatInterface
              currentCode={code}
              onCodeModified={handleCodeModified}
              onLog={addConsoleMessage}
            />
          </div>

          <div className="console-panel">
            <Console messages={consoleMessages} onClear={clearConsole} />
          </div>
        </div>
      </main>
    </div>
  )
}

export default App
