import { useEffect, useRef, useState } from "react";
import * as api from "./api.js";
import ResultReport from "./components/ResultReport.jsx";
import { BridgeMark, HeroArt, Icon } from "./components/Illustrations.jsx";
import { speak } from "./voice/tts.js";

const LANGUAGES = [
  { code: "hi-IN", label: "हिन्दी (Hindi)" },
  { code: "bn-IN", label: "বাংলা (Bengali)" },
  { code: "ta-IN", label: "தமிழ் (Tamil)" },
  { code: "te-IN", label: "తెలుగు (Telugu)" },
  { code: "mr-IN", label: "मराठी (Marathi)" },
  { code: "en-IN", label: "English" },
];

const SCOPE_OPTIONS = [
  { id: "land", label: "Land registry records" },
  { id: "discom", label: "Electricity bill payments" },
  { id: "aa", label: "Bank account summary" },
  { id: "uli", label: "Lending history (RBI ULI)" },
];

const HOW_IT_WORKS = [
  {
    icon: "mic",
    title: "Speak or type in your language",
    text: "Six Indian languages, guided one step at a time.",
  },
  {
    icon: "shield",
    title: "Verify once with an OTP",
    text: "Sent to your Aadhaar-linked number and checked in seconds.",
  },
  {
    icon: "doc",
    title: "Consent, then and only then",
    text: "Tick exactly what you share. Consent expires on its own.",
  },
  {
    icon: "gauge",
    title: "Get your Borrower Readiness Index",
    text: "Passed straight to a partner lender — funds arrive by UPI/IMPS.",
  },
];

const STEP_GUIDE = {
  otp: {
    icon: "shield",
    title: "Why we verify",
    points: [
      "The OTP goes only to your Aadhaar-linked number.",
      "It proves the session is yours — nothing else is collected.",
      "Wrong number? Go back and start a fresh session.",
    ],
  },
  consent: {
    icon: "doc",
    title: "You hold the pen",
    points: [
      "Tick only the records you are comfortable sharing.",
      "Consent is time-bound and revocable under DPDP.",
      "Every pull is logged in the audit ledger — no record contents.",
    ],
  },
  appraise: {
    icon: "scan",
    title: "Four sources, one pass",
    points: [
      "Land, electricity, bank and lending records are pulled in parallel.",
      "Features are computed in memory and never written to disk.",
      "Your score is handed to the partner lender as a signed package.",
    ],
  },
};

const STEPS = ["start", "otp", "consent", "appraise", "result"];

function StepPanel({ icon, title, points }) {
  return (
    <aside className="panel" aria-label={`About this step: ${title}`}>
      <span className="panel-icon" aria-hidden="true">
        <Icon name={icon} size={26} />
      </span>
      <p className="eyebrow">Good to know</p>
      <h2 className="panel-title">{title}</h2>
      <ul className="panel-list">
        {points.map((point) => (
          <li key={point}>
            <Icon name="check" size={15} className="panel-check" />
            <span>{point}</span>
          </li>
        ))}
      </ul>
      <p className="panel-note">
        <Icon name="lock" size={15} />
        Pass-through by design — record contents are never stored.
      </p>
    </aside>
  );
}

function BusyLabel({ busy, idle, active }) {
  return busy ? (
    <>
      <span className="spinner" aria-hidden="true" />
      {active}
    </>
  ) : (
    idle
  );
}

