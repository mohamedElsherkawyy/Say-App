from fastapi.responses import JSONResponse
from langchain_groq import ChatGroq
from langchain_core.output_parsers import PydanticOutputParser 
from config import groq_api_key
from models import STTRequest, STTResponse

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    api_key=groq_api_key
)

response_parser = PydanticOutputParser(pydantic_object=STTResponse)
format_instructions = response_parser.get_format_instructions()

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
        - Use this instructions to format your response:```{format_instructions}```
        - Make sure to return one list of categories and not multiple lists.
        - Try to figure out the category of the text and return the category.
        - if the text have Subtotal and Total take Total.
        """
    try:
        response = llm.invoke(prompt)
        return {"response": response_parser.parse(response.content)}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

