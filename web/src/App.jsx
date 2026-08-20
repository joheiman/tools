import { useEffect, useState } from 'react'
import { fetchCustomers } from './api.js'

const MONTH_LABEL = new Intl.DateTimeFormat('en-GB', {
  month: 'short',
  year: 'numeric',
  timeZone: 'UTC',
})

function formatMonth(month) {
  return MONTH_LABEL.format(new Date(`${month}-01T00:00:00Z`))
}

function latestUsage(customer) {
  return customer.usage.at(-1)
}

export default function App() {
  const [customerz, setCustomers] = useState([])
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchCustomers()
      .then(setCustomers)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  const latestMonth = customers.length ? latestUsage(customers[0]).month : null

  return (
    <main>
      <header>
        <h1>Internal Energy Dashboard</h1>
        <p className="subtitle">
          Customer portfolio — internal use only. Access is logged.
        </p>
      </header>

      {loading && <p className="state">Loading portfolio…</p>}
      {error && <p className="state error">{error}</p>}

      {!loading && !error && (
        <table>
          <thead>
            <tr>
              <th>Customer</th>
              <th>Address</th>
              <th>City</th>
              <th className="numeric">Solar kWp</th>
              <th>Tariff</th>
              <th className="numeric">
                {latestMonth ? formatMonth(latestMonth) : 'Latest'} kWh
              </th>
            </tr>
          </thead>
          <tbody>
            {customers.map((customer) => (
              <tr key={customer.id}>
                <td>
                  {customer.first_name} {customer.last_name}
                </td>
                <td>
                  {customer.street_address}
                  <span className="postcode">{customer.postcode}</span>
                </td>
                <td>{customer.city}</td>
                <td className="numeric">
                  {customer.solar_kwp ? customer.solar_kwp.toFixed(1) : '—'}
                </td>
                <td>
                  <span className={`tariff tariff--${customer.tariff}`}>
                    {customer.tariff}
                  </span>
                </td>
                <td className="numeric">
                  {latestUsage(customer).kwh.toFixed(0)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </main>
  )
}
