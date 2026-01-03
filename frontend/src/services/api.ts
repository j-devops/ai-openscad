import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export interface LLMSettings {
  model?: string
  temperature?: number
  max_tokens?: number
}

export interface GenerateRequest {
  prompt: string
  style?: string
  model?: string
  temperature?: number
  max_tokens?: number
}

export interface GenerateResponse {
  code: string
  generated_at: string
}

export interface RenderRequest {
  code: string
  format?: 'png' | 'stl' | 'both'
}

export interface RenderResponse {
  job_id: string
  status: string
  preview_url?: string
  stl_url?: string
}

export const generateCode = async (
  prompt: string,
  llmSettings?: LLMSettings
): Promise<string> => {
  const response = await api.post<GenerateResponse>('/api/v1/generate/', {
    prompt,
    ...llmSettings,
  })
  return response.data.code
}

export const submitRenderJob = async (code: string): Promise<RenderResponse> => {
  const response = await api.post<RenderResponse>('/api/v1/render/', {
    code,
    format: 'both',
  })
  return response.data
}

export const getRenderStatus = async (jobId: string): Promise<RenderResponse> => {
  const response = await api.get<RenderResponse>(`/api/v1/render/${jobId}`)
  return response.data
}

export const getPreviewUrl = (jobId: string): string => {
  return `${API_URL}/api/v1/render/${jobId}/preview`
}

export const getDownloadUrl = (jobId: string): string => {
  return `${API_URL}/api/v1/render/${jobId}/download`
}
