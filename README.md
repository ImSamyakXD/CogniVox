# 🧠 CogniVox

> **"Every image holds a story. CogniVox gives it a voice."**

CogniVox is an AI-powered web application that extracts text from images using **Azure Computer Vision OCR** and converts it to natural-sounding speech using **Azure Neural Text-to-Speech** — all inside a sleek, dark-themed Streamlit interface.

Built by **[Samyak Jain](https://www.linkedin.com/in/samyak-jainxd)** · Powered by Microsoft Azure Cognitive Services

---

## ✨ Features

| Feature | Description |
|---|---|
| 🖼️ **Image → OCR** | Upload any image (PNG, JPG, WEBP, BMP, TIFF) and extract all text using Azure Computer Vision Read API v3.2 |
| 🔊 **Text → Speech** | Paste or type any text, pick from 8 neural voices, control speed & pitch, and synthesise a WAV file |
| 🔁 **Full Pipeline** | One-click end-to-end flow: upload an image → OCR → TTS → playback & download |
| 💬 **Feedback** | In-app feedback form (powered by Formspree) with star rating |
| ⬇️ **Downloads** | Export extracted text as `.txt` and synthesised audio as `.wav` |

---

## 🗂️ Project Structure

```
cognivox/
├── cognivox.py       # Main Streamlit application
├── README.md         # This file
└── requirements.txt  # Python dependencies
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- An **Azure** account with:
  - **Computer Vision** resource (for OCR)
  - **Speech Services** resource (for TTS)
- A **Formspree** account (for the feedback form)

### 1. Clone the repository

```bash
git clone https://github.com/your-username/cognivox.git
cd cognivox
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure credentials

Open `cognivox.py` and update the credentials at the top of the file:

```python
CV_KEY        = "your_azure_computer_vision_key"
CV_ENDPOINT   = "https://your-resource.cognitiveservices.azure.com/"
SPEECH_KEY    = "your_azure_speech_key"
SPEECH_REGION = "eastus"           # Your Azure region
FORMSPREE_ID  = "your_formspree_id"
```

> ⚠️ **Security note:** For production use, store credentials in environment variables or a `.env` file and load them with `python-dotenv`. Never commit API keys to version control.

### 4. Run the app

```bash
streamlit run cognivox.py
```

The app will open at `http://localhost:8501` in your browser.

---

## 📦 Dependencies

```txt
streamlit
requests
Pillow
```

Install all at once:

```bash
pip install streamlit requests Pillow
```

---

## 🎙️ Available Neural Voices

| Label | Voice ID | Gender | Region |
|---|---|---|---|
| Aria | `en-US-AriaNeural` | Female | US |
| Guy | `en-US-GuyNeural` | Male | US |
| Jenny | `en-US-JennyNeural` | Female | US |
| Davis | `en-US-DavisNeural` | Male | US |
| Sonia | `en-GB-SoniaNeural` | Female | UK |
| Ryan | `en-GB-RyanNeural` | Male | UK |
| Neerja | `en-IN-NeerjaNeural` | Female | India |
| Prabhat | `en-IN-PrabhatNeural` | Male | India |

---

## 🔧 How It Works

### OCR Pipeline

```
User uploads image
        ↓
PIL converts to JPEG (handles RGBA, P-mode, etc.)
        ↓
POST to Azure Computer Vision Read API v3.2
        ↓
Poll Operation-Location URL until status = "succeeded"
        ↓
Concatenate all detected lines → display + download
```

### TTS Pipeline

```
User provides text + voice settings
        ↓
POST to Azure STS endpoint → fetch Bearer token
        ↓
Build SSML with prosody (rate %, pitch Hz)
        ↓
POST to Azure Neural TTS endpoint
        ↓
Receive riff-24khz-16bit-mono-pcm WAV → playback + download
```

---

## 🎨 Design

- **Theme:** Deep dark (`#07070e` base) with purple accent (`#6c63ff`)
- **Fonts:** Syne (headings / UI) · DM Mono (body / code)
- **Navigation:** Horizontal pill-tab radio bar — no sidebar, fully responsive
- **No Streamlit chrome:** Header, footer, menu and deploy button all hidden for a clean app feel

---

## 🌐 Deploying to Streamlit Cloud

1. Push the repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) and connect your repo
3. Add your secrets in **Settings → Secrets**:

```toml
CV_KEY = "your_key"
CV_ENDPOINT = "https://your-endpoint.cognitiveservices.azure.com/"
SPEECH_KEY = "your_key"
SPEECH_REGION = "eastus"
FORMSPREE_ID = "your_id"
```

4. Update `cognivox.py` to read from `st.secrets`:

```python
CV_KEY     = st.secrets["CV_KEY"]
CV_ENDPOINT = st.secrets["CV_ENDPOINT"]
# etc.
```

---

## ⚠️ Known Limitations

- OCR polls for up to **30 seconds**; very large or complex images may time out — use compressed or cropped images for best results
- TTS is limited to the **Azure Neural TTS character quota** of your subscription tier
- Formspree free tier allows **50 submissions/month**

---

## 👨‍💻 Developer

**Samyak Jain**  
AI & Cloud enthusiast building intelligent tools powered by Azure Cognitive Services.

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?logo=linkedin)](https://www.linkedin.com/in/samyak-jainxd)

---

## 📄 License

This project is for educational and portfolio purposes. Azure Cognitive Services usage is subject to [Microsoft's Terms of Service](https://azure.microsoft.com/en-us/support/legal/).