export default function App() {
  const [session, setSession] = useState(null);
  const [language, setLanguage] = useState("hi-IN");
  const [step, setStep] = useState("start");
  const [otp, setOtp] = useState("");
  const [devOtp, setDevOtp] = useState(null);
  const [scope, setScope] = useState(SCOPE_OPTIONS.map((o) => o.id));
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const firstRender = useRef(true);

  const fail = (err) => setError(err.message || String(err));

  const start = async () => {
    setBusy(true);
    setError(null);
    try {
      const s = await api.createSession(language);
      setSession(s);
      setStep("otp");
      speak("Please verify your identity with a one time password", language);
      const sent = await api.sendOtp(s.session_id);
      setDevOtp(sent.dev_otp);
    } catch (err) {
      fail(err);
    } finally {
      setBusy(false);
    }
  };

  const verify = async () => {
    if (otp.length !== 6) return;
    setBusy(true);
    setError(null);
    try {
      await api.verifyOtp(session.session_id, otp);
      setStep("consent");
      speak("Identity verified. Please grant consent to read your records", language);
    } catch (err) {
      fail(err);
    } finally {
      setBusy(false);
    }
  };

  const grant = async () => {
    setBusy(true);
    setError(null);
    try {
      await api.grantConsent(session.session_id, scope);
      setStep("appraise");
      speak("Consent granted. Continue to check your credit readiness", language);
    } catch (err) {
      fail(err);
    } finally {
      setBusy(false);
    }
  };

  const runAppraise = async () => {
    setBusy(true);
    setError(null);
    try {
      const r = await api.appraise(session.session_id);
      setResult(r);
      setStep("result");
      speak(`Your Borrower Readiness Index is ${r.bri} out of 100`, language);
    } catch (err) {
      fail(err);
    } finally {
      setBusy(false);
    }
  };

  const restart = () => {
    setSession(null);
    setStep("start");
    setResult(null);
    setOtp("");
    setDevOtp(null);
    setError(null);
  };

  useEffect(() => {
    if (step !== "otp") setOtp("");
    if (firstRender.current) {
      firstRender.current = false;
      return;
    }
    document.getElementById(`step-${step}`)?.focus();
  }, [step]);

  const stepIndex = STEPS.indexOf(step);

  return (
    <div>
      <header className="topbar">
        <div className="topbar-inner">
          <div className="brand">
            <BridgeMark />
            <h1 className="brand-name">SetuCredit</h1>
          </div>
          {step === "start" ? (
            <nav className="topnav" aria-label="Primary">
              <a href="#how-it-works">How it works</a>
              <a href="#trust">Trust</a>
            </nav>
          ) : (
            <button type="button" className="link-btn" onClick={restart}>
              Start over
            </button>
          )}
        </div>
      </header>

      <div className="shell">
        <ol className="progress" aria-label="Onboarding progress">
          {["Language", "OTP", "Consent", "Appraise", "Result"].map((label, i) => (
            <li
              key={label}
              className={i <= stepIndex ? "on" : ""}
              aria-current={i === stepIndex ? "step" : undefined}
            >
              <span className="step-dot">{i + 1}</span>
              <span className="step-label">{label}</span>
            </li>
          ))}
        </ol>

        <main id="main-content">
          {error && (
            <div className="error" role="alert">
              {error}
            </div>
          )}

          {step === "start" && (
            <>
              <section className="hero" aria-labelledby="hero-title">
                <div className="hero-copy">
                  <p className="eyebrow">Voice-first · DPI-powered</p>
                  <h2 className="hero-title" id="hero-title">
                    Your records are already a credit history.
                  </h2>
                  <p className="hero-lede">
                    Land ownership, electricity bills and bank activity say more about a borrower
                    than a bureau file ever could. SetuCredit turns them into a Borrower Readiness
                    Index a partner lender can act on — with your consent, in your language, in
                    minutes.
                  </p>
                  <ul className="trust-chips" id="trust">
                    <li>
                      <Icon name="lock" size={14} /> Consent first
                    </li>
                    <li>
                      <Icon name="shield" size={14} /> Data never stored
                    </li>
                    <li>
                      <Icon name="globe" size={14} /> 6 languages
                    </li>
                  </ul>
                </div>
                <HeroArt />
              </section>

              <div className="split">
                <section
                  className="card"
                  id="step-start"
                  tabIndex={-1}
                  aria-labelledby="heading-start"
                >
                  <h2 id="heading-start">Get started</h2>
                  <label htmlFor="lang">Choose your language</label>
                  <select id="lang" value={language} onChange={(e) => setLanguage(e.target.value)}>
                    {LANGUAGES.map((l) => (
                      <option key={l.code} value={l.code}>
                        {l.label}
                      </option>
                    ))}
                  </select>
                  <button disabled={busy} onClick={start}>
                    <BusyLabel busy={busy} idle="Start onboarding" active="Starting…" />
                  </button>
                  <p className="hint">
                    Takes about two minutes. Keep your Aadhaar-linked phone handy.
                  </p>
                </section>

                <aside className="panel" id="how-it-works" aria-label="How it works">
                  <p className="eyebrow">How it works</p>
                  <h2 className="panel-title">Four steps, one bridge to a lender</h2>
                  <ol className="how-list">
                    {HOW_IT_WORKS.map((item) => (
                      <li key={item.title}>
                        <span className="how-icon" aria-hidden="true">
                          <Icon name={item.icon} size={20} />
                        </span>
                        <span className="how-text">
                          <strong>{item.title}</strong>
                          <span>{item.text}</span>
                        </span>
                      </li>
                    ))}
                  </ol>
                  <p className="panel-note">
                    <Icon name="lock" size={15} />
                    Pass-through by design — borrower records are never written to our database.
                  </p>
                </aside>
              </div>
            </>
          )}

          {step === "otp" && (
            <div className="split">
              <section
                className="card"
                id="step-otp"
                tabIndex={-1}
                aria-labelledby="heading-otp"
              >
                <h2 id="heading-otp">Verify your number</h2>
                <label htmlFor="otp">
                  Enter the 6-digit OTP sent to your Aadhaar-linked number.
                </label>
                {devOtp && (
                  <p className="hint" id="otp-hint">
                    Dev mode OTP: <strong>{devOtp}</strong>
                  </p>
                )}
                <input
                  id="otp"
                  type="text"
                  inputMode="numeric"
                  autoComplete="one-time-code"
                  maxLength={6}
                  placeholder="123456"
                  aria-describedby={devOtp ? "otp-hint" : undefined}
                  value={otp}
                  onChange={(e) => setOtp(e.target.value.replace(/\D/g, ""))}
                />
                <button disabled={busy || otp.length !== 6} onClick={verify}>
                  <BusyLabel busy={busy} idle="Verify OTP" active="Verifying…" />
                </button>
              </section>
              <StepPanel {...STEP_GUIDE.otp} />
            </div>
          )}

          {step === "consent" && (
            <div className="split">
              <section
                className="card"
                id="step-consent"
                tabIndex={-1}
                aria-labelledby="heading-consent"
              >
                <h2 id="heading-consent">Grant consent</h2>
                <p>
                  SetuCredit reads these records <strong>once, only with your consent</strong>.
                  Nothing is stored on our servers.
                </p>
                {SCOPE_OPTIONS.map((o) => (
                  <label key={o.id} className="check">
                    <input
                      type="checkbox"
                      checked={scope.includes(o.id)}
                      onChange={(e) =>
                        setScope((prev) =>
                          e.target.checked ? [...prev, o.id] : prev.filter((s) => s !== o.id),
                        )
                      }
                    />
                    {o.label}
                  </label>
                ))}
                <button disabled={busy || scope.length === 0} onClick={grant}>
                  <BusyLabel busy={busy} idle="Grant consent" active="Granting…" />
                </button>
              </section>
              <StepPanel {...STEP_GUIDE.consent} />
            </div>
          )}

          {step === "appraise" && (
            <div className="split">
              <section
                className="card"
                id="step-appraise"
                tabIndex={-1}
                aria-labelledby="heading-appraise"
              >
                <h2 id="heading-appraise">Check readiness</h2>
                <p>We will pull your records in parallel and compute your BRI score.</p>
                <div className="scope-review">
                  {SCOPE_OPTIONS.filter((o) => scope.includes(o.id)).map((o) => (
                    <span key={o.id} className="scope-chip">
                      <Icon name="check" size={14} />
                      {o.label}
                    </span>
                  ))}
                </div>
                <button disabled={busy} onClick={runAppraise}>
                  <BusyLabel busy={busy} idle="Check my readiness" active="Pulling data…" />
                </button>
              </section>
              <StepPanel {...STEP_GUIDE.appraise} />
            </div>
          )}

          {step === "result" && result && (
            <section
              className="card result"
              id="step-result"
              tabIndex={-1}
              aria-label={`Your result: Borrower Readiness Index ${result.bri} out of 100`}
            >
              <ResultReport result={result} onRestart={restart} />
            </section>
          )}
        </main>

        <footer>
          <div className="footer-grid">
            <div className="footer-brand">
              <BridgeMark size={24} />
              <span>SetuCredit</span>
            </div>
            <p className="footer-tag">The middleware bridge between consented data and lenders.</p>
            <p className="footer-note">Consent first · Pass-through by default · Data never stored</p>
          </div>
        </footer>
      </div>
    </div>
  );
}
