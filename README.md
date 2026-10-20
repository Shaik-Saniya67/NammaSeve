<div align="center">

# ನ &nbsp; NammaSeve

### Understand every Kannada notice, clearly.

*ನಮ್ಮ ಸೇವೆ — a calm, premium reading companion for Karnataka's public notices*

[![Live Demo](https://img.shields.io/badge/🚀_Live_Demo-nammaseve.streamlit.app-A4231B?style=for-the-badge)](https://nammaseve.streamlit.app/)
[![GitHub](https://img.shields.io/badge/GitHub-Shaik--Saniya67%2FNammaSeve-241711?style=for-the-badge&logo=github)](https://github.com/Shaik-Saniya67/NammaSeve)

![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-A4231B?style=for-the-badge)
![Groq](https://img.shields.io/badge/AI-Groq%20Llama%203.3-D99A1E?style=for-the-badge)
![Languages](https://img.shields.io/badge/Languages-ಕನ್ನಡ%20·%20తెలుగు%20·%20हिन्दी%20·%20English-5B140F?style=for-the-badge)

### 👉 [Try NammaSeve live](https://nammaseve.streamlit.app/) &nbsp;·&nbsp; [View the source on GitHub](https://github.com/Shaik-Saniya67/NammaSeve)

</div>

---

## ✨ What is NammaSeve?

Government circulars, municipal orders and public notices are often written in formal Kannada that is hard to follow. **NammaSeve** lets anyone upload a notice and instantly get a **plain-language explanation in their own language**, then ask questions and see the **exact original sentence** behind every answer.

> **Explain, don't replace.** The original text always stays within reach, and answers are grounded only in the notice you uploaded.

---

## 🎯 Who is it for, and how does it help?

| 👤 Who | 💡 How NammaSeve helps |
|---|---|
| **Citizens and families** | Understand ration card, tax, scheme and eligibility notices without a translator. |
| **Telugu, Hindi or English speakers living in Karnataka** | Read Kannada notices in the language you are most comfortable with. |
| **Elderly and first-time readers** | Hear the explanation read aloud in simple language. |
| **Students and job seekers** | Quickly pick out dates, documents and fees in exam or recruitment notices. |
| **Local helpers and volunteers** | Explain notices to others, backed by the original sentence as proof. |
| **Small businesses** | Check licence, permit and compliance notices before a deadline. |

---

## 🚀 Features

- 📄 **Upload anything**: text PDFs, scanned PDFs, and photos (PNG, JPG, JPEG, WEBP).
- 🔍 **Smart reading**: text PDFs are read directly, and scans fall back to **Kannada + English OCR**.
- 🗣️ **Explanation in your language**: Kannada, Telugu, Hindi or English.
- 🗂️ **Structured summary**: *what the notice is about, important dates, what you need to do, fees and documents.*
- 💬 **Ask the notice**: questions in any of the four languages, answered **only** from the notice.
- 🔗 **Evidence-first answers**: every answer cites the exact supporting Kannada sentence.
- 🔊 **Read aloud**: generate audio of the explanation in the chosen language.
- 🧾 **Verify**: inspect the full extracted text next to the explanation.
- 🛡️ **Honest by design**: if something isn't in the notice, it says *"Not clearly stated in the notice."*

---

## 🪔 The experience

- 🏛️ **Karnataka-inspired landing page**: a 3D Dravidian temple tower, glowing sun, Western Ghats hills, Mysore-silk border and the Kannada flag colours.
- 🌸 **Living 3D background**: a rotating rangoli floor in perspective, a tilted mandala, floating gold orbs and drifting marigold petals.
- 🎭 **Premium transitions**: a stage-curtain opening, soft dissolves between pages, staggered card reveals and 3D hover tilt.
- 🎨 **Palette**: ivory `#F6EEDA` · espresso `#241711` · kumkum red `#A4231B` · turmeric gold `#D99A1E`.
- 📱 Responsive on phones, and respects *reduced motion* settings.

---

## 🧭 How it works

```
 Upload notice ──▶ Extract text ──▶ AI explains ──▶ Ask questions ──▶ See cited sentence
  PDF / image     PyMuPDF + OCR     Groq Llama 3.3   in 4 languages    + optional audio (gTTS)
```

1. **Bring your notice**: upload a PDF, scan or photo.
2. **Understand the essentials**: pick a language and click *Read and explain notice*.
3. **Ask with confidence**: type a question and get the answer plus the original sentence.

---

## ⚡ Quick start (Windows)

> Just want to try it? Use the live app at **[nammaseve.streamlit.app](https://nammaseve.streamlit.app/)**. To run it yourself:
>
> ```powershell
> git clone https://github.com/Shaik-Saniya67/NammaSeve.git
> cd NammaSeve
> ```

1. Keep your existing `.env` file in this folder. **Do not replace it with `.env.example`**, because `.env` holds your private API key.
2. Install dependencies:

   ```powershell
   py -m pip install -r requirements.txt
   ```

3. Make sure `.env` contains your real values:

   ```dotenv
   GROQ_API_KEY=your_real_key_here
   GROQ_MODEL=openai/gpt-oss-120b
   TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
   TESSERACT_LANG=kan+eng
   ```

4. Run:

   ```powershell
   py -m streamlit run app.py
   ```

> 🔐 Never share your API key or commit `.env` to GitHub. It is already in `.gitignore`.

### OCR requirement
For scanned PDFs and photos, install **Tesseract OCR** with the Kannada (`kan`) and English (`eng`) language data. Text-based PDFs work without it.

---

## 🛠️ Tech stack

| Layer | Tool |
|---|---|
| Interface | Streamlit with custom CSS (no JavaScript) |
| AI explanation and Q&A | Groq API, `openai/gpt-oss-120b` |
| PDF reading | PyMuPDF |
| OCR | Tesseract via `pytesseract`, plus Pillow |
| Read-aloud | gTTS |
| Landing auto-enter | streamlit-autorefresh |

## 📁 Project files

| File | Purpose |
|---|---|
| `app.py` | Streamlit interface, premium design, Groq explanation and Q&A |
| `document_reader.py` | PDF text extraction with OCR fallback |
| `speech.py` | Read-aloud audio generation |
| `requirements.txt` | Python dependencies |
| `.env.example` | Configuration template (copy values into your own `.env`) |

---

## 🩺 Troubleshooting

| Problem | Fix |
|---|---|
| *"Add your Groq API key…"* | Put `GROQ_API_KEY` in `.env` beside `app.py` and restart. |
| *"We couldn't extract enough text"* | Use a clearer photo or a text-based PDF. |
| *OCR failed / missing languages* | Install Tesseract with `kan` and `eng`, and check `TESSERACT_CMD`. |
| Fonts look plain | Kannada and Telugu fonts load from Google Fonts, so an internet connection is needed. |

---

<div align="center">

**Rooted in Karnataka. Designed for understanding.** 🪔

*NammaSeve supports understanding; it does not replace official clarification from the issuing authority.*

</div>
