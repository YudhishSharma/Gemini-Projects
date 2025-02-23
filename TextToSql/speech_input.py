import streamlit as st
import speech_recognition as sr

def get_speech_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening... Speak Now !!")
        try:
            audio = recognizer.listen(source, timeout = 7, phrase_time_limit = 10)
            text = recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            st.warning("Sorry, I could not understand what you said!")
        except sr.RequestError as e:
            st.error(f"Sorry, an error occurred while processing your request!:  {e}")