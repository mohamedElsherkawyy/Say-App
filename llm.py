from fastapi.responses import JSONResponse
from langchain_groq import ChatGroq
from langchain_core.output_parsers import PydanticOutputParser 
from config import groq_api_key
from models import STTRequest, STTResponse, ExpensesAnalysisRequest, ExpensesAnalysisResponse

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
        - If the text have Subtotal and Total take Total.
        """
    try:
        response = llm.invoke(prompt)
        return {"response": response_parser.parse(response.content)}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


expenses_response_parser = PydanticOutputParser(pydantic_object=ExpensesAnalysisResponse)
expenses_format_instructions = expenses_response_parser.get_format_instructions()

def analyze_expenses(request: ExpensesAnalysisRequest):
    analysis_prompt = f"""
        You are an AI Language Engine specialized in Egyptian Arabic (عامية مصرية).
        You work inside a personal finance app called "احسبهالي" which is a voice assistant that can help you with your expenses and income.
        Here is the transactions:
        \"\"\"{request.transactions}\"\"\"

        Your ONLY responsibility:
        - Convert pre-calculated analytics & alerts into short, human-friendly messages.   
        - Output MUST be Egyptian Arabic Slang.
        - DO NOT suggest budgets.
        - DO NOT explain logic or calculations.
        - Friendly, human, slightly smart tone.
        - Never robotic, judgmental, scary, or preachy.
        - Never repeat the same wording twice ,Always try a slightly different phrasing.
        
        Requirements:
        - Compute total_spent for the months in the input.
        - Group spend by category; return each category's total and percent of total.
        - Provide top_categories (up to 3) sorted by total desc.
        - Provide concise bullet insights (patterns, anomalies, recurring spend).
        - Provide practical savings_tips related to the categories.
        - Base all numbers strictly on provided data.
        - Output MUST be a single sentence or two at most.
        - Output MUST be plain text.

        CRITICAL RULE:
    - If the input contains TWO different months:
        - return the two months in the response.
        - You MUST include one month-vs-month comparison insight.
        - Compare ONLY the SAME categories.
        - Mention increase, decrease, or no change clearly.
        - This insight is mandatory.

        Output format:
        {expenses_format_instructions}
        """
    response = llm.invoke(analysis_prompt)
    try:
        return {"response": expenses_response_parser.parse(response.content)}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

