const API_BASE = '/api'

export interface Reading {
  id: number
  period: string
  hws_value: number
  cws_value: number
  electric_value: number
}

export interface Tariff {
  id: number
  resource_type: 'hws' | 'cws' | 'electric' | 'rent'
  rate: number
  effective_from: string
  effective_to: string | null
}

export interface MonthlyCost {
  period: string
  hws_consumption: number
  cws_consumption: number
  electric_consumption: number
  hws_cost: number
  cws_cost: number
  electric_cost: number
  rent: number
  total: number
}

export interface YearSummary {
  year: number
  months: MonthlyCost[]
  total_hws_cost: number
  total_cws_cost: number
  total_electric_cost: number
  total_rent: number
  grand_total: number
}

export interface Stats {
  year: number
  avg_monthy_total: number
  max_month_total: number
  min_month_total: number
  total_readings: number
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!response.ok) {
    const body = await response.text()
    throw new Error(`API error ${response.status}: ${body}`)
  }
  if (response.status === 204) return undefined as T
  return response.json()
}

export const api = {
  // Readings
  getReadings: (year?: number) =>
    request<Reading[]>(`/readings${year ? `?year=${year}` : ''}`),

  getReadingYears: () => request<number[]>('/readings/years'),

  createReading: (data: Omit<Reading, 'id'>) =>
    request<Reading>('/readings', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  updateReading: (id: number, data: { period: string; hws_value: number; cws_value: number; electric_value: number }) =>
    request<Reading>(`/readings/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  deleteReading: (id: number) =>
    request<void>(`/readings/${id}`, { method: 'DELETE' }),

  // Tariffs
  getTariffs: () => request<Tariff[]>('/tariffs'),

  upsertTariff: (data: { resource_type: string; rate: number; effective_from: string }) =>
    request<Tariff>('/tariffs', {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  // Summary
  getSummary: (year: number) => request<YearSummary>(`/summary?year=${year}`),

  getStats: (year: number) => request<Stats>(`/summary/stats?year=${year}`),
}