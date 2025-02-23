import streamlit as st
import speech_recognition as sr
import sounddevice as sd
import numpy as np
import tempfile
import wave

def get_speech_input():
    recognizer = sr.Recognizer()
    
    # Streamlit UI update
    st.info("Listening... Speak Now !!")
    
    # Define recording parameters
    sample_rate = 16000 
    duration = 7 
    
    try:
        # Record audio using sounddevice
        audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype=np.int16)
        sd.wait()  

        # Save the recorded audio to a temporary WAV file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            with wave.open(temp_audio.name, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)  # 16-bit PCM
                wf.setframerate(sample_rate)
                wf.writeframes(audio_data.tobytes())

            temp_audio_path = temp_audio.name

        # Use SpeechRecognition to process the temporary WAV file
        with sr.AudioFile(temp_audio_path) as source:
            audio = recognizer.record(source)  
            text = recognizer.recognize_google(audio) 
            return text

    except sr.UnknownValueError:
        st.warning("Sorry, I could not understand what you said!")
    except sr.RequestError as e:
        st.error(f"Sorry, an error occurred while processing your request: {e}")

    return None
