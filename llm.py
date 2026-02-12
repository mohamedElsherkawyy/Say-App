from fastapi.responses import JSONResponse
from langchain_groq import ChatGroq
from groq import Groq
from langchain_core.output_parsers import PydanticOutputParser 
from config import groq_api_key
from models import STTRequest, STTResponse, ExpensesAnalysisRequest, ExpensesAnalysisResponse
from ocr import process_image
from prompts import STT_PROMPT_TEMPLATE, EXPENSES_ANALYSIS_PROMPT_TEMPLATE, RECEIPT_PROMPT_TEMPLATE

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    api_key=groq_api_key
)
response_parser = PydanticOutputParser(pydantic_object=STTResponse)
format_instructions = response_parser.get_format_instructions()

def process_stt(request: STTRequest ):
    prompt = STT_PROMPT_TEMPLATE.format(
        stt_text=request.stt_text,
        format_instructions=format_instructions,
    )
    try:
        response = llm.invoke(prompt)
        return {"response": response_parser.parse(response.content)}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


expenses_response_parser = PydanticOutputParser(pydantic_object=ExpensesAnalysisResponse)
expenses_format_instructions = expenses_response_parser.get_format_instructions()

def analyze_expenses(request: ExpensesAnalysisRequest):
    analysis_prompt = EXPENSES_ANALYSIS_PROMPT_TEMPLATE.format(
        transactions=request.transactions,
        format_instructions=expenses_format_instructions,
    )
    response = llm.invoke(analysis_prompt)
    try:
        return {"response": expenses_response_parser.parse(response.content)}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
    
def receipt(image_base64: str):
    """Analyze receipt via Groq vision API. Image sent as image_url, not in prompt."""
    client = Groq(api_key=groq_api_key)
    text = RECEIPT_PROMPT_TEMPLATE.format(format_instructions=format_instructions)
    try:
        r = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": text},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}},
                ],
            }],
        )
        content = r.choices[0].message.content
        return {"response": response_parser.parse(content) if content else {"category": []}}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

