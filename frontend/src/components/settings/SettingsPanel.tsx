import React, { useState } from 'react';
import { useSettingsStore } from '../../store/settingsStore';
import './SettingsPanel.css';

const MODELS = [
  { value: 'gpt-4-turbo-preview', label: 'GPT-4 Turbo' },
  { value: 'gpt-4', label: 'GPT-4' },
  { value: 'gpt-3.5-turbo', label: 'GPT-3.5 Turbo' },
];

export const SettingsPanel: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const { llm, setModel, setTemperature, setMaxTokens, resetToDefaults } = useSettingsStore();

  const handleTemperatureChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setTemperature(parseFloat(e.target.value));
  };

  const handleMaxTokensChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setMaxTokens(parseInt(e.target.value, 10));
  };

  const handleModelChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setModel(e.target.value);
  };

  return (
    <div className="settings-container">
      <button className="settings-button" onClick={() => setIsOpen(!isOpen)} title="LLM Settings">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <circle cx="12" cy="12" r="3"></circle>
          <path d="M12 1v6m0 6v6m6-12l-3 3m-6 6l-3 3m12-6h-6m-6 0H1m16.5-4.5l-3 3m-9 9l-3 3"></path>
        </svg>
      </button>

      {isOpen && (
        <div className="settings-panel">
          <div className="settings-header">
            <h3>LLM Settings</h3>
            <button className="settings-close" onClick={() => setIsOpen(false)}>
              ×
            </button>
          </div>

          <div className="settings-content">
            {/* Model Selection */}
            <div className="setting-group">
              <label htmlFor="model-select">Model</label>
              <select
                id="model-select"
                value={llm.model}
                onChange={handleModelChange}
                className="model-select"
              >
                {MODELS.map((model) => (
                  <option key={model.value} value={model.value}>
                    {model.label}
                  </option>
                ))}
              </select>
              <p className="setting-hint">Which OpenAI model to use for code generation</p>
            </div>

            {/* Temperature Slider */}
            <div className="setting-group">
              <label htmlFor="temperature-slider">
                Temperature: <span className="setting-value">{llm.temperature.toFixed(2)}</span>
              </label>
              <input
                id="temperature-slider"
                type="range"
                min="0"
                max="2"
                step="0.05"
                value={llm.temperature}
                onChange={handleTemperatureChange}
                className="slider"
              />
              <div className="slider-labels">
                <span>Precise (0)</span>
                <span>Creative (2)</span>
              </div>
              <p className="setting-hint">
                Lower values make output more focused and deterministic, higher values make it more creative
              </p>
            </div>

            {/* Max Tokens Slider */}
            <div className="setting-group">
              <label htmlFor="tokens-slider">
                Max Tokens: <span className="setting-value">{llm.maxTokens}</span>
              </label>
              <input
                id="tokens-slider"
                type="range"
                min="500"
                max="4000"
                step="100"
                value={llm.maxTokens}
                onChange={handleMaxTokensChange}
                className="slider"
              />
              <div className="slider-labels">
                <span>500</span>
                <span>4000</span>
              </div>
              <p className="setting-hint">Maximum length of generated code (longer = more complex models)</p>
            </div>

            {/* Reset Button */}
            <div className="settings-actions">
              <button className="reset-button" onClick={resetToDefaults}>
                Reset to Defaults
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
