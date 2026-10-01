/**
 * Browser TTS as the offline voice channel; swap for Bhashini TTS once keys
 * are provisioned (same speak(text, lang) contract).
 */
export function speak(text, lang) {
  if (!("speechSynthesis" in window)) return;
  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = lang || "hi-IN";
  utterance.rate = 0.95;
  window.speechSynthesis.speak(utterance);
}
