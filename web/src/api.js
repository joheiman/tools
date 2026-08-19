const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000'
const TOKEN = import.meta.env.VITE_TOOL_API_TOKEN

export async function fetchCustomers() {
  if (!TOKEN) {
    throw new Error(
      'VITE_TOOL_API_TOKEN is not set. Copy web/.env.example to web/.env.',
    )
  }

  const response = await fetch(`${API_BASE}/api/customers`, {
    headers: { Authorization: `Bearer ${TOKEN}` },
  })

  if (response.status === 401) {
    throw new Error('The API rejected the operator token (401).')
  }
  if (!response.ok) {
    throw new Error(`The API returned ${response.status}.`)
  }

  return response.json()
}
