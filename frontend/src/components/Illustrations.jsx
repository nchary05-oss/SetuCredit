const ICONS = {
  globe: (
    <>
      <circle cx="12" cy="12" r="9" />
      <path d="M3 12h18" />
      <path d="M12 3c2.7 2.8 2.7 15.2 0 18" />
      <path d="M12 3c-2.7 2.8-2.7 15.2 0 18" />
    </>
  ),
  shield: (
    <>
      <path d="M12 3l7 3v5.5c0 4.6-3 7.7-7 9.5-4-1.8-7-4.9-7-9.5V6z" />
      <path d="M9 12l2 2 4-4" />
    </>
  ),
  doc: (
    <>
      <path d="M6 3h8l4 4v14H6z" />
      <path d="M14 3v4h4" />
      <path d="M9 14l2 2 4-4" />
    </>
  ),
  scan: (
    <>
      <circle cx="11" cy="11" r="6" />
      <path d="M15.5 15.5L20 20" />
      <path d="M8.5 12v-1.5M11 12v-3M13.5 12v-2" />
    </>
  ),
  gauge: (
    <>
      <path d="M4 17a8 8 0 0 1 16 0" />
      <path d="M12 17l4-4.5" />
      <circle cx="12" cy="17" r="1.4" />
      <path d="M4 20h16" />
    </>
  ),
  plant: (
    <>
      <path d="M3 19l6-7 4 4 3-3 5 6z" />
      <path d="M3 21h18" />
      <path d="M17 5c-3 0-5 2-5 5 3 0 5-2 5-5z" />
      <path d="M12 10c0-2.5-1.5-4-4-4 0 2.5 1.5 4 4 4z" />
    </>
  ),
  bolt: <path d="M13 3L5 14h6l-1 7 8-11h-6z" />,
  bank: (
    <>
      <path d="M3 9l9-5 9 5" />
      <path d="M5.5 10v8M10 10v8M14 10v8M18.5 10v8" />
      <path d="M3 20.5h18" />
    </>
  ),
  clock: (
    <>
      <circle cx="12" cy="12" r="8.5" />
      <path d="M12 7.5V12l3 2" />
    </>
  ),
  mic: (
    <>
      <path d="M12 3.5a2.8 2.8 0 0 1 2.8 2.8v5a2.8 2.8 0 0 1-5.6 0v-5A2.8 2.8 0 0 1 12 3.5z" />
      <path d="M5.5 11.5a6.5 6.5 0 0 0 13 0" />
      <path d="M12 18v3" />
    </>
  ),
  lock: (
    <>
      <rect x="5" y="10.5" width="14" height="10" rx="2" />
      <path d="M8.5 10.5V8a3.5 3.5 0 0 1 7 0v2.5" />
    </>
  ),
  check: <path d="M4.5 12.5l5 5 10-11" />,
  sun: (
    <>
      <circle cx="12" cy="12" r="4" />
      <path d="M12 2.5V5M12 19v2.5M2.5 12H5M19 12h2.5M5 5l1.8 1.8M17.2 17.2L19 19M19 5l-1.8 1.8M6.8 17.2L5 19" />
    </>
  ),
  moon: <path d="M20 13.5A8 8 0 0 1 10.5 4 8 8 0 1 0 20 13.5z" />,
};

export function Icon({ name, size = 20, className }) {
  return (
    <svg
      className={className}
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {ICONS[name]}
    </svg>
  );
}

export function BridgeMark({ size = 30 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 32 32" fill="none" aria-hidden="true">
      <rect width="32" height="32" rx="9" fill="#0c4a6e" />
      <path
        d="M5 24c3.5-9.5 18.5-9.5 22 0"
        stroke="var(--accent)"
        strokeWidth="2.2"
        strokeLinecap="round"
      />
      <path d="M3.5 18.5h25" stroke="#e0f2fe" strokeWidth="2.2" strokeLinecap="round" />
      <path d="M8 18.5V24M24 18.5V24" stroke="var(--accent)" strokeWidth="1.8" strokeLinecap="round" />
      <path d="M16 14.4v4.1" stroke="var(--accent)" strokeWidth="1.6" strokeLinecap="round" />
    </svg>
  );
}

