const TICK_ANGLES = [0, 25, 50, 75, 100];

function polar(cx, cy, r, value) {
  const a = ((180 - value * 1.8) * Math.PI) / 180;
  return [cx + r * Math.cos(a), cy - r * Math.sin(a)];
}

export function ScoreGauge({ value, color = "#38bdf8", bandLabel }) {
  const clamped = Math.max(0, Math.min(100, value));
  const cx = 160;
  const cy = 150;
  const r = 120;
  const ticks = TICK_ANGLES.map((t) => {
    const [x1, y1] = polar(cx, cy, r + 16, t);
    const [x2, y2] = polar(cx, cy, r + 25, t);
    return { t, x1, y1, x2, y2 };
  });

  return (
    <svg
      className="gauge"
      viewBox="0 0 320 208"
      role="img"
      aria-label={`Borrower Readiness Index ${value} out of 100, ${bandLabel} band`}
    >
      <path d="M40 152v38M280 152v38" stroke="#334155" strokeWidth="11" strokeLinecap="round" />
      <path d="M8 192h304" stroke="#1e293b" strokeWidth="3" strokeDasharray="2 8" strokeLinecap="round" />
      <path
        d={`M ${cx - r} ${cy} A ${r} ${r} 0 0 1 ${cx + r} ${cy}`}
        fill="none"
        stroke="#0f172a"
        strokeWidth="20"
        strokeLinecap="round"
      />
      <path
        d={`M ${cx - r} ${cy} A ${r} ${r} 0 0 1 ${cx + r} ${cy}`}
        fill="none"
        stroke={color}
        strokeWidth="20"
        strokeLinecap="round"
        pathLength="100"
        strokeDasharray={`${clamped} ${100 - clamped}`}
        style={{ transition: "stroke-dasharray 900ms ease" }}
      />
      {ticks.map(({ t, x1, y1, x2, y2 }) => (
        <path
          key={t}
          d={`M${x1} ${y1}L${x2} ${y2}`}
          stroke={t <= clamped ? color : "#475569"}
          strokeWidth={t % 50 === 0 ? 3 : 2}
          strokeLinecap="round"
          opacity={t <= clamped ? 0.9 : 0.6}
        />
      ))}
      <text
        x="160"
        y="132"
        textAnchor="middle"
        className="gauge-value"
        fill="currentColor"
        fontSize="72"
        fontWeight="800"
        fontFamily="ui-monospace, SFMono-Regular, Menlo, monospace"
      >
        {Math.round(clamped)}
      </text>
      <text x="160" y="160" textAnchor="middle" fill="currentColor" fontSize="13" className="gauge-sub">
        out of 100
      </text>
      <text x="8" y="180" fill="currentColor" fontSize="11" className="gauge-sub">
        0
      </text>
      <text x="312" y="180" textAnchor="end" fill="currentColor" fontSize="11" className="gauge-sub">
        100
      </text>
    </svg>
  );
}

export function DonutChart({ parts, centerValue, centerLabel }) {
  const total = parts.reduce((sum, p) => sum + p.value, 0) || 1;
  let offset = 0;
  const segments = parts
    .filter((p) => p.value > 0)
    .map((p) => {
      const pct = (p.value / total) * 100;
      const segment = { ...p, pct, offset };
      offset += pct;
      return segment;
    });

  return (
    <div className="donut-wrap">
      <svg
        className="donut"
        viewBox="0 0 180 180"
        role="img"
        aria-label={`Contribution mix: ${parts
          .map((p) => `${p.label} ${Math.round((p.value / total) * 100)}%`)
          .join(", ")}`}
      >
        <circle cx="90" cy="90" r="64" fill="none" stroke="#0f172a" strokeWidth="26" />
        {segments.map((s) => (
          <circle
            key={s.label}
            cx="90"
            cy="90"
            r="64"
            fill="none"
            stroke={s.color}
            strokeWidth="26"
            pathLength="100"
            strokeDasharray={`${Math.max(s.pct - 1.5, 0.5)} ${100 - Math.max(s.pct - 1.5, 0.5)}`}
            strokeDashoffset={-s.offset}
            transform="rotate(-90 90 90)"
          />
        ))}
        <text
          x="90"
          y="86"
          textAnchor="middle"
          className="donut-value"
          fill="currentColor"
          fontSize="26"
          fontWeight="800"
          fontFamily="ui-monospace, SFMono-Regular, Menlo, monospace"
        >
          {centerValue}
        </text>
        <text x="90" y="106" textAnchor="middle" className="donut-sub" fill="currentColor" fontSize="11">
          {centerLabel}
        </text>
      </svg>
      <ul className="donut-legend">
        {parts.map((p) => (
          <li key={p.label}>
            <span className="swatch" style={{ background: p.color }} aria-hidden="true" />
            <span className="legend-name">{p.label}</span>
            <span className="legend-value">
              {p.value.toFixed(1)} pts · {Math.round((p.value / total) * 100)}%
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
