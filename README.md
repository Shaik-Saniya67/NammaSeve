# NammaSeve

**Understand every Kannada notice, clearly.**

NammaSeve helps people understand Kannada public notices in Kannada, Telugu, Hindi, or English. Upload a PDF or image, get a simple explanation, ask questions grounded in the notice, inspect the extracted original text, and optionally listen to the explanation.

## Visual refresh

- **Karnataka-inspired landing page**: a Dravidian temple tower built from real 3D CSS (with depth, side faces and a gentle sway), a glowing sun with rotating rays, Western Ghats-style hills, Mysore-silk zari border, the Kannada flag colours (yellow and red), and heritage chips for Hampi, Mysuru, Belur, Halebidu and Badami.
- **3D living background** on every page: a slowly turning rangoli floor in perspective, a tilted rotating mandala, floating gold orbs and drifting marigold petals. No JavaScript or images needed.
- **Premium transitions**: a stage-curtain opening on first load, a soft ivory dissolve when entering the app, staggered card reveals, 3D tilt on hover and shimmering buttons.
- Palette: warm ivory `#F6EEDA`, espresso `#241711`, kumkum red `#A4231B`, turmeric gold `#D99A1E`.
- Glass-style cards, refined form controls, responsive layout and reduced-motion support.
- All features, logic and settings are unchanged: only the look and feel was updated.

## Run on Windows

1. Keep your existing `.env` file in this folder. **Do not replace it with `.env.example`**, because `.env` contains your private API key.
2. Open PowerShell in this folder and install dependencies:

   ```powershell
   py -m pip install -r requirements.txt
   ```

3. Confirm `.env` contains your real Groq key and Tesseract settings, for example:

   ```dotenv
   GROQ_API_KEY=your_real_key_here
   TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
   TESSERACT_LANG=kan+eng
   ```

   Replace the placeholder with your real key. Never share it or commit `.env` to GitHub.

4. Start the app:

   ```powershell
   py -m streamlit run app.py
   ```

## OCR requirement

For scanned PDFs and images, install the Windows Tesseract OCR application with Kannada (`kan`) and English (`eng`) language data. The Python package `pytesseract` is also required; both are included in the setup instructions above.

## Files

- `app.py` — Streamlit interface and Groq-powered explanation/Q&A.
- `document_reader.py` — PDF text extraction and OCR fallback.
- `speech.py` — read-aloud audio generation.
- `requirements.txt` — Python dependencies.
- `.env.example` — configuration template; copy values into your own `.env` without exposing secrets.
