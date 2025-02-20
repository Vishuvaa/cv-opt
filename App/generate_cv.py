from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from prompts import prompts
from langchain.output_parsers import PydanticOutputParser
from typing import List

class MonthYear(BaseModel):
    month : str = Field(description="The month of the year")
    year : str = Field(description="The year of the month")

class Education(BaseModel):
    degree : str = Field(description="Name of the degree")
    institute : str = Field(description="The institute of the degree")
    year : MonthYear = Field(description="The year of graduation")

class WorkExperience(BaseModel):
    company : str = Field(description="The company name")
    role : str = Field(description="The role")
    description : str = Field(description="The description of the roles and responsibilities")
    start_date : str = Field(description="The start date of the job")
    end_date : str = Field(description="The end date of the job")

class Project(BaseModel):
    name : str = Field(description="The name of the project")
    description : str = Field(description="The description of the project")

class Courses(BaseModel):
    name : str = Field(description= "Name of additional courses other than degree")
    description : str = Field(description="Description of additional courses")

class Certifications(BaseModel):
    name : str = Field(description="The name of the certification")
    description : str = Field(description="Short description on the certification")

class CV(BaseModel) :
    name : str = Field( description="The name of the person")
    email : str = Field( description="The email of the person")
    phone : str = Field( description="The phone number of the person")
    location : str = Field( description="The location of the person")
    education :List[Education] = Field( description="The education of the person")
    work_experience : List[WorkExperience] = Field( description="The work experience of the person")
    skills : List[str] = Field( description="The skills of the person")
    projects : List[Project] = Field(description="The projects of the person")
    courses : List[Courses] = Field( description="The additional courses other than degree")
    certifications : List[Certifications] = Field( description="The certifications of the person")

def generatecv(cv, jd, transcript):

    llm = ChatOpenAI(model="gpt-4o-mini",temperature=0)

    system_message = prompts["cv generater"]["system"]
    human_message = prompts["cv generater"]["human"]

    prompt_tuple = [
            ("system", system_message),
            ("human", human_message)
        ]
    
    prompt_value_dict = {
            "cv": cv,
            "jd": jd,
            "transcript" : transcript
        }
    
    prompt = ChatPromptTemplate.from_messages(prompt_tuple)
    parser = PydanticOutputParser(pydantic_object=CV)
    format_instructions =  parser.get_format_instructions() 
    prompt_value_dict["format_instructions"] = str(format_instructions)


    chain = prompt | llm

    response = chain.invoke(prompt_value_dict)
    result = parser.parse(response.content)    

    return result.model_dump()
