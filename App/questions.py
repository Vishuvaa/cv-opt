from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from prompts import prompts
from langchain.output_parsers import PydanticOutputParser

def generate_questions(cv, jd) -> str :

    llm = ChatOpenAI(model="gpt-4o-mini",temperature=0)

    class questions(BaseModel):
        question : list[str] = Field(description = "List of questions")


    system_message = prompts["question generator"]["system"]
    human_message = prompts["question generator"]["human"]

    prompt_tuple = [
            ("system", system_message),
            ("human", human_message)
        ]
    
    prompt_value_dict = {
            "jd": jd,
            "cv": cv,
        }
    
    prompt = ChatPromptTemplate.from_messages(prompt_tuple)
    parser = PydanticOutputParser(pydantic_object=questions)
    format_instructions =  parser.get_format_instructions() # parsing format instructions
    prompt_value_dict["format_instructions"] = str(format_instructions)


    chain = prompt | llm

    response = chain.invoke(prompt_value_dict)
    result = parser.parse(response.content)    

    return result.question





    
