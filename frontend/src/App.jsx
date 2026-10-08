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
  { code: "ml-IN", label: "മലയാളം (Malayalam)" },
  { code: "gu-IN", label: "ગુજરાતી (Gujarati)" },
  { code: "bho-IN", label: "भोजपुरी (Bhojpuri)" },
  { code: "or-IN", label: "ଓଡ଼ିଆ (Odia)" },
  { code: "kn-IN", label: "ಕನ್ನಡ (Kannada)" },
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

function ConsentReceipt({ consent, labels, t, busy, onRevoke }) {
  if (!consent) return null;
  const shortId =
    consent.consent_id && consent.consent_id.length > 8
      ? consent.consent_id.slice(0, 8)
      : consent.consent_id;
  const expiry = new Date(consent.expires_at).toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
  return (
    <div className="consent-receipt" aria-label={t.receiptTitle}>
      <p className="summary-eyebrow">{t.receiptTitle}</p>
      <p className="receipt-line">
        {t.receiptShared}: {labels.join(" · ")}
      </p>
      <p className="receipt-meta">
        {shortId} · {t.receiptValid} {expiry}
      </p>
      <button type="button" className="secondary" disabled={busy} onClick={onRevoke}>
        <BusyLabel busy={busy} idle={t.revokeBtn} active={t.revokingBtn} />
      </button>
    </div>
  );
}

