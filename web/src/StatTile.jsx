import Sparkline from './Sparkline.jsx'

export default function StatTile({ label, value, unit, trend, trendLabel }) {
  return (
    <div className="tile">
      <p className="tile__label">{label}</p>
      <p className="tile__value">
        {value}
        {unit && <span className="tile__unit">{unit}</span>}
      </p>
      {trend && <Sparkline values={trend} label={trendLabel} />}
    </div>
  )
}
