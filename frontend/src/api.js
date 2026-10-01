async function request(path, options = {}) {
  const response = await fetch(path, {
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

export const sendOtp = (sessionId) =>
  request(`/v1/sessions/${sessionId}/otp`, {
    method: "POST",
    body: JSON.stringify({ action: "send" }),
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

export const appraise = (sessionId) =>
  request(`/v1/sessions/${sessionId}/appraise`, { method: "POST" });
