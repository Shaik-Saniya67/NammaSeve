from io import BytesIO

def make_audio(text: str, language: str) -> bytes:
    from gtts import gTTS
    codes = {
        "Kannada": "kn",
        "Telugu": "te",
        "Hindi": "hi",
        "English": "en",
    }
    audio = BytesIO()
    gTTS(text=text, lang=codes.get(language, "en"), slow=False).write_to_fp(audio)
    return audio.getvalue()