export function HeroArt() {
  const waves = [268, 284, 300];
  const hangers = [
    [202, 142],
    [227, 165],
    [240, 168],
    [253, 165],
    [278, 142],
  ];
  const bars = [
    [58, 18],
    [68, 36],
    [78, 52],
    [88, 30],
    [98, 14],
  ];
  return (
    <svg
      className="hero-art"
      viewBox="0 0 480 320"
      role="img"
      aria-label="A bridge carrying consented records from a borrower's phone to a partner lender"
    >
      <defs>
        <radialGradient id="sa-glow" cx="50%" cy="45%" r="55%">
          <stop offset="0%" stopColor="#0ea5e9" stopOpacity="0.32" />
          <stop offset="100%" stopColor="#0ea5e9" stopOpacity="0" />
        </radialGradient>
      </defs>
      <rect x="0.5" y="0.5" width="479" height="319" rx="20" fill="var(--il-bg)" stroke="var(--panel-line)" />
      <ellipse cx="240" cy="150" rx="200" ry="130" fill="url(#sa-glow)" />

      <rect x="0" y="248" width="132" height="72" fill="var(--il-art-bg)" />
      <rect x="348" y="248" width="132" height="72" fill="var(--il-art-bg)" />
      <path d="M0 248h132" stroke="var(--status-ok-ink)" strokeWidth="2" opacity="0.55" />
      <path d="M348 248h132" stroke="var(--il-steel)" strokeWidth="2" opacity="0.8" />
      {waves.map((y, i) => (
        <path
          key={y}
          d={`M140 ${y} q 16 -7 32 0 t 32 0 t 32 0 t 32 0 t 32 0`}
          fill="none"
          stroke="#0ea5e9"
          strokeWidth="2"
          strokeLinecap="round"
          opacity={0.5 - i * 0.12}
        />
      ))}

      <path d="M176 300V90M304 300V90" stroke="var(--il-steel)" strokeWidth="7" strokeLinecap="round" />
      <path d="M176 96 Q240 240 304 96" fill="none" stroke="var(--accent)" strokeWidth="3" />
      <path d="M176 100L132 190M304 100L348 190" stroke="var(--accent)" strokeWidth="2.4" opacity="0.85" />
      {hangers.map(([x, y]) => (
        <path
          key={x}
          d={`M${x} ${y}V190`}
          stroke="var(--accent)"
          strokeWidth="1.5"
          opacity="0.7"
        />
      ))}
      <rect x="120" y="187" width="240" height="7" rx="3.5" fill="var(--il-steel)" />
      <path
        d="M132 190.5h216"
        stroke="#0ea5e9"
        strokeWidth="1.6"
        strokeDasharray="9 11"
        opacity="0.7"
      />

      <rect x="44" y="140" width="64" height="108" rx="10" fill="var(--il-bg)" stroke="var(--il-steel)" strokeWidth="2" />
      <rect x="51" y="148" width="50" height="92" rx="6" fill="var(--il-bg)" />
      {bars.map(([x, h], i) => (
        <rect
          key={x}
          x={x}
          y={194 - h / 2}
          width="6"
          height={h}
          rx="3"
          fill={i % 2 ? "#0ea5e9" : "#38bdf8"}
        />
      ))}
      <path d="M114 178a18 18 0 0 1 0 32" fill="none" stroke="var(--accent)" strokeWidth="2.5" strokeLinecap="round" />
      <path d="M124 166a30 30 0 0 1 0 56" fill="none" stroke="var(--accent)" strokeWidth="2.5" strokeLinecap="round" opacity="0.55" />

      <path d="M378 176L412 152L446 176Z" fill="var(--il-steel)" />
      <rect x="384" y="176" width="56" height="72" fill="var(--il-panel)" stroke="var(--il-steel)" strokeWidth="1.5" />
      <path d="M396 186v54M412 186v54M428 186v54" stroke="#64748b" strokeWidth="3" />
      <path d="M384 248h56" stroke="var(--il-steel)" strokeWidth="2" />
      <circle cx="412" cy="134" r="15" fill="#34d399" />
      <text
        x="412"
        y="140"
        textAnchor="middle"
        fontSize="17"
        fontWeight="700"
        fill="#052e16"
        fontFamily="system-ui, sans-serif"
      >
        ₹
      </text>

      <g>
        <rect x="146" y="46" width="86" height="54" rx="8" fill="var(--il-panel)" stroke="var(--il-steel)" />
        <rect x="154" y="55" width="44" height="6" rx="3" fill="var(--il-steel)" />
        <rect x="156" y="84" width="9" height="9" rx="2" fill="#38bdf8" />
        <rect x="170" y="76" width="9" height="17" rx="2" fill="#34d399" />
        <rect x="184" y="70" width="9" height="23" rx="2" fill="#fbbf24" />
        <rect x="198" y="80" width="9" height="13" rx="2" fill="#38bdf8" />
        <rect x="212" y="73" width="9" height="20" rx="2" fill="#a78bfa" />
      </g>

      <g>
        <rect x="298" y="30" width="96" height="48" rx="8" fill="var(--il-panel)" stroke="var(--il-steel)" />
        <rect x="307" y="41" width="52" height="6" rx="3" fill="var(--il-steel)" />
        <rect x="307" y="54" width="38" height="6" rx="3" fill="var(--il-steel)" />
        <circle cx="377" cy="54" r="11" fill="#34d399" opacity="0.18" />
        <path d="M372 54l3.5 3.5 6-6.5" fill="none" stroke="var(--status-ok-ink)" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" />
      </g>
    </svg>
  );
}
