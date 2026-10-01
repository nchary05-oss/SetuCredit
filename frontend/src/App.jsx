import { useCallback, useEffect, useState } from "react";
import * as api from "./api.js";
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

const STEPS = ["start", "otp", "consent", "appraise", "result"];

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

  const restart = useCallback(() => {
    setSession(null);
    setStep("start");
    setResult(null);
    setOtp("");
    setDevOtp(null);
    setError(null);
  }, []);

  useEffect(() => {
    if (step !== "otp") setOtp("");
  }, [step]);

  const stepIndex = STEPS.indexOf(step);

  return (
    <div className="shell">
      <header>
        <h1>SetuCredit</h1>
        <p>Credit readiness for everyone — in your own language</p>
      </header>

      <ol className="progress">
        {["Language", "OTP", "Consent", "Appraise", "Result"].map((label, i) => (
          <li key={label} className={i <= stepIndex ? "on" : ""}>
            {label}
          </li>
        ))}
      </ol>

      {error && <div className="error">{error}</div>}

      {step === "start" && (
        <section className="card">
          <label htmlFor="lang">Choose your language</label>
          <select id="lang" value={language} onChange={(e) => setLanguage(e.target.value)}>
            {LANGUAGES.map((l) => (
              <option key={l.code} value={l.code}>
                {l.label}
              </option>
            ))}
          </select>
          <button disabled={busy} onClick={start}>
            {busy ? "Starting…" : "Start onboarding"}
          </button>
        </section>
      )}

      {step === "otp" && (
        <section className="card">
          <p>Enter the 6-digit OTP sent to your Aadhaar-linked number.</p>
          {devOtp && <p className="hint">Dev mode OTP: <strong>{devOtp}</strong></p>}
          <input
            inputMode="numeric"
            maxLength={6}
            placeholder="123456"
            value={otp}
            onChange={(e) => setOtp(e.target.value.replace(/\D/g, ""))}
          />
          <button disabled={busy || otp.length !== 6} onClick={verify}>
            {busy ? "Verifying…" : "Verify OTP"}
          </button>
        </section>
      )}

      {step === "consent" && (
        <section className="card">
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
            {busy ? "Granting…" : "Grant consent"}
          </button>
        </section>
      )}

      {step === "appraise" && (
        <section className="card">
          <p>We will pull your records in parallel and compute your BRI score.</p>
          <button disabled={busy} onClick={runAppraise}>
            {busy ? "Pulling data…" : "Check my readiness"}
          </button>
        </section>
      )}

      {step === "result" && result && (
        <section className="card result">
          <div className="bri">{result.bri}</div>
          <div className="bri-label">Borrower Readiness Index (0–100)</div>
          <ul className="sources">
            {Object.entries(result.sources).map(([source, s]) => (
              <li key={source} className={s.status}>
                {source}: {s.status}
              </li>
            ))}
          </ul>
          <p className="hint">
            Package {result.appraisal_id.slice(0, 8)} — handoff: {result.handoff} —{" "}
            {result.model_version}
          </p>
          <button onClick={restart}>New session</button>
        </section>
      )}

      <footer>
        Consent first · Pass-through by default · Data never stored
      </footer>
    </div>
  );
}
