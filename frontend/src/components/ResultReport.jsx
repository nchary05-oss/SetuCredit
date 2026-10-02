import { ScoreGauge, DonutChart } from "./Charts.jsx";
import { Icon } from "./Illustrations.jsx";

const SOURCE_NAMES = {
  land: "Land registry",
  discom: "Electricity utility",
  aa: "Bank account (Account Aggregator)",
  uli: "Lending history (RBI ULI)",
};

const SOURCE_SHORT = {
  land: "Land registry",
  discom: "Electricity",
  aa: "Bank account",
  uli: "Lending history",
};

const SOURCE_ICONS = { land: "plant", discom: "bolt", aa: "bank", uli: "clock" };

const SOURCE_COLORS = {
  land: "#34d399",
  discom: "#fbbf24",
  aa: "#38bdf8",
  uli: "#a78bfa",
};

const SOURCE_ORDER = ["land", "discom", "aa", "uli"];

const FEATURE_LABELS = {
  land_area_acres: (v) => `${v} acres of land holding`,
  land_ownership_clear: (v) =>
    v ? "Ownership records clear" : "Ownership not fully clear",
  land_years_held: (v) => `Held for ${v} years`,
  utility_on_time_ratio: (v) => `${Math.round(v * 100)}% of bills paid on time`,
  utility_months_paid: (v) => `${v} months of bills paid`,
  utility_bill_level: (v) =>
    v >= 1 ? "₹3,000+ average monthly bill" : `~₹${Math.round(v * 3000)} average monthly bill`,
  bank_balance_level: (v) =>
    v >= 1 ? "₹50,000+ average balance" : `~₹${Math.round(v * 50000)} average balance`,
  bank_inflow_consistency: (v) => `${Math.round(v * 100)}% income inflow consistency`,
  bank_months_active: (v) => `Banking for ${v} months`,
  bank_emi_ratio: (v) => `${Math.round(v * 100)}% of inflow committed to EMIs`,
  credit_existing_loans: (v) => `${v} existing loan${v === 1 ? "" : "s"}`,
  credit_repayment_regular_months: (v) => `${v} months of regular repayment`,
  credit_delinquencies: (v) => `${v} late payment${v === 1 ? "" : "s"} in the last 12 months`,
};

const PREFIX_TO_SOURCE = [
  ["land_", "land"],
  ["utility_", "discom"],
  ["bank_", "aa"],
  ["credit_", "uli"],
];

function bandFor(bri) {
  if (bri >= 80)
    return { label: "Strong", color: "#34d399", note: "Eligible for larger loan amounts" };
  if (bri >= 60)
    return { label: "Good", color: "#38bdf8", note: "Likely to qualify with most partner lenders" };
  if (bri >= 40)
    return {
      label: "Fair",
      color: "#fbbf24",
      note: "Eligible for smaller loans — paying bills on time and keeping your bank account active will improve this",
    };
  return {
    label: "Building",
    color: "#f87171",
    note: "Not ready yet — build a record of regular bill payments and repayments, then check again",
  };
}

function formatDateTime(d) {
  return d.toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

const inr = new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
  maximumFractionDigits: 0,
});

