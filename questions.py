from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from resources import cv, jd
from dotenv import load_dotenv

load_dotenv()

class Response(BaseModel):
    question : list[str] = Field(description= "List of questions")

llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
)

llm_with_tools = llm.bind_tools([Response], strict = True)

system_message = """

You are a senior CV optimizer. Given a CV and a job description. Your job is to deeply analyse the CV
against the provided Job description and identify the attribute gaps.

These attributes should be a good mix of technical and non technical attributes.

Look for key things the recruiter of the job might want from the candidate that is actually missing in the CV.

Based on your analysis prepare 15 questions to ask from the candidate to address these skill gaps.
There can be many skills the candidate might have that are required for the job but might not have 
replicated in the CV, your job is to get those information from the user.

Tailor the questions based on their CV so that the questions feel personal.

Note : You are not an interviewer, You are an CV optimizer who will help the candidate to optimize his CV.
SO be polite, helpful and ask your questions elaborate and simpler. This is very important. If you did not follow
this you will be fired.

**YOU SHOULD ASK ATELAST 15 QUESTIONS**

"""

human_message = """

Here's the candidate's CV : {CV}

This is the role the candidate is targetting : {JD}

"""

prompt = ChatPromptTemplate.from_messages(
    [
        ("system",system_message,),
        ("human", human_message),
    ]
)

prompt_value_dict = {
    "CV": cv,
    "JD": jd,
}

chain = prompt | llm_with_tools

response = chain.invoke(prompt_value_dict)
response_dict = response.tool_calls

print(response_dict[0]["args"]["question"])








