/**
 * A 12-point trend sparkline: context beside a number, not a chart to read
 * values off. One series, so no legend and no labels — the current period is
 * carried in the accent hue and the exact figures live in the accessible
 * label and in the table itself.
 */
export default function Sparkline({ values, label, width = 108, height = 28 }) {
  if (values.length < 2) return null

  const pad = 6 // room for the end dot and its surface ring
  const min = Math.min(...values)
  const max = Math.max(...values)
  const span = max - min || 1

  const x = (i) => pad + (i * (width - pad * 2)) / (values.length - 1)
  const y = (value) => pad + (1 - (value - min) / span) * (height - pad * 2)

  const points = values.map((value, i) => `${x(i)},${y(value)}`)
  const previous = points.slice(0, -1).join(' ')
  const current = points.slice(-2).join(' ')
  const lastIndex = values.length - 1

  return (
    <svg
      className="sparkline"
      width={width}
      height={height}
      viewBox={`0 0 ${width} ${height}`}
      role="img"
      aria-label={label}
    >
      <title>{label}</title>
      <polyline className="sparkline__previous" points={previous} />
      <polyline className="sparkline__current" points={current} />
      <circle
        className="sparkline__marker"
        cx={x(lastIndex)}
        cy={y(values[lastIndex])}
        r="4"
      />
    </svg>
  )
}
