import os
import streamlit as st
import requests
import io
import time
from PIL import Image

# ── Credentials — st.secrets (Streamlit Cloud) or env vars (local) ────────────
def _secret(key: str) -> str:
    try:
        return st.secrets[key]
    except (KeyError, FileNotFoundError):
        val = os.environ.get(key, "")
        if not val:
            st.error(f"Missing secret: `{key}`. Add it to `.streamlit/secrets.toml` or your environment.", icon="🔑")
        return val

CV_KEY        = _secret("CV_KEY")
CV_ENDPOINT   = _secret("CV_ENDPOINT")
SPEECH_KEY    = _secret("SPEECH_KEY")
SPEECH_REGION = _secret("SPEECH_REGION")
FORMSPREE_ID  = _secret("FORMSPREE_ID")

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CogniVox · Samyak Jain",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:ital,wght@0,300;0,400;0,500;1,300&display=swap');

:root {
    --bg:      #07070e;
    --surface: #0e0e18;
    --card:    #13131f;
    --border:  #252538;
    --accent:  #6c63ff;
    --gold:    #f0b429;
    --text:    #e6e6f0;
    --muted:   #7070a0;
    --green:   #4af098;
    --red:     #ff5c7a;
}

/* ── Base ── */
html, body, [data-testid="stAppViewContainer"],
.stApp, [data-testid="stMain"] {
    font-family: 'DM Mono', monospace !important;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

/* ── Hide ALL Streamlit chrome ── */
[data-testid="stHeader"]         { display: none !important; }
[data-testid="stSidebar"]        { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }
#MainMenu                        { display: none !important; }
footer                           { display: none !important; }
.stDeployButton                  { display: none !important; }
[data-testid="stToolbar"]        { display: none !important; }

/* ── Main block padding ── */
[data-testid="stMainBlockContainer"] {
    padding-top: 0 !important;
    padding-bottom: 3rem !important;
    max-width: 860px !important;
}

/* ── Top brand bar ── */
.cv-navbar {
    background: rgba(7,7,14,0.96);
    border-bottom: 1px solid var(--border);
    padding: 0.75rem 0.2rem 0.65rem;
    margin-bottom: 0.5rem;
}
.cv-brand {
    display: flex;
    align-items: center;
    gap: 0.55rem;
}
.cv-brand-icon { font-size: 1.3rem; filter: drop-shadow(0 0 10px #6c63ff88); }
.cv-brand-name {
    font-family: 'Syne', sans-serif;
    font-size: 1.1rem;
    font-weight: 800;
    background: linear-gradient(130deg, #fff 30%, #6c63ff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.02em;
}
.cv-brand-by {
    font-size: 0.57rem;
    color: var(--muted);
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-left: auto;
}

/* ── Radio → pill tabs ── */
div[data-testid="stRadio"] > div {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    gap: 0.3rem !important;
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    padding: 0.3rem !important;
    width: 100% !important;
    overflow-x: auto !important;
}
div[data-testid="stRadio"] > div::-webkit-scrollbar { display: none; }
div[data-testid="stRadio"] label {
    flex: 1 !important;
    text-align: center !important;
    padding: 0.45rem 0.6rem !important;
    border-radius: 7px !important;
    cursor: pointer !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 0.74rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.03em !important;
    color: var(--muted) !important;
    transition: all 0.18s !important;
    white-space: nowrap !important;
    margin: 0 !important;
    border: none !important;
    background: transparent !important;
}
div[data-testid="stRadio"] label:hover {
    color: var(--text) !important;
    background: rgba(108,99,255,0.1) !important;
}
div[data-testid="stRadio"] label[data-checked="true"],
div[data-testid="stRadio"] label[aria-checked="true"] {
    background: linear-gradient(135deg, #6c63ff, #a78bfa) !important;
    color: #fff !important;
    box-shadow: 0 3px 14px rgba(108,99,255,0.4) !important;
}
/* Hide the radio dot circles */
div[data-testid="stRadio"] label div[data-testid="stMarkdownContainer"] { display: block !important; }
div[data-testid="stRadio"] input[type="radio"] { display: none !important; }
div[data-testid="stRadio"] > div > label > div:first-child { display: none !important; }

/* ── Buttons ── */
.stButton > button {
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.84rem !important;
    background: linear-gradient(135deg, #6c63ff, #a78bfa) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.55rem 1.5rem !important;
    letter-spacing: 0.05em !important;
    transition: all 0.22s ease !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(108,99,255,0.45) !important;
}

/* ── Inputs ── */
.stTextArea textarea, .stTextInput input {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.85rem !important;
}
.stTextArea textarea:focus, .stTextInput input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(108,99,255,0.2) !important;
}
.stSelectbox > div > div {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 8px !important;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    background: var(--surface) !important;
    border: 1.5px dashed rgba(108,99,255,0.45) !important;
    border-radius: 10px !important;
}
[data-testid="stFileUploaderDropzone"] {
    padding: 0.55rem 1rem !important;
    min-height: unset !important;
    background: transparent !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] span {
    font-size: 0.76rem !important;
    color: var(--muted) !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] small {
    font-size: 0.68rem !important;
    color: var(--muted) !important;
}
[data-testid="stFileUploaderDropzone"] svg {
    width: 22px !important; height: 22px !important; color: var(--accent) !important;
}
[data-testid="stFileUploader"] button {
    font-size: 0.72rem !important;
    padding: 0.25rem 0.85rem !important;
    background: rgba(108,99,255,0.12) !important;
    border: 1px solid rgba(108,99,255,0.38) !important;
    border-radius: 6px !important;
    color: var(--accent) !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    transition: background 0.18s !important;
}
[data-testid="stFileUploader"] button:hover {
    background: rgba(108,99,255,0.24) !important;
    transform: none !important;
    box-shadow: none !important;
}

/* ── Misc ── */
.stProgress > div > div { background: var(--accent) !important; }
audio { width: 100%; border-radius: 8px; margin-top: 0.5rem; }
hr { border-color: var(--border) !important; margin: 1.2rem 0 !important; }

/* ── Cards ── */
.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.3rem 1.5rem;
    margin-bottom: 1rem;
}
.card-accent { border-left: 3px solid var(--accent); }
.card-gold   { border-left: 3px solid var(--gold); }

/* ── Typography helpers ── */
.section-tag {
    font-family: 'Syne', sans-serif;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 0.4rem;
}
.hero-wrap { padding: 0 0 1.2rem; }
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: clamp(1.8rem, 4vw, 2.8rem);
    font-weight: 800;
    line-height: 1.05;
    background: linear-gradient(130deg, #fff 35%, #6c63ff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-sub {
    font-size: 0.82rem;
    color: var(--muted);
    margin-top: 0.35rem;
    letter-spacing: 0.03em;
}

/* ── Pipeline step badges ── */
.step-badge {
    display: inline-flex; align-items: center; justify-content: center;
    width: 26px; height: 26px; border-radius: 50%;
    background: var(--accent); color: #fff;
    font-family: 'Syne', sans-serif; font-weight: 800; font-size: 0.75rem;
    margin-right: 0.45rem; flex-shrink: 0;
}
.step-row { display: flex; align-items: center; }

/* ── OCR output box ── */
.ocr-box {
    background: #08080f;
    border: 1px solid var(--border);
    border-left: 3px solid var(--green);
    border-radius: 10px;
    padding: 0.9rem 1.1rem;
    font-size: 0.85rem;
    line-height: 1.75;
    white-space: pre-wrap;
    word-break: break-word;
    max-height: 280px;
    overflow-y: auto;
    color: var(--green);
}

/* ── Alerts ── */
.alert-ok {
    background: rgba(74,240,152,0.08);
    border: 1px solid rgba(74,240,152,0.3);
    border-radius: 8px; padding: 0.75rem 1rem;
    color: var(--green); font-size: 0.82rem; margin: 0.5rem 0;
}
.alert-err {
    background: rgba(255,92,122,0.08);
    border: 1px solid rgba(255,92,122,0.3);
    border-radius: 8px; padding: 0.75rem 1rem;
    color: var(--red); font-size: 0.82rem; margin: 0.5rem 0;
}

/* ── Chips ── */
.chip {
    display: inline-block;
    background: rgba(108,99,255,0.12);
    border: 1px solid rgba(108,99,255,0.3);
    border-radius: 999px;
    padding: 0.15rem 0.65rem;
    font-size: 0.7rem; color: var(--accent);
    margin: 0.1rem 0.2rem 0.1rem 0;
}
.chip-gold {
    background: rgba(240,180,41,0.12) !important;
    border-color: rgba(240,180,41,0.3) !important;
    color: var(--gold) !important;
}

/* ── Footer ── */
.footer {
    text-align: center;
    color: var(--muted);
    font-size: 0.72rem;
    padding: 2rem 0 1rem;
    border-top: 1px solid var(--border);
    margin-top: 2rem;
    letter-spacing: 0.02em;
}
.footer a { color: var(--accent); text-decoration: none; }
.footer a:hover { text-decoration: underline; }
</style>
""", unsafe_allow_html=True)


# ── VOICES ────────────────────────────────────────────────────────────────────
VOICES = {
    "Aria   · Female · US" : "en-US-AriaNeural",
    "Guy    · Male   · US" : "en-US-GuyNeural",
    "Jenny  · Female · US" : "en-US-JennyNeural",
    "Davis  · Male   · US" : "en-US-DavisNeural",
    "Sonia  · Female · UK" : "en-GB-SoniaNeural",
    "Ryan   · Male   · UK" : "en-GB-RyanNeural",
    "Neerja · Female · IN" : "en-IN-NeerjaNeural",
    "Prabhat· Male   · IN" : "en-IN-PrabhatNeural",
}

PAGES = ["🖼️  Image → OCR", "🔊  Text → Speech", "🔁  Full Pipeline", "💬  Feedback"]

# ── Brand header ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="cv-navbar">
  <div class="cv-brand">
    <span class="cv-brand-icon">🧠</span>
    <span class="cv-brand-name">CogniVox</span>
    <span class="cv-brand-by">by Samyak Jain</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Single source of truth: st.radio styled as pill tabs ─────────────────────
page = st.radio(
    "nav",
    PAGES,
    horizontal=True,
    label_visibility="collapsed",
    key="page",
)


# ═══════════════════════════════════════════════════════════════════════════════
# UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

def prepare_image_bytes(uploaded_file) -> bytes:
    """Convert ANY uploaded image format → JPEG bytes for Azure CV."""
    uploaded_file.seek(0)
    img = Image.open(uploaded_file)
    if img.mode in ("RGBA", "LA"):
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[-1])
        img = bg
    elif img.mode == "P":
        img = img.convert("RGBA")
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[-1])
        img = bg
    elif img.mode != "RGB":
        img = img.convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    return buf.getvalue()


def azure_ocr(image_bytes: bytes) -> str:
    """Submit JPEG bytes to Azure Read API v3.2, poll and return text."""
    url = CV_ENDPOINT.rstrip("/") + "/vision/v3.2/read/analyze"
    headers = {
        "Ocp-Apim-Subscription-Key": CV_KEY,
        "Content-Type": "application/octet-stream",
    }
    r = requests.post(url, headers=headers, params={"language": "en"},
                      data=image_bytes, timeout=30)
    if r.status_code not in (200, 202):
        raise RuntimeError(f"Azure OCR submit failed: {r.status_code} – {r.text[:400]}")
    op_url = r.headers.get("Operation-Location", "")
    if not op_url:
        raise RuntimeError("Azure OCR returned no Operation-Location header.")
    poll_hdrs = {"Ocp-Apim-Subscription-Key": CV_KEY}
    for _ in range(30):
        time.sleep(1)
        poll = requests.get(op_url, headers=poll_hdrs, timeout=15)
        data = poll.json()
        status = data.get("status", "")
        if status == "succeeded":
            lines = []
            for pg in data.get("analyzeResult", {}).get("readResults", []):
                for line in pg.get("lines", []):
                    lines.append(line.get("text", ""))
            return "\n".join(lines) or "(No text detected in this image)"
        if status == "failed":
            raise RuntimeError("Azure OCR analysis failed on the server side.")
    raise RuntimeError("Azure OCR timed out (>30 s). Try a smaller or clearer image.")


def azure_tts(text: str, voice: str, rate: int, pitch: int) -> bytes:
    """Synthesise text via Azure Neural TTS REST, return WAV bytes."""
    token_url = f"https://{SPEECH_REGION}.api.cognitive.microsoft.com/sts/v1.0/issueToken"
    tok = requests.post(token_url,
                        headers={"Ocp-Apim-Subscription-Key": SPEECH_KEY},
                        timeout=10)
    if tok.status_code != 200:
        raise RuntimeError(f"TTS token request failed: {tok.status_code} – {tok.text[:200]}")
    token = tok.text
    safe = (text.replace("&", "&amp;").replace("<", "&lt;")
                .replace(">", "&gt;").replace('"', "&quot;").replace("'", "&apos;"))
    ssml = (f"<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-US'>"
            f"<voice name='{voice}'>"
            f"<prosody rate='{rate:+d}%' pitch='{pitch:+d}Hz'>{safe}</prosody>"
            f"</voice></speak>")
    tts_url = f"https://{SPEECH_REGION}.tts.speech.microsoft.com/cognitiveservices/v1"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/ssml+xml",
        "X-Microsoft-OutputFormat": "riff-24khz-16bit-mono-pcm",
        "User-Agent": "CogniVoxApp",
    }
    r = requests.post(tts_url, headers=headers, data=ssml.encode("utf-8"), timeout=30)
    if r.status_code != 200:
        raise RuntimeError(f"TTS synthesis failed: {r.status_code} – {r.text[:200]}")
    return r.content


def submit_feedback(name: str, email: str, rating: str, message: str) -> bool:
    r = requests.post(
        f"https://formspree.io/f/{FORMSPREE_ID}",
        data={"name": name, "email": email, "rating": rating, "message": message},
        headers={"Accept": "application/json"},
        timeout=15,
    )
    return r.status_code == 200


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — Image → OCR
# ═══════════════════════════════════════════════════════════════════════════════
if "🖼️  Image → OCR" in page:

    if not st.session_state.get("ocr_text"):
        st.markdown("""
        <div style='text-align:center;padding:2.5rem 1rem 2rem;'>
            <div style='font-size:3.5rem;margin-bottom:0.5rem;
                        filter:drop-shadow(0 0 40px #6c63ffaa);'>🧠</div>
            <div style='font-family:Syne,sans-serif;
                        font-size:clamp(2.4rem,6vw,4rem);
                        font-weight:800;line-height:1.0;letter-spacing:-0.03em;
                        background:linear-gradient(130deg,#ffffff 25%,#6c63ff 65%,#a78bfa 100%);
                        -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                        background-clip:text;margin-bottom:0.4rem;'>
                CogniVox
            </div>
            <div style='font-size:0.78rem;color:#8888b0;line-height:1.9;
                        font-style:italic;max-width:440px;margin:0.8rem auto 1.6rem;'>
                "Every image holds a story.<br>
                <span style='color:#6c63ff;font-style:normal;font-weight:600;
                             font-family:Syne,sans-serif;'>CogniVox</span>
                gives it a voice."
            </div>
            <div style='display:flex;justify-content:center;gap:0.7rem;flex-wrap:wrap;'>
                <span class='chip'>🔍 Azure OCR</span>
                <span class='chip'>🔊 Neural TTS</span>
                <span class='chip chip-gold'>⚡ East US</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class='hero-wrap'>
        <div class='section-tag'>Step 1 of 3</div>
        <div class='hero-title'>Image → Text</div>
        <div class='hero-sub'>Upload any image · Azure Computer Vision extracts every word</div>
    </div>""", unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "Drop image here — PNG · JPG · WEBP · BMP · TIFF",
        type=["png", "jpg", "jpeg", "webp", "bmp", "tiff"],
    )

    if uploaded:
        col_img, col_res = st.columns([1, 1], gap="large")
        with col_img:
            uploaded.seek(0)
            st.image(Image.open(uploaded), use_container_width=True, caption=uploaded.name)
        with col_res:
            st.markdown("<div class='section-tag'>Extracted Text</div>", unsafe_allow_html=True)
            if st.button("⚡  Run OCR", key="ocr_btn"):
                with st.spinner("Sending to Azure Computer Vision…"):
                    try:
                        img_bytes = prepare_image_bytes(uploaded)
                        text = azure_ocr(img_bytes)
                        st.session_state["ocr_text"] = text
                    except Exception as e:
                        st.markdown(f"<div class='alert-err'>❌ {e}</div>",
                                    unsafe_allow_html=True)
            if st.session_state.get("ocr_text"):
                st.markdown(f"<div class='ocr-box'>{st.session_state['ocr_text']}</div>",
                            unsafe_allow_html=True)
                st.download_button("⬇  Download .txt",
                                   st.session_state["ocr_text"],
                                   file_name="extracted_text.txt",
                                   mime="text/plain")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — Text → Speech
# ═══════════════════════════════════════════════════════════════════════════════
elif "🔊  Text → Speech" in page:
    st.markdown("""
    <div class='hero-wrap'>
        <div class='section-tag'>Step 2 of 3</div>
        <div class='hero-title'>Text → Voice</div>
        <div class='hero-sub'>Paste any text · choose a neural voice · hear it speak</div>
    </div>""", unsafe_allow_html=True)

    col_l, col_r = st.columns([3, 2], gap="large")
    with col_l:
        st.markdown("<div class='section-tag'>Input Text</div>", unsafe_allow_html=True)
        user_text = st.text_area("txt", value=st.session_state.get("ocr_text", ""),
                                  height=210,
                                  placeholder="Type or paste your text here…",
                                  label_visibility="collapsed")
    with col_r:
        st.markdown("<div class='section-tag'>Voice Settings</div>", unsafe_allow_html=True)
        voice_label = st.selectbox("Voice", list(VOICES.keys()))
        rate  = st.slider("Speed  (%)", -50, 100, 0, step=5)
        pitch = st.slider("Pitch  (Hz)", -20, 20, 0, step=2)

    if st.button("🔊  Synthesise Speech", key="tts_btn"):
        if not user_text.strip():
            st.warning("Please enter some text first.")
        else:
            with st.spinner("Calling Azure Neural TTS…"):
                try:
                    audio = azure_tts(user_text.strip(), VOICES[voice_label], rate, pitch)
                    st.session_state["audio_bytes"] = audio
                    st.markdown("<div class='alert-ok'>✅ Audio ready!</div>",
                                unsafe_allow_html=True)
                except Exception as e:
                    st.markdown(f"<div class='alert-err'>❌ {e}</div>",
                                unsafe_allow_html=True)

    if st.session_state.get("audio_bytes"):
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<div class='section-tag'>Playback</div>", unsafe_allow_html=True)
        st.audio(st.session_state["audio_bytes"], format="audio/wav")
        st.download_button("⬇  Download .wav",
                           st.session_state["audio_bytes"],
                           file_name="cognivox_speech.wav",
                           mime="audio/wav")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — Full Pipeline
# ═══════════════════════════════════════════════════════════════════════════════
elif "🔁  Full Pipeline" in page:
    st.markdown("""
    <div class='hero-wrap'>
        <div class='section-tag'>End-to-end</div>
        <div class='hero-title'>Image → OCR → Voice</div>
        <div class='hero-sub'>Upload an image and hear its text — all in one click</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class='card card-accent' style='display:flex;gap:1.5rem;flex-wrap:wrap;
         align-items:center;margin-bottom:1.4rem;'>
        <div class='step-row'><span class='step-badge'>1</span>Upload</div>
        <span style='color:#3a3a5a;'>──▶</span>
        <div class='step-row'><span class='step-badge'>2</span>OCR</div>
        <span style='color:#3a3a5a;'>──▶</span>
        <div class='step-row'><span class='step-badge'>3</span>TTS</div>
        <span style='color:#3a3a5a;'>──▶</span>
        <div class='step-row'>
            <span class='step-badge' style='background:#f0b429;color:#07070e;'>▶</span>Play
        </div>
    </div>""", unsafe_allow_html=True)

    col_up, col_cfg = st.columns([2, 1], gap="large")
    with col_up:
        uploaded_p = st.file_uploader(
            "Image (PNG · JPG · WEBP · BMP · TIFF)",
            type=["png", "jpg", "jpeg", "webp", "bmp", "tiff"],
            key="pipeline_upload",
        )
        if uploaded_p:
            uploaded_p.seek(0)
            st.image(Image.open(uploaded_p), use_container_width=True, caption=uploaded_p.name)
    with col_cfg:
        st.markdown("<div class='section-tag'>Voice Settings</div>", unsafe_allow_html=True)
        p_voice = st.selectbox("Voice", list(VOICES.keys()), key="p_voice")
        p_rate  = st.slider("Speed (%)",  -50, 100, 0, 5,  key="p_rate")
        p_pitch = st.slider("Pitch (Hz)", -20,  20, 0, 2,  key="p_pitch")

    if st.button("⚡  Extract & Speak", key="pipeline_btn"):
        if not uploaded_p:
            st.warning("Please upload an image first.")
        else:
            prog = st.progress(0, text="Preparing image…")
            try:
                img_bytes = prepare_image_bytes(uploaded_p)
                prog.progress(15, text="Sending to Azure OCR…")
                ocr_text = azure_ocr(img_bytes)
                prog.progress(55, text="OCR done — synthesising voice…")
                st.markdown("<div class='section-tag'>Extracted Text</div>",
                            unsafe_allow_html=True)
                st.markdown(f"<div class='ocr-box'>{ocr_text}</div>",
                            unsafe_allow_html=True)
                audio = azure_tts(ocr_text, VOICES[p_voice], p_rate, p_pitch)
                prog.progress(100, text="Done ✅")
                st.markdown("<hr>", unsafe_allow_html=True)
                st.markdown("<div class='section-tag'>Generated Audio</div>",
                            unsafe_allow_html=True)
                st.audio(audio, format="audio/wav")
                dl1, dl2 = st.columns(2)
                with dl1:
                    st.download_button("⬇  Text (.txt)", ocr_text, "ocr_text.txt", "text/plain")
                with dl2:
                    st.download_button("⬇  Audio (.wav)", audio, "cognivox.wav", "audio/wav")
            except Exception as e:
                prog.empty()
                st.markdown(f"<div class='alert-err'>❌ {e}</div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — Feedback
# ═══════════════════════════════════════════════════════════════════════════════
elif "💬  Feedback" in page:
    st.markdown("""
    <div class='hero-wrap'>
        <div class='section-tag'>We'd love to hear from you</div>
        <div class='hero-title'>Feedback</div>
        <div class='hero-sub'>Help Samyak Jain improve CogniVox · takes 30 seconds</div>
    </div>""", unsafe_allow_html=True)

    col_f, col_info = st.columns([3, 2], gap="large")
    with col_f:
        f_name    = st.text_input("Your Name",     placeholder="e.g. Rahul Sharma")
        f_email   = st.text_input("Email Address", placeholder="hello@example.com")
        f_rating  = st.select_slider(
            "Overall Rating",
            options=["⭐ Poor","⭐⭐ Fair","⭐⭐⭐ Good","⭐⭐⭐⭐ Great","⭐⭐⭐⭐⭐ Excellent"],
            value="⭐⭐⭐⭐ Great",
        )
        f_message = st.text_area("Your Message", height=150,
                                  placeholder="What worked well? What can be improved?")
        if st.button("📨  Send Feedback", key="fb_btn"):
            if not f_name.strip() or not f_email.strip() or not f_message.strip():
                st.warning("Please fill in all fields before submitting.")
            else:
                with st.spinner("Submitting…"):
                    ok = submit_feedback(f_name, f_email, f_rating, f_message)
                if ok:
                    st.markdown("<div class='alert-ok'>✅ Thank you! Feedback submitted.</div>",
                                unsafe_allow_html=True)
                else:
                    st.markdown("<div class='alert-err'>❌ Submission failed — please try again.</div>",
                                unsafe_allow_html=True)

    with col_info:
        st.markdown("""
        <div class='card card-accent'>
            <div class='section-tag'>About the Developer</div>
            <div style='font-family:Syne,sans-serif;font-size:1.25rem;
                        font-weight:800;color:#fff;margin:0.5rem 0 0.3rem;'>
                Samyak Jain
            </div>
            <div style='font-size:0.78rem;color:#7070a0;line-height:1.85;margin-bottom:1rem;'>
                AI &amp; Cloud enthusiast building intelligent
                tools powered by Azure Cognitive Services.
            </div>
            <a href='https://www.linkedin.com/in/samyak-jainxd' target='_blank'
               style='display:inline-flex;align-items:center;gap:0.45rem;
                      background:rgba(108,99,255,0.13);border:1px solid rgba(108,99,255,0.38);
                      border-radius:8px;padding:0.45rem 1rem;color:#6c63ff;
                      text-decoration:none;font-size:0.78rem;font-weight:600;'>
                🔗 Connect on LinkedIn
            </a>
        </div>
        <div class='card card-gold' style='margin-top:0.8rem;'>
            <div class='section-tag'>Pipeline</div>
            <div style='font-size:0.78rem;color:#7070a0;line-height:2.1;'>
                🖼️ Image upload (any format)<br>
                🔍 Azure Computer Vision OCR<br>
                🔊 Azure Neural TTS (8 voices)<br>
                ⬇️ Download text &amp; audio<br>
                💬 Formspree feedback form
            </div>
        </div>
        """, unsafe_allow_html=True)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class='footer'>
    Crafted with ❤️ by&nbsp;
    <a href='https://www.linkedin.com/in/samyak-jainxd' target='_blank'>Samyak Jain</a>
    &nbsp;·&nbsp; Powered by Azure Cognitive Services
    &nbsp;·&nbsp; © 2025 CogniVox
</div>
""", unsafe_allow_html=True)
