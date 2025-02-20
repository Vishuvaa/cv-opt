import streamlit as st
import assemblyai as aai
import os
from dotenv import load_dotenv

load_dotenv()

aai.settings.api_key = os.environ.get('ASSEMBLYAI_API_KEY')
transcriber = aai.Transcriber()

st.title("🎙️ Streamlit Audio Recorder with Local Storage")

# Initialize session state for recording status
if "recording" not in st.session_state:
    st.session_state.recording = False

# Toggle button to start/stop recording
if st.button("🎤 Start/Stop Recording"):
    st.session_state.recording = not st.session_state.recording

# Show recording status
if st.session_state.recording:
    st.write("🔴 Recording... Speak now!")

# Audio input component (appears only when recording)
if st.session_state.recording:
    audio_data = st.audio_input("Record your voice")
else:
    audio_data = None

# Save the recorded audio locally
if audio_data is not None:
    transcript = transcriber.transcribe(audio_data)
    st.write(transcript.text)
