from fastapi import FastAPI, Request, Form, UploadFile, File, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates
import asyncio
import PyPDF2 as pdf
from openai import OpenAI
from prompts import prompts
from pydantic import BaseModel
from getDfResponse import run_sample
from questions import generate_questions
from fastapi.responses import JSONResponse
import uuid
import httpx
import assemblyai as aai
import os
from dotenv import load_dotenv
import time
from generate_cv import generatecv

load_dotenv()

aai.settings.api_key = os.environ.get('ASSEMBLYAI_API_KEY')
transcriber = aai.Transcriber()

cv =""
jd = ""
transcript_history = ""

session_variables = {
    "cv" : "",
    "jd" : "",
    "id" : None,
    "questions" : None,
}

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get('/')
async def name(request: Request):
    return templates.TemplateResponse('home.html', {'request': request})

def input_pdf_text(uploaded_file):
    global session_variables
    reader = pdf.PdfReader(uploaded_file.file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

@app.post("/upload")
async def upload(
    jd: str = Form(...,min_length=50),
    cv: UploadFile = File(...)
):
    global session_variables
    cv_content = input_pdf_text(cv)

    document = {
        "jd": jd,
        "cv": cv_content,
    }

    try :
        session_variables["cv"] = document["cv"]
        session_variables["jd"] = document["jd"]
        session_variables["questions"] = generate_questions(session_variables["cv"], session_variables["jd"])
        async with httpx.AsyncClient() as client:
            response = await client.post("http://127.0.0.1:8001/send-questions/", json={"questions": session_variables["questions"]})
        print(response.json())
        message ="Form submission success"
        err = "No error"
    except Exception as e:
        message = "Error while inserting data to the database."
        err = str(e)

    return {
        "message" : message,
        "error" : err
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    cv = session_variables["cv"]
    jd = session_variables["jd"]

    #"""
    
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompts["skill gap analyser"]["system"]},
            {'role': 'user', 'content': prompts["skill gap analyser"]["human"].format(cv=cv, jd=jd)}
        ],
        temperature=0,
        stream=True
    )

    # Stream OpenAI response to WebSocket
    for chunk in response:
        if chunk.choices[0].delta.content:
            await websocket.send_text(chunk.choices[0].delta.content)
        await asyncio.sleep(0)  # Yield control to event loop

    #"""
    #await websocket.send_text("Analysis")
    #await asyncio.sleep(0)
    await websocket.close()

class InputData(BaseModel):
    text: str
@app.post("/chat")
async def receive_data(input_data: InputData):
    
    global session_variables, transcript_history

    if session_variables["id"] is None:
        session_variables["id"] = str(uuid.uuid4())
        transcript_history = "Bot : Can you tell me about yourself? \n"
    

    transcript_history += f"Human :{input_data.text}\n"
    bot_response = run_sample(input_data.text, session_variables["id"])
    transcript_history += f"Bot :{bot_response}\n"
    if bot_response.strip() == "Thank you for your responses.":
        print(transcript_history)
    response_data = {"message": bot_response}
    return response_data

@app.post("/transcribe")
async def transcribe(audio: UploadFile = File(...)):
    try:
        print(audio)
        audio_bytes = await audio.read()
        transcript = transcriber.transcribe(audio_bytes)
        return JSONResponse(content={"transcript": transcript.text})
    except Exception as e:
        return JSONResponse(content={"transcript": f"Error while transcribing. Try again please. {e}"})
    
@app.post("/generateCV")
async def generate_cv(input_data: InputData):
    global session_variables, transcript_history
    print(input_data.text)# Simulating long-running task
    new_cv = generatecv(session_variables["cv"], session_variables["jd"], transcript_history)
    print(new_cv)
    return {"cv" : new_cv}

@app.get('/analyze')
async def analyze(request: Request):
    return templates.TemplateResponse('analyze.html', {'request': request})