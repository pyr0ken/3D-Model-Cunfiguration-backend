# speech_to_text.py
import speech_recognition as sr

def transcribe_audio(audio_data):
    recognizer = sr.Recognizer()
    audio = sr.AudioFile(audio_data)
    with audio as source:
        audio_content = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio_content)
    except sr.UnknownValueError:
        text = "Could not understand the audio"
    except sr.RequestError as e:
        text = f"Could not request results; {e}"
    return text
