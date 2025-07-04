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
    food: Optional[str] = Field(default=None)
    transportation: Optional[str] = Field(default=None)
    shopping: Optional[str] = Field(default=None)
    fitness: Optional[str] = Field(default=None)
    clothes: Optional[str] = Field(default=None)

class STTResponse(BaseModel):
    category: list[category]

def process_stt(request: STTRequest ):
    prompt = f"""
You are a specialized assistant that processes raw speech-to-text outputs and organizes them into clear, well-structured, and accurate responses.
The text in egyptian arabic.
The text is about what the user spent money on.
Only return the amount of money spent on each category.
Try to figure out the category of the text and return the category.
Do not duplicate the list of categories.

Here is the raw STT input:
\"\"\"{request.stt_text}\"\"\"
Your task:
- Use this instructions to format your response:```format_instructions```
"""

    try:
        response_parser = PydanticOutputParser(pydantic_object=STTResponse)
        format_instructions = response_parser.get_format_instructions()
        response = llm.invoke(prompt + format_instructions)
        return {"response": response_parser.parse(response.content)}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

