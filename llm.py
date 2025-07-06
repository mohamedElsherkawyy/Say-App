import os
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
from pydantic import BaseModel , Field
from typing import List, Union, Optional
from langchain_groq import ChatGroq
from langchain_core.output_parsers import PydanticOutputParser 

load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    raise ValueError("GROQ_API_KEY not found in environment variables")

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    api_key=groq_api_key
)

class STTRequest(BaseModel):
    stt_text: str

class category(BaseModel):
    food: Optional[str] = Field(default=None, description="The amount of money spent on food , drinks , coffee shops , restaurants , etc")
    transportation: Optional[str] = Field(default=None, description="The amount of money spent on transportation , taxi , bus , metro , etc")
    travel: Optional[str] = Field(default=None, description="The amount of money spent on travel , hotel , airbnb , etc")
    shopping: Optional[str] = Field(default=None, description="The amount of money spent on shopping , clothes , shoes , etc , not including food and drinks")
    fitness: Optional[str] = Field(default=None, description="The amount of money spent on fitness , gym , yoga , etc")
    entertainment: Optional[str] = Field(default=None, description="The amount of money spent on entertainment , movies , concerts , games , etc")


class STTResponse(BaseModel):
    category: list[category]

def process_stt(request: STTRequest ):
    prompt = f"""
You are a specialized assistant that processes raw speech-to-text outputs and ocr outputs and organizes them into categories.
The text in egyptian arabic.
The text is about what the user spent money on.
Only return the amount of money spent on each category.
Do not return the currency of the amount of money spent.
When the user says "I spent 1000 and 5000 egyptian pounds on food" you should return the amount of money spent on food as 6000 egyptian pounds.

Here is the raw STT input:
\"\"\"{request.stt_text}\"\"\"
Your task:
- Use this instructions to format your response:```format_instructions```
- Make sure to return one list of categories and not multiple lists.
- Try to figure out the category of the text and return the category.
"""
    try:
        response_parser = PydanticOutputParser(pydantic_object=STTResponse)
        format_instructions = response_parser.get_format_instructions()
        response = llm.invoke(prompt + format_instructions)
        return {"response": response_parser.parse(response.content)}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

