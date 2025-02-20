import streamlit as st
import uuid
from getDfResponse import run_sample
import os
from dotenv import load_dotenv
import assemblyai as aai
import os
from dotenv import load_dotenv
import time

load_dotenv()

aai.settings.api_key = os.environ.get('ASSEMBLYAI_API_KEY')
transcriber = aai.Transcriber()

if "audio_data" not in st.session_state:
    st.session_state.audio_data = None

if "intro_message" not in st.session_state:
    st.session_state.intro_message = ""

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "page" not in st.session_state:
    st.session_state.page = "home"

if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("CV Optimizer")

if st.session_state.page == "home":
    st.markdown("Hello, I'm your CV Optimizing assistant. I help you in curating your CV specifically against a preferred Job description. To get started, first upload your CV.")
    cv = st.file_uploader("Upload your CV here.")
    if cv :
        st.session_state.page = "job_decription"

if st.session_state.page == "job_decription":
    st.markdown("Great! Now, please upload your preferred Job description.")
    with st.form(key='my_form'):
        jd = st.text_area("Job description", height=200)
        submit_button = st.form_submit_button("Submit")

    if submit_button:
        st.session_state.page = "questionnare"
        st.rerun()

if st.session_state.page == "questionnare":

    id = st.session_state["session_id"]

    if st.session_state.intro_message == "":
        intro= run_sample("hi", id)
        st.session_state.intro_message = intro
    def display_messages():
        for msg in st.session_state['messages']:
            with st.container():
                st.chat_message(msg['role']).markdown(msg['content'])

    with st.spinner("Loading"):
        st.markdown(st.session_state.intro_message)

    with st.container():
        display_messages()
        user_input = st.chat_input("Say something...")
        
    print("Audio data : ", st.session_state.audio_data)
    audio_key = f"audio_{int(time.time())}" 
    st.session_state["audio_data"] = st.audio_input("🎙️✨", key = str(audio_key))
    print(st.session_state.audio_data)

    if st.session_state["audio_data"]:
        transcript = transcriber.transcribe(st.session_state["audio_data"])
        user_input = transcript.text
        print("Audio data after recording: ", st.session_state["audio_data"])
        st.session_state["audio_data"] = None

    #print("Audio data : ", st.session_state.audio_data)

    if user_input:
        st.session_state['messages'].append({'role': 'user', 'content': user_input})  # Append user message
        st.session_state['messages'].append({'role': 'assistant', 'content': run_sample(user_input, id)})  # Echo response

        st.rerun()



