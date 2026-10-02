/**
 * Browser TTS as the offline voice channel; swap for Bhashini TTS once keys
 * are provisioned (same speak(text, lang) contract).
 */
function pickVoice(lang) {
  const voices = window.speechSynthesis.getVoices();
  if (!voices.length) return null;
  return (
    voices.find((v) => v.lang === lang) ||
    voices.find((v) => v.lang?.startsWith(lang?.slice(0, 2))) ||
    null
  );
}

export function speak(text, lang) {
  if (!("speechSynthesis" in window)) return;
  const run = () => {
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = lang || "hi-IN";
    utterance.rate = 0.95;
    const voice = pickVoice(utterance.lang);
    if (voice) {
      utterance.voice = voice;
      utterance.lang = voice.lang;
    }
    window.speechSynthesis.speak(utterance);
  };
  // Voices load async in Chrome — retry once they arrive.
  if (!window.speechSynthesis.getVoices().length) {
    window.speechSynthesis.onvoiceschanged = () => run();
    // Fallback in case the event already fired with an empty list.
    setTimeout(run, 250);
  } else {
    run();
  }
}
