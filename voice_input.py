"""Voice input for NammaSeve's "Ask the Notice" question box.

Speech recognition runs entirely in the user's browser (Web Speech API).
Nothing is sent to Groq or any LLM, no audio is recorded or stored by the
app, and no API keys or secrets are used here. The recognised text is only
written into the existing Streamlit text input so the user can edit it and
press "Find answer" themselves.
"""
import json

import streamlit.components.v1 as components

# Speech-recognition locales. Kept separate from the answer language on purpose:
# a user may speak Kannada and still want the answer in English.
SPEECH_LOCALES = {
    "English": "en-IN",
    "Hindi": "hi-IN",
    "Kannada": "kn-IN",
    "Telugu": "te-IN",
}
_SPEECH_LABELS = [
    ("English", "English"),
    ("Hindi", "हिन्दी · Hindi"),
    ("Kannada", "ಕನ್ನಡ · Kannada"),
    ("Telugu", "తెలుగు · Telugu"),
]

_TEMPLATE = r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Noto+Sans+Kannada:wght@400;500;600&family=Noto+Sans+Telugu:wght@400;500;600&display=swap');
*{box-sizing:border-box}
html,body{margin:0;padding:0;background:transparent;font-family:'DM Sans','Noto Sans Kannada','Noto Sans Telugu',sans-serif;color:#241711}
.row{display:flex;align-items:center;gap:10px;flex-wrap:wrap;padding:2px 1px}
#mic{width:48px;height:48px;flex:0 0 48px;border-radius:12px;cursor:pointer;display:flex;align-items:center;justify-content:center;
  border:1px solid rgba(201,160,90,.75);background:linear-gradient(180deg,#fffefa,#f6ecd4);color:#A4231B;
  box-shadow:0 1px 0 #fff inset,0 8px 18px -10px rgba(70,40,15,.45);transition:transform .3s cubic-bezier(.22,.8,.2,1),box-shadow .3s,border-color .3s}
#mic:hover:not(:disabled){transform:translateY(-2px);border-color:#D99A1E;box-shadow:0 14px 24px -12px rgba(70,40,15,.45)}
#mic:focus-visible{outline:none;box-shadow:0 0 0 4px rgba(217,154,30,.28)}
#mic:disabled{opacity:.5;cursor:not-allowed}
#mic.live{background:linear-gradient(135deg,#b3261e,#6a150e 75%);border-color:#5B140F;color:#fff6e3;animation:pulse 1.3s ease-in-out infinite}
@keyframes pulse{0%,100%{box-shadow:0 0 0 0 rgba(179,38,30,.45)}50%{box-shadow:0 0 0 9px rgba(179,38,30,0)}}
#mic svg{width:22px;height:22px;fill:currentColor}
select{height:48px;border-radius:12px;border:1px solid #d8c29a;background:rgba(255,254,250,.94);color:#241711;
  font:500 .9rem 'DM Sans','Noto Sans Kannada','Noto Sans Telugu',sans-serif;padding:0 .7rem;cursor:pointer;max-width:100%}
select:focus{outline:none;border-color:#D99A1E;box-shadow:0 0 0 4px rgba(217,154,30,.22)}
select:disabled{opacity:.5;cursor:not-allowed}
#status{flex:1 1 180px;min-width:150px;font-size:.84rem;line-height:1.5;color:#74695c}
#status.err{color:#A4231B}
@media(prefers-reduced-motion:reduce){#mic,#mic.live{animation:none;transition:none}}
</style>
<div class="row">
  <button id="mic" type="button" aria-label="Speak your question" title="Speak your question">
    <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 14a3.5 3.5 0 0 0 3.5-3.5v-5a3.5 3.5 0 0 0-7 0v5A3.5 3.5 0 0 0 12 14Zm6-3.5a1 1 0 1 0-2 0 4 4 0 0 1-8 0 1 1 0 1 0-2 0 6 6 0 0 0 5 5.9V19H9.5a1 1 0 1 0 0 2h5a1 1 0 1 0 0-2H13v-2.6a6 6 0 0 0 5-5.9Z"/></svg>
  </button>
  <select id="lang" aria-label="Language you will speak in">__OPTIONS__</select>
  <div id="status" role="status" aria-live="polite"></div>
</div>
<script>
(function () {
  var INPUT_LABEL = __INPUT_LABEL__;
  var DEFAULT_LOCALE = __DEFAULT_LOCALE__;
  var IDLE = "Tap the mic and speak. Needs microphone access and an internet connection (your browser's speech service). You can edit the text before asking.";
  var micBtn = document.getElementById("mic");
  var sel = document.getElementById("lang");
  var statusEl = document.getElementById("status");
  sel.value = DEFAULT_LOCALE;

  function resize() {
    try { window.frameElement.style.height = (document.documentElement.scrollHeight + 4) + "px"; } catch (e) {}
  }
  function say(msg, isErr) {
    statusEl.textContent = msg;
    statusEl.className = isErr ? "err" : "";
    resize();
  }
  function questionInput() {
    try {
      return window.parent.document.querySelector('input[aria-label="' + INPUT_LABEL + '"]');
    } catch (e) { return null; }
  }
  function fill(text, focus) {
    var el = questionInput();
    if (!el) return false;
    try {
      var setter = Object.getOwnPropertyDescriptor(window.parent.HTMLInputElement.prototype, "value").set;
      setter.call(el, text);
      el.dispatchEvent(new window.parent.Event("input", { bubbles: true }));
      if (focus) el.focus();
      return true;
    } catch (e) { return false; }
  }

  var SR = null;
  try { SR = window.parent.SpeechRecognition || window.parent.webkitSpeechRecognition; } catch (e) {}
  SR = SR || window.SpeechRecognition || window.webkitSpeechRecognition;

  if (!SR) {
    micBtn.disabled = true; sel.disabled = true;
    say("Voice input isn't supported in this browser. Please type your question, or try Chrome or Edge.", true);
    return;
  }
  if (window.isSecureContext === false) {
    micBtn.disabled = true; sel.disabled = true;
    say("Voice input needs a secure (https) page or localhost. Please type your question.", true);
    return;
  }

  var rec = null, listening = false, finalText = "", sawError = false;

  function setLive(on) {
    listening = on;
    micBtn.classList.toggle("live", on);
    micBtn.setAttribute("aria-pressed", on ? "true" : "false");
    micBtn.title = on ? "Stop listening" : "Speak your question";
    sel.disabled = on;
  }
  function errorMessage(code) {
    switch (code) {
      case "not-allowed":
      case "service-not-allowed":
        return "Microphone access was blocked. Allow it from the address bar, or type your question.";
      case "audio-capture":
        return "No microphone was found. Please connect one, or type your question.";
      case "language-not-supported":
        return "This browser can't recognise the selected language. Try another language, or type your question.";
      case "network":
        return "Couldn't reach the speech service. Check your internet connection, or type your question.";
      case "no-speech":
        return "Didn't hear anything. Tap the mic and try again, or type your question.";
      default:
        return "Voice recognition failed. Please try again or type your question.";
    }
  }

  function start() {
    if (!questionInput()) {
      say("Couldn't find the question box. Please type your question.", true);
      return;
    }
    finalText = ""; sawError = false;
    try {
      rec = new SR();
      rec.lang = sel.value;
      rec.continuous = false;
      rec.interimResults = true;
      rec.maxAlternatives = 1;
    } catch (e) {
      say("Voice input couldn't start. Please type your question.", true);
      return;
    }
    rec.onstart = function () { setLive(true); say("Listening… speak your question."); };
    rec.onresult = function (ev) {
      var interim = "", fin = "";
      for (var i = 0; i < ev.results.length; i++) {
        var t = ev.results[i][0].transcript;
        if (ev.results[i].isFinal) fin += t; else interim += t;
      }
      if (fin) finalText = fin.trim();
      var shown = (fin + interim).trim();
      if (shown) fill(shown, false);
    };
    rec.onerror = function (ev) {
      if (ev.error === "aborted") return;
      sawError = true;
      say(errorMessage(ev.error), true);
    };
    rec.onend = function () {
      setLive(false);
      if (finalText) {
        if (fill(finalText, true)) say("Check the text, edit it if needed, then press “Find answer”.");
        else say("Couldn't fill the question box. Please type your question.", true);
      } else if (!sawError) {
        say("Didn't catch that. Tap the mic and try again, or type your question.", true);
      }
    };
    try { rec.start(); }
    catch (e) { setLive(false); say("Voice input couldn't start. Please type your question.", true); }
  }

  micBtn.addEventListener("click", function () {
    if (listening && rec) { try { rec.stop(); } catch (e) {} return; }
    start();
  });
  say(IDLE);
})();
</script>
"""


def render_voice_input(default_language: str = "English", input_label: str = "Your question") -> None:
    """Render a mic button that fills the text input labelled ``input_label``.

    ``default_language`` only pre-selects the speech language; the user can
    change it, so speech language and answer language stay independent.
    """
    options = "".join(
        f'<option value="{SPEECH_LOCALES[name]}">{label}</option>' for name, label in _SPEECH_LABELS
    )
    html = (
        _TEMPLATE.replace("__OPTIONS__", options)
        .replace("__INPUT_LABEL__", json.dumps(input_label))
        .replace("__DEFAULT_LOCALE__", json.dumps(SPEECH_LOCALES.get(default_language, "en-IN")))
    )
    components.html(html, height=96)
