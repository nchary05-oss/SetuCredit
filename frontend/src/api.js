async function request(path, options = {}) {
  // window.SETUCREDIT_API_BASE is injected at container start (config.js ->
  // nginx envsubst). Empty locally: the PWA is same-origin (Vite proxy /
  // compose nginx). On Render the browser calls the backend URL directly.
  const base = globalThis.SETUCREDIT_API_BASE || "";
  const response = await fetch(base + path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = body.detail;
    const message = Array.isArray(detail)
      ? detail.map((d) => d.msg || JSON.stringify(d)).join(", ")
      : detail || response.statusText;
    throw new Error(message);
  }
  return body;
}

export const createSession = (language) =>
  request("/v1/sessions", { method: "POST", body: JSON.stringify({ language }) });

export const getSession = (sessionId) => request(`/v1/sessions/${sessionId}`);

export const sendOtp = (sessionId, { aadhaar_number, consent }) =>
  request(`/v1/sessions/${sessionId}/otp`, {
    method: "POST",
    body: JSON.stringify({ action: "send", aadhaar_number, consent }),
  });

export const verifyOtp = (sessionId, otp) =>
  request(`/v1/sessions/${sessionId}/otp`, {
    method: "POST",
    body: JSON.stringify({ action: "verify", otp }),
  });

export const grantConsent = (sessionId, scope) =>
  request(`/v1/sessions/${sessionId}/consents`, {
    method: "POST",
    body: JSON.stringify({ scope }),
  });

export const revokeConsent = (sessionId) =>
  request(`/v1/sessions/${sessionId}/consents/revoke`, { method: "POST" });

export const appraise = (sessionId) =>
  request(`/v1/sessions/${sessionId}/appraise`, { method: "POST" });

export const confirmHandoff = (appraisalId) =>
  request(`/v1/appraisals/${appraisalId}/handoff`, { method: "POST" });
