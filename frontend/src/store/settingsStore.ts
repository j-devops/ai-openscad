import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface LLMSettings {
  model: string;
  temperature: number;
  maxTokens: number;
}

interface SettingsState {
  llm: LLMSettings;
  setModel: (model: string) => void;
  setTemperature: (temperature: number) => void;
  setMaxTokens: (maxTokens: number) => void;
  resetToDefaults: () => void;
}

const DEFAULT_SETTINGS: LLMSettings = {
  model: 'gpt-4-turbo-preview',
  temperature: 0.3,
  maxTokens: 2000,
};

export const useSettingsStore = create<SettingsState>()(
  persist(
    (set) => ({
      llm: DEFAULT_SETTINGS,
      setModel: (model) => set((state) => ({ llm: { ...state.llm, model } })),
      setTemperature: (temperature) => set((state) => ({ llm: { ...state.llm, temperature } })),
      setMaxTokens: (maxTokens) => set((state) => ({ llm: { ...state.llm, maxTokens } })),
      resetToDefaults: () => set({ llm: DEFAULT_SETTINGS }),
    }),
    {
      name: 'ai-openscad-settings',
    }
  )
);
