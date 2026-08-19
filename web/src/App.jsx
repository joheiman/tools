import { useEffect, useState } from 'react'
import { fetchCustomers, fetchPortfolioSummary } from './api.js'
import Sparkline from './Sparkline.jsx'
import StatTile from './StatTile.jsx'

const MONTH_LABEL = new Intl.DateTimeFormat('en-GB', {
  month: 'short',
  year: 'numeric',
  timeZone: 'UTC',
})
const WHOLE = new Intl.NumberFormat('en-GB', { maximumFractionDigits: 0 })
const COMPACT = new Intl.NumberFormat('en-GB', {
  notation: 'compact',
  maximumFractionDigits: 1,
})

function formatMonth(month) {
  return MONTH_LABEL.format(new Date(`${month}-01T00:00:00Z`))
}

function latestUsage(customer) {
  return customer.usage.at(-1)
}

function trendLabel(usage) {
  const kwh = usage.map((point) => point.kwh)
  const min = Math.min(...kwh)
  const max = Math.max(...kwh)
  return (
    `Monthly consumption, ${formatMonth(usage[0].month)} to ` +
    `${formatMonth(usage.at(-1).month)}: low ${WHOLE.format(min)} kWh, ` +
    `high ${WHOLE.format(max)} kWh, latest ${WHOLE.format(usage.at(-1).kwh)} kWh.`
  )
}

export default function App() {
  const [customers, setCustomers] = useState([])
  const [summary, setSummary] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([fetchCustomers(), fetchPortfolioSummary()])
      .then(([customerList, portfolio]) => {
        setCustomers(customerList)
        setSummary(portfolio)
      })
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

      {summary && (
        <section className="tiles" aria-label="Portfolio summary">
          <StatTile
            label="Customers"
            value={WHOLE.format(summary.customer_count)}
          />
          <StatTile
            label="Installed solar capacity"
            value={summary.total_solar_kwp.toFixed(1)}
            unit="kWp"
          />
          <StatTile
            label="Consumption, last 12 months"
            value={COMPACT.format(summary.total_kwh_12m)}
            unit="kWh"
            trend={summary.monthly_totals.map((point) => point.kwh)}
            trendLabel={trendLabel(summary.monthly_totals)}
          />
        </section>
      )}

      {!loading && !error && (
        <table>
          <thead>
            <tr>
              <th>Customer</th>
              <th>Address</th>
              <th>City</th>
              <th className="numeric">Solar kWp</th>
              <th>Tariff</th>
              <th>12-month trend</th>
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
                <td>
                  <Sparkline
                    values={customer.usage.map((point) => point.kwh)}
                    label={trendLabel(customer.usage)}
                  />
                </td>
                <td className="numeric">
                  {WHOLE.format(latestUsage(customer).kwh)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </main>
  )
}