export default function ResultReport({ result, onRestart }) {
  const band = bandFor(result.bri);
  const generatedAt = formatDateTime(new Date());
  const handedOff = result.handoff !== "failed";

  const details = {};
  for (const [key, format] of Object.entries(FEATURE_LABELS)) {
    if (!(key in result.features)) continue;
    const source = PREFIX_TO_SOURCE.find(([prefix]) => key.startsWith(prefix))?.[1];
    if (!source) continue;
    (details[source] ??= []).push(format(result.features[key]));
  }

  const presentSources = SOURCE_ORDER.filter((s) => s in result.attributions);
  const donutParts = presentSources.map((source) => ({
    label: SOURCE_SHORT[source],
    value: result.attributions[source],
    color: SOURCE_COLORS[source],
  }));
  const recordsAnalysed = Object.values(result.sources).reduce(
    (n, s) => n + s.record_count,
    0,
  );
  const sourcesOk = Object.values(result.sources).filter((s) => s.status === "ok").length;
  const sourcesTotal = Object.keys(result.sources).length;

  return (
    <div className="report">
      <div className="report-head">
        <p className="report-meta">Analysis report · generated {generatedAt}</p>
        <button type="button" onClick={() => window.print()}>
          Print / Save as PDF
        </button>
      </div>

      <section className="report-summary" aria-label="Score summary">
        <div className="gauge-card">
          <ScoreGauge value={result.bri} color={band.color} bandLabel={band.label} />
        </div>
        <div className="summary-side">
          <p className="summary-eyebrow">Borrower Readiness Index</p>
          <div className="band">
            <span className="band-label" style={{ background: band.color }}>
              {band.label}
            </span>
            <span className="band-note">{band.note}</span>
          </div>
          <div className="loan-block">
            <p className="summary-eyebrow">Suggested loan amount</p>
            {result.loan_range ? (
              <>
                <p className="loan-value">
                  {inr.format(result.loan_range.min_inr)} – {inr.format(result.loan_range.max_inr)}
                </p>
                <p className="loan-note">
                  Indicative range for the partner lender — the final amount is set by the lender
                  after their assessment.
                </p>
              </>
            ) : (
              <p className="loan-note">
                Not available at this score yet — a suggestion appears from BRI 40 upwards.
              </p>
            )}
          </div>
          <div className="stats">
            <div className="stat">
              <span className="stat-value">{recordsAnalysed}</span>
              <span className="stat-label">Records analysed</span>
            </div>
            <div className="stat">
              <span className="stat-value">
                {sourcesOk}/{sourcesTotal}
              </span>
              <span className="stat-label">Sources verified</span>
            </div>
            <div className="stat">
              <span className="stat-value">{result.handoff}</span>
              <span className="stat-label">Lender handoff</span>
            </div>
          </div>
        </div>
      </section>

      <div className="report-cols">
        <section className="report-section" aria-label="Score breakdown">
          <h2>Score breakdown</h2>
          <p className="section-lede">Points earned against the maximum available per source.</p>
          <ul className="breakdown">
            {presentSources.map((source) => {
              const attr = result.attributions[source];
              const max = result.max_points[source] || 100;
              return (
                <li key={source}>
                  <span className="bd-name">{SOURCE_NAMES[source]}</span>
                  <span className="bar-track" aria-hidden="true">
                    <span
                      className="bar-fill"
                      style={{ width: `${(attr / max) * 100}%`, background: SOURCE_COLORS[source] }}
                    />
                  </span>
                  <span className="bd-points">
                    {attr.toFixed(1)} / {max} pts
                  </span>
                </li>
              );
            })}
          </ul>
        </section>

        <section className="report-section" aria-label="Contribution mix">
          <h2>Contribution mix</h2>
          <p className="section-lede">Share of the points you earned from each record type.</p>
          <DonutChart
            parts={donutParts}
            centerValue={result.bri}
            centerLabel="BRI score"
          />
        </section>
      </div>

      <section className="report-section" aria-label="Data sources checked">
        <h2>Data sources checked</h2>
        <ul className="source-grid">
          {Object.entries(result.sources).map(([source, s]) => (
            <li key={source} className={`source-tile ${s.status}`}>
              <span className="source-icon" aria-hidden="true">
                <Icon name={SOURCE_ICONS[source] ?? "doc"} size={22} />
              </span>
              <span className="source-name">{SOURCE_NAMES[source] ?? source}</span>
              <span className={`source-status ${s.status}`}>{s.status}</span>
              <span className="source-count">
                {s.record_count} record{s.record_count === 1 ? "" : "s"}
              </span>
            </li>
          ))}
        </ul>
      </section>

      <div className="report-cols">
        <section className="report-section" aria-label="Detailed analysis">
          <h2>Detailed analysis</h2>
          {SOURCE_ORDER.filter((s) => details[s]).map((source) => (
            <div key={source} className="detail-group">
              <h3>
                <span className="dot" style={{ background: SOURCE_COLORS[source] }} aria-hidden="true" />
                {SOURCE_NAMES[source]}
              </h3>
              <ul>
                {details[source].map((line) => (
                  <li key={line}>{line}</li>
                ))}
              </ul>
            </div>
          ))}
        </section>

        <div className="report-stack">
          <section className="report-section" aria-label="Next steps">
            <h2>Next steps</h2>
            <p>
              {handedOff
                ? `Your pre-underwritten package (${result.appraisal_id.slice(0, 8)}) has been shared with the partner lender. After their approval, funds disburse instantly via UPI/IMPS.`
                : "Your package could not be shared with the partner lender right now. Please start a new session and try again."}
            </p>
            <p className="consent-note">
              This assessment used the records you consented to share. They were processed in
              memory for this request only — nothing was stored on our servers.
            </p>
          </section>

          <section className="report-section report-meta-block" aria-label="Report details">
            <h2>Report details</h2>
            <dl>
              <div>
                <dt>Appraisal ID</dt>
                <dd>{result.appraisal_id}</dd>
              </div>
              <div>
                <dt>Scoring model</dt>
                <dd>{result.model_version}</dd>
              </div>
              <div>
                <dt>Generated</dt>
                <dd>{generatedAt}</dd>
              </div>
              <div>
                <dt>Handoff status</dt>
                <dd>{result.handoff}</dd>
              </div>
            </dl>
          </section>
        </div>
      </div>

      <div className="report-actions">
        <button type="button" onClick={() => window.print()}>
          Print / Save as PDF
        </button>
        <button type="button" className="secondary" onClick={onRestart}>
          New session
        </button>
      </div>
    </div>
  );
}
