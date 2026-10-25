/**
 * Every network call lives here. In dev Vite proxies /api → localhost:8000.
 */
const BASE_URL = import.meta.env.VITE_API_URL || '/api'

async function request(path, options = {}) {
  let response
  try {
    response = await fetch(`${BASE_URL}${path}`, {
      headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
      ...options,
    })
  } catch {
    throw new Error('Cannot reach the server. Is the backend running on port 8000?')
  }

  if (!response.ok) {
    let detail = `Request failed (${response.status})`
    try {
      const body = await response.json()
      detail = body.detail || detail
    } catch { /* non-JSON error body */ }
    throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail))
  }
  if (response.status === 204) return null
  return response.json()
}

export const api = {
  health: () => request('/health'),
  symptoms: () => request('/symptoms'),
  listLogs: (profile) => request(`/logs?profile=${encodeURIComponent(profile)}`),
  createLog: (payload) => request('/logs', { method: 'POST', body: JSON.stringify(payload) }),
  deleteLog: (id) => request(`/logs/${id}`, { method: 'DELETE' }),
  insights: (profile) => request(`/insights?profile=${encodeURIComponent(profile)}`),
  report: (profile) => request(`/report?profile=${encodeURIComponent(profile)}`),
  loadScenario: (scenario, profile) =>
    request('/scenario', { method: 'POST', body: JSON.stringify({ scenario, profile }) }),
}

export default api
