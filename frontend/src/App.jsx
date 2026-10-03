import { Suspense, lazy, useEffect, useRef, useState } from "react";
import * as api from "./api.js";
const ResultReport = lazy(() => import("./components/ResultReport.jsx"));
import { BridgeMark, HeroArt, Icon } from "./components/Illustrations.jsx";
import { speak } from "./voice/tts.js";
import { getStrings, speakText } from "./i18n.js";

const LANGUAGES = [
  { code: "hi-IN", label: "हिन्दी (Hindi)" },
  { code: "bn-IN", label: "বাংলা (Bengali)" },
  { code: "ta-IN", label: "தமிழ் (Tamil)" },
  { code: "te-IN", label: "తెలుగు (Telugu)" },
  { code: "mr-IN", label: "मराठी (Marathi)" },
  { code: "en-IN", label: "English" },
];

const SCOPE_IDS = ["land", "discom", "aa", "uli"];

const SCOPE_LABEL_KEY = { land: "scopeLand", discom: "scopeDiscom", aa: "scopeAa", uli: "scopeUli" };

function howItems(t) {
  return [
    { icon: "mic", title: t.how1t, text: t.how1x },
    { icon: "shield", title: t.how2t, text: t.how2x },
    { icon: "doc", title: t.how3t, text: t.how3x },
    { icon: "gauge", title: t.how4t, text: t.how4x },
  ];
}

function guideFor(step, t) {
  if (step === "otp")
    return { icon: "shield", title: t.gOtpT, points: [t.gOtp1, t.gOtp2, t.gOtp3] };
  if (step === "consent")
    return { icon: "doc", title: t.gConT, points: [t.gCon1, t.gCon2, t.gCon3] };
  return { icon: "scan", title: t.gAppT, points: [t.gApp1, t.gApp2, t.gApp3] };
}

const STEPS = ["start", "otp", "consent", "appraise", "result"];

function StepPanel({ icon, title, points, eyebrow, note }) {
  return (
    <aside className="panel" aria-label={`About this step: ${title}`}>
      <span className="panel-icon" aria-hidden="true">
        <Icon name={icon} size={26} />
      </span>
      <p className="eyebrow">{eyebrow}</p>
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
        {note}
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
  const [scope, setScope] = useState(SCOPE_IDS);
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const firstRender = useRef(true);
  const t = getStrings(language);
  const scopeOptions = SCOPE_IDS.map((id) => ({ id, label: t[SCOPE_LABEL_KEY[id]] }));

  const fail = (err) => setError(err.message || String(err));

  const start = async () => {
    setBusy(true);
    setError(null);
    try {
      const s = await api.createSession(language);
      setSession(s);
      setStep("otp");
      speak(t.speakVerify, language);
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
      speak(t.speakVerified, language);
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
      speak(t.speakGranted, language);
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
      speak(speakText(t.speakResult, { bri: r.bri }), language);
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
              <a href="#how-it-works">{t.navHow}</a>
              <a href="#trust">{t.navTrust}</a>
            </nav>
          ) : (
            <button type="button" className="link-btn" onClick={restart}>
              {t.startOver}
            </button>
          )}
        </div>
      </header>

      <div className="shell">
        <ol className="progress" aria-label="Onboarding progress">
          {t.progress.map((label, i) => (
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
                  <p className="eyebrow">{t.heroEyebrow}</p>
                  <h2 className="hero-title" id="hero-title">
                    {t.heroTitle}
                  </h2>
                  <p className="hero-lede">
                    {t.heroLede}
                  </p>
                  <ul className="trust-chips" id="trust">
                    <li>
                      <Icon name="lock" size={14} /> {t.chipConsent}
                    </li>
                    <li>
                      <Icon name="shield" size={14} /> {t.chipStored}
                    </li>
                    <li>
                      <Icon name="globe" size={14} /> {t.chipLang}
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
                  <h2 id="heading-start">{t.getStarted}</h2>
                  <label htmlFor="lang">{t.chooseLang}</label>
                  <select id="lang" value={language} onChange={(e) => setLanguage(e.target.value)}>
                    {LANGUAGES.map((l) => (
                      <option key={l.code} value={l.code}>
                        {l.label}
                      </option>
                    ))}
                  </select>
                  <button disabled={busy} onClick={start}>
                    <BusyLabel busy={busy} idle={t.startBtn} active={t.startingBtn} />
                  </button>
                  <p className="hint">
                    {t.startHint}
                  </p>
                </section>

                <aside className="panel" id="how-it-works" aria-label="How it works">
                  <p className="eyebrow">{t.howEyebrow}</p>
                  <h2 className="panel-title">{t.howTitle}</h2>
                  <ol className="how-list">
                    {howItems(t).map((item) => (
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
                    {t.passNote}
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
                <h2 id="heading-otp">{t.otpTitle}</h2>
                <div className="aadhaar-note" role="note">
                  <strong>{t.aadhaarTitle}</strong>
                  <p>{t.aadhaarBody}</p>
                </div>
                <div className="otp-help" role="note" aria-label={t.otpHelpTitle}>
                  <strong>{t.otpHelpTitle}</strong>
                  <ul>
                    <li>{t.otpHelp1}</li>
                    <li>{t.otpHelp2}</li>
                    <li>{t.otpHelp3}</li>
                  </ul>
                </div>
                <label htmlFor="otp">
                  {t.otpLabel}
                </label>
                {devOtp && (
                  <p className="hint" id="otp-hint">
                    {t.devOtp} <strong>{devOtp}</strong>
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
                  <BusyLabel busy={busy} idle={t.verifyBtn} active={t.verifyingBtn} />
                </button>
              </section>
              <StepPanel {...guideFor("otp", t)} eyebrow={t.goodToKnow} note={t.passShort} />
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
                <h2 id="heading-consent">{t.consentTitle}</h2>
                <p>
                  {t.consentDesc}
                </p>
                {scopeOptions.map((o) => (
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
                  <BusyLabel busy={busy} idle={t.grantBtn} active={t.grantingBtn} />
                </button>
              </section>
              <StepPanel {...guideFor("consent", t)} eyebrow={t.goodToKnow} note={t.passShort} />
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
                <h2 id="heading-appraise">{t.appraiseTitle}</h2>
                <p>{t.appraiseDesc}</p>
                <div className="scope-review">
                  {scopeOptions.filter((o) => scope.includes(o.id)).map((o) => (
                    <span key={o.id} className="scope-chip">
                      <Icon name="check" size={14} />
                      {o.label}
                    </span>
                  ))}
                </div>
                <button disabled={busy} onClick={runAppraise}>
                  <BusyLabel busy={busy} idle={t.checkBtn} active={t.pullingBtn} />
                </button>
              </section>
              <StepPanel {...guideFor("appraise", t)} eyebrow={t.goodToKnow} note={t.passShort} />
            </div>
          )}

          {step === "result" && result && (
            <section
              className="card result"
              id="step-result"
              tabIndex={-1}
              aria-label={`Your result: Borrower Readiness Index ${result.bri} out of 100`}
            >
              <Suspense fallback={<p className="hint">{t.loadingReport}</p>}>
                <ResultReport result={result} onRestart={restart} />
              </Suspense>
            </section>
          )}
        </main>

        <footer>
          <div className="footer-grid">
            <div className="footer-brand">
              <BridgeMark size={24} />
              <span>SetuCredit</span>
            </div>
            <p className="footer-tag">{t.footerTag}</p>
            <p className="footer-note">{t.footerNote}</p>
          </div>
        </footer>
      </div>
    </div>
  );
}