export default function App() {
  const [session, setSession] = useState(null);
  const [language, setLanguage] = useState("en-IN");
  const [step, setStep] = useState("start");
  const [otp, setOtp] = useState("");
  const [aadhaar, setAadhaar] = useState("");
  const [aadhaarConsent, setAadhaarConsent] = useState(false);
  const [uidai, setUidai] = useState(null);
  const [otpSent, setOtpSent] = useState(false);
  const [devOtp, setDevOtp] = useState(null);
  const [scope, setScope] = useState(SCOPE_IDS);
  const [consent, setConsent] = useState(null);
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const [resendIn, setResendIn] = useState(0);
  const [pullStatus, setPullStatus] = useState({});
  const firstRender = useRef(true);
  const errorRef = useRef(null);
  const [theme, setTheme] = useState(
    () => document.documentElement.getAttribute("data-theme") || "dark",
  );

  const toggleTheme = () => {
    const next = theme === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    localStorage.setItem("sc-theme", next);
    setTheme(next);
  };
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
      setOtpSent(false);
      setUidai(null);
      setDevOtp(null);
      speak(t.speakVerify, language);
    } catch (err) {
      fail(err);
    } finally {
      setBusy(false);
    }
  };

  const requestOtp = async () => {
    if (aadhaar.length !== 12 || !aadhaarConsent) return;
    setBusy(true);
    setError(null);
    try {
      const sent = await api.sendOtp(session.session_id, {
        aadhaar_number: aadhaar,
        consent: true,
      });
      setUidai(sent);
      setDevOtp(sent.dev_otp);
      setOtp("");
      setOtpSent(true);
      setResendIn(30);
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
      setAadhaar(""); // pass-through: drop the full number once verified
      setStep("consent");
      speak(t.speakVerified, language);
    } catch (err) {
      fail(err);
    } finally {
      setBusy(false);
    }
  };

  const resend = async () => {
    if (resendIn > 0 || aadhaar.length !== 12) return;
    setBusy(true);
    setError(null);
    try {
      const sent = await api.sendOtp(session.session_id, {
        aadhaar_number: aadhaar,
        consent: true,
      });
      setUidai(sent);
      setDevOtp(sent.dev_otp);
      setOtp("");
      setResendIn(30);
    } catch (err) {
      fail(err);
    } finally {
      setBusy(false);
    }
  };

  useEffect(() => {
    if (resendIn <= 0) return;
    const timer = setTimeout(() => setResendIn((s) => s - 1), 1000);
    return () => clearTimeout(timer);
  }, [resendIn]);

  const grant = async () => {
    setBusy(true);
    setError(null);
    try {
      const c = await api.grantConsent(session.session_id, scope);
      setConsent(c);
      setStep("appraise");
      speak(t.speakGranted, language);
    } catch (err) {
      fail(err);
    } finally {
      setBusy(false);
    }
  };

  const revoke = async () => {
    setBusy(true);
    setError(null);
    try {
      await api.revokeConsent(session.session_id);
      setConsent(null);
      setResult(null);
      setPullStatus({});
      setStep("consent");
      speak(t.speakRevoked, language);
    } catch (err) {
      fail(err);
    } finally {
      setBusy(false);
    }
  };

  const runAppraise = async () => {
    setBusy(true);
    setError(null);
    setPullStatus({});
    try {
      const r = await api.appraise(session.session_id);
      for (const id of SCOPE_IDS.filter((s) => scope.includes(s))) {
        await new Promise((res) => setTimeout(res, 300));
        const status = r.sources?.[id]?.status ?? "failed";
        setPullStatus((prev) => ({ ...prev, [id]: status }));
      }
      await new Promise((res) => setTimeout(res, 450));
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
    setAadhaar("");
    setAadhaarConsent(false);
    setUidai(null);
    setOtpSent(false);
    setDevOtp(null);
    setError(null);
    setPullStatus({});
    setConsent(null);
  };

  useEffect(() => {
    if (step !== "otp") setOtp("");
    if (firstRender.current) {
      firstRender.current = false;
      return;
    }
    document.getElementById(`step-${step}`)?.focus();
  }, [step]);

  useEffect(() => {
    if (error) errorRef.current?.focus();
  }, [error]);

  const stepIndex = STEPS.indexOf(step);

  return (
    <div>
      <a className="skip-link" href="#main-content">
        {t.skipToContent}
      </a>
      <header className="topbar">
        <div className="topbar-inner">
          <div className="brand">
            <BridgeMark />
            <h1 className="brand-name">SetuCredit</h1>
          </div>
          <button
            type="button"
            className="theme-toggle"
            data-current={theme}
            aria-label={theme === "dark" ? "Switch to light appearance" : "Switch to dark appearance"}
            onClick={toggleTheme}
          >
            <Icon name="sun" size={15} className="theme-sun" />
            <Icon name="moon" size={15} className="theme-moon" />
            {theme === "dark" ? t.appearanceLight : t.appearanceDark}
          </button>
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
            <div className="error" role="alert" ref={errorRef} tabIndex={-1}>
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
                <form
                  className="card"
                  id="step-start"
                  tabIndex={-1}
                  aria-labelledby="heading-start"
                  onSubmit={(e) => {
                    e.preventDefault();
                    start();
                  }}
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
                  <button type="submit" disabled={busy}>
                    <BusyLabel busy={busy} idle={t.startBtn} active={t.startingBtn} />
                  </button>
                  <p className="hint">
                    {t.startHint}
                  </p>
                </form>

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
              <form
                className="card"
                id="step-otp"
                tabIndex={-1}
                aria-labelledby="heading-otp"
                onSubmit={(e) => {
                  e.preventDefault();
                  if (otpSent) verify();
                  else requestOtp();
                }}
              >
                <h2 id="heading-otp">{t.otpTitle}</h2>
                <div className="aadhaar-note" role="note">
                  <strong>{t.aadhaarTitle}</strong>
                  <p>{t.aadhaarBody}</p>
                </div>
                {!otpSent ? (
                  <>
                    <label htmlFor="aadhaar">{t.aadhaarNumberLabel}</label>
                    <input
                      id="aadhaar"
                      type="text"
                      inputMode="numeric"
                      autoComplete="off"
                      maxLength={12}
                      placeholder={t.aadhaarNumberPlaceholder}
                      value={aadhaar}
                      onChange={(e) => setAadhaar(e.target.value.replace(/\D/g, ""))}
                    />
                    <p className="hint">{t.demoAadhaarHint}</p>
                    <label className="check">
                      <input
                        type="checkbox"
                        checked={aadhaarConsent}
                        onChange={(e) => setAadhaarConsent(e.target.checked)}
                      />
                      {t.aadhaarConsent}
                    </label>
                    <button
                      type="submit"
                      disabled={busy || aadhaar.length !== 12 || !aadhaarConsent}
                    >
                      <BusyLabel busy={busy} idle={t.requestOtpBtn} active={t.requestingBtn} />
                    </button>
                  </>
                ) : (
                  <>
                    <div className="otp-help" role="note" aria-label={t.otpHelpTitle}>
                      <strong>
                        {speakText(t.otpSentTo, {
                          mobile: uidai?.masked_mobile ?? "",
                          aadhaar: uidai?.masked_aadhaar ?? "",
                        })}
                      </strong>
                      <ul>
                        <li>{t.otpHelp1}</li>
                        <li>{t.otpHelp2}</li>
                        <li>{t.otpHelp3}</li>
                      </ul>
                    </div>
                    <label htmlFor="otp">{t.otpLabel}</label>
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
                    <button type="submit" disabled={busy || otp.length !== 6}>
                      <BusyLabel busy={busy} idle={t.verifyBtn} active={t.verifyingBtn} />
                    </button>
                    <button
                      type="button"
                      className="secondary"
                      disabled={busy || resendIn > 0}
                      onClick={resend}
                    >
                      {resendIn > 0
                        ? speakText(t.resendWait, { s: resendIn })
                        : busy
                          ? t.resendingBtn
                          : t.resendBtn}
                    </button>
                    <button
                      type="button"
                      className="link-btn"
                      disabled={busy}
                      onClick={() => {
                        setOtpSent(false);
                        setOtp("");
                        setError(null);
                      }}
                    >
                      {t.editNumberBtn}
                    </button>
                  </>
                )}
              </form>
              <StepPanel {...guideFor("otp", t)} eyebrow={t.goodToKnow} note={t.passShort} />
            </div>
          )}

          {step === "consent" && (
            <div className="split">
              <form
                className="card"
                id="step-consent"
                tabIndex={-1}
                aria-labelledby="heading-consent"
                onSubmit={(e) => {
                  e.preventDefault();
                  grant();
                }}
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
                <button type="submit" disabled={busy || scope.length === 0}>
                  <BusyLabel busy={busy} idle={t.grantBtn} active={t.grantingBtn} />
                </button>
              </form>
              <StepPanel {...guideFor("consent", t)} eyebrow={t.goodToKnow} note={t.passShort} />
            </div>
          )}

          {step === "appraise" && (
            <div className="split">
              <form
                className="card"
                id="step-appraise"
                tabIndex={-1}
                aria-labelledby="heading-appraise"
                onSubmit={(e) => {
                  e.preventDefault();
                  runAppraise();
                }}
              >
                <h2 id="heading-appraise">{t.appraiseTitle}</h2>
                <p>{t.appraiseDesc}</p>
                <ConsentReceipt
                  consent={consent}
                  labels={scopeOptions.filter((o) => scope.includes(o.id)).map((o) => o.label)}
                  t={t}
                  busy={busy}
                  onRevoke={revoke}
                />
                {busy ? (
                  <ul className="pull-list" aria-live="polite" aria-label={t.appraiseTitle}>
                    {scopeOptions
                      .filter((o) => scope.includes(o.id))
                      .map((o) => {
                        const st = pullStatus[o.id];
                        return (
                          <li key={o.id} className={st ? `done ${st}` : "active"}>
                            <span className="pull-icon" aria-hidden="true">
                              {st === "ok" ? (
                                <span className="pull-check-ok">✓</span>
                              ) : st === "failed" ? (
                                <span className="pull-check-fail">✕</span>
                              ) : (
                                <span className="spinner" />
                              )}
                            </span>
                            <span className="pull-name">{o.label}</span>
                            <span className="pull-state">
                              {st === "ok"
                                ? t.pullDone
                                : st === "failed"
                                  ? t.pullFailed
                                  : t.pullReading}
                            </span>
                          </li>
                        );
                      })}
                  </ul>
                ) : (
                  <div className="scope-review">
                    {scopeOptions.filter((o) => scope.includes(o.id)).map((o) => (
                      <span key={o.id} className="scope-chip">
                        <Icon name="check" size={14} />
                        {o.label}
                      </span>
                    ))}
                  </div>
                )}
                <button type="submit" disabled={busy}>
                  <BusyLabel busy={busy} idle={t.checkBtn} active={t.pullingBtn} />
                </button>
              </form>
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
                <ResultReport
                  result={result}
                  onRestart={restart}
                  consent={consent}
                  t={t}
                  revokeBusy={busy}
                  onRevoke={revoke}
                />
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
