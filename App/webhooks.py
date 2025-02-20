
from fastapi import FastAPI, Request, File, WebSocket, WebSocketDisconnect, UploadFile
import json
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
import sys

questions = ['Your CV highlights experience with various LLMs and NLP tasks. Can you describe a project where you had to fine-tune a large language model for a specific application, detailing the challenges you faced and how you overcame them?',
 'The job description emphasizes experience with RAG (Retrieval-Augmented Generation).  Describe your experience building and deploying RAG systems. What were some key design decisions you made, and what were the performance implications of those choices?',
 "You've worked with both TensorFlow and PyTorch.  Can you compare and contrast your experiences with these frameworks, particularly in the context of LLM development and deployment?  Which would you choose for a specific task and why?",
 'This role requires collaboration with instructional designers.  Describe a situation where you successfully collaborated with a non-technical team to achieve a shared goal. What communication strategies did you employ?',
 'The job description mentions developing metrics to evaluate LLM performance. What metrics would you use to assess the effectiveness of an AI tutor, and how would you interpret those metrics to inform model improvements?',
 'You mention experience with Flask and FastAPI.  What are the trade-offs between these frameworks, and which would you choose for building the backend services for our AI tutors, and why?',
 'Explain your understanding of MLOps and DevOps, and how these practices would apply to the continuous improvement and deployment of our AI language learning tutors.',
 'Describe your experience with A/B testing in the context of machine learning models.  How would you design an A/B test to compare different LLM architectures or prompt engineering strategies for our AI tutors?',
 'Our AI tutors need to be emotionally intuitive. How would you approach designing and implementing this aspect of the AI, considering the limitations and ethical considerations of current LLM technology?',
 'The job description mentions staying updated with the latest advancements in LLM technologies.  What are some recent advancements in LLMs that you find particularly exciting, and how do you keep yourself informed about these developments?']


questions = questions[:5]

app = FastAPI()
current_index = -1
intent = ""
def format_response(text):
    response = {
            "fulfillmentResponse": {
                "messages": [
                    {
                        "text": {
                            "text": [text]
                        }
                    }
                ]
            }
    }

    return response


@app.get("/")
async def home(request:Request):
    return "ok"

class QuestionRequest(BaseModel):
    questions: list[str]

@app.post("/send-questions/")
async def receive_questions(data: QuestionRequest):

    global questions
    # Access the list of questions
    questions = data.questions
    print(f"Received questions: {questions}")
    
    # Optionally, you can process the questions here or return them as a response
    return {"message": "Recieved sucessfully"}



@app.post("/webhook")
async def handle_webhook(request: Request):

    global current_index, intent, questions

    body = await request.json()
    pretty_body = json.dumps(body, indent=4)
    print(pretty_body)
    page_info = body.get("pageInfo", {})
    session_info = body.get("sessionInfo", {})
    current_intent = session_info.get("parameters",{}).get("$request.generative.subintent1", "")
    current_page = page_info.get('displayName', "")
    user_input = body.get("text", "")
    print("current_intent :", current_intent)
    print("user input : ", user_input)


    if current_page == 'Entry Page' and current_intent == "":
        current_index = -1
        text = "Can you tell me about yourself?"
        current_index += 1
        #response = format_response(text)
        response = format_response(text)

    elif current_index == len(questions)-1:
        text = "Thank you for joining. Your responses are recorded."
        response = format_response(text)

    elif current_page == "Entry Page" and current_intent == "answer":
        text = questions[current_index]
        current_index += 1
        #response = format_response(text)
        response = format_response(text)

    elif current_page == "Entry Page" and current_intent == "repeat":
        if current_index == 0:
            text = "Can you tell me about yourself?"
        else:
            text = questions[current_index-1]
            
        #response = format_response(text)
        response = format_response(text, intent)

    elif current_page == "Entry Page" and current_intent == "skip":
        text = questions[current_index]
        current_index += 1
        #response = format_response(text)
        response = format_response(text)

    elif current_page == "Entry Page" and current_intent == "exit":
        text = "Thank you for your time. Goodbye!"
        #response = format_response(text)
        response = format_response(text)

    return JSONResponse(content=response, status_code=200)

