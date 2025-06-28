# utils/voice.py

import pyttsx3

def speak(text):
    try:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    except RuntimeError as e:
        print("Speech error:", e)

def listen():
    import speech_recognition as sr
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)

    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return "Sorry, I couldn't understand that."
    except sr.RequestError:
        return "Could not request results from Google Speech Recognition."
