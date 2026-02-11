from fastapi.responses import JSONResponse
from langchain_groq import ChatGroq
from groq import Groq
from langchain_core.output_parsers import PydanticOutputParser 
from config import groq_api_key
from models import STTRequest, STTResponse, ExpensesAnalysisRequest, ExpensesAnalysisResponse
from ocr import process_image

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
        You are an Egyptian Arabic financial assistant for "احسبهالي", a voice-first personal finance app.

        === INPUT DATA ===
        {request.transactions}

        === YOUR TASK ===
        Analyze the transaction data and generate a structured financial summary.

        === ANALYSIS REQUIREMENTS ===

        1. MONTH IDENTIFICATION
        - Extract the month(s) from the transaction data
        - Output month name(s) in ENGLISH only
        - Format: "January" for single month, "January and February" for two months
        - Do NOT use Arabic for month names

        2. TOTAL SPENDING CALCULATION
        - Sum ALL expense transactions in the provided data
        - Double-check your calculation before outputting
        - Verify: total_spent = sum of all individual transaction amounts
        - Report total_spent as a precise number (integer or decimal)
        - CRITICAL: Ensure this number is mathematically correct

        3. CATEGORY BREAKDOWN
        - Group all transactions by category
        - For each category calculate:
            * Total amount spent (sum of all transactions in that category)
            * Percentage of overall spending (category_total / total_spent * 100)
        - Verify percentages add up to 100% (or very close due to rounding)
        - Sort categories by total amount (highest to lowest)

        4. TOP CATEGORIES
        - Extract the top 3 categories by spending amount
        - Return as ordered list with amounts and percentages
        - These should match the top 3 from your category breakdown

        5. MONTH-TO-MONTH COMPARISON (CONDITIONAL)
        - IF input contains exactly 2 different months:
            * Compare spending in IDENTICAL categories only
            * Calculate the difference (increase/decrease/unchanged)
            * Express as percentage change where meaningful
            * Include at least ONE comparison insight in your insights section
            * This comparison is MANDATORY when 2 months exist
        - IF input contains only 1 month:
            * Skip month-to-month comparison entirely

        6. INSIGHTS (2-4 bullet points)
        - Identify spending patterns (e.g., recurring payments, concentration in specific categories)
        - Flag anomalies (unusually high single transactions, unexpected category spikes)
        - Note frequency patterns (daily coffee, weekly groceries, etc.)
        - If 2 months provided: MUST include comparison between months
        - Keep factual and observation-based
        - Output in Egyptian Arabic (عامية مصرية)

        7. SAVINGS TIPS (2-3 practical suggestions)
        - Base recommendations on actual category data
        - Focus on highest-spending or most frequent categories
        - Make actionable and realistic
        - Avoid generic advice
        - Output in Egyptian Arabic (عامية مصرية)

        === LANGUAGE & TONE GUIDELINES ===

        LANGUAGE RULES:
        - month field: ENGLISH only (e.g., "January", "February and March")
        - insights field: Egyptian Arabic colloquial (عامية مصرية)
        - savings_tips field: Egyptian Arabic colloquial (عامية مصرية)

        TONE REQUIREMENTS:
        - Conversational and friendly (like talking to a friend)
        - Helpful and supportive
        - Clear and concise
        - Slightly witty when appropriate

        TONE PROHIBITIONS:
        - Robotic or formal language
        - Judgmental or condescending
        - Alarmist or scary phrasing
        - Preachy or moralistic
        - Repetitive wording (vary your phrasing)

        MESSAGE LENGTH:
        - Each insight/tip should be 1-2 sentences maximum
        - Be concise but complete
        - Prioritize clarity over brevity

        === CALCULATION VERIFICATION ===
        Before finalizing your response:
        1. Verify total_spent = sum of ALL transaction amounts
        2. Verify each category total = sum of transactions in that category
        3. Verify all category percentages add up to ~100%
        4. Verify top_categories matches the highest 3 from categories list

        === OUTPUT FORMAT ===
        {expenses_format_instructions}

        === CRITICAL RULES ===
        1. Month field MUST be in ENGLISH (never Arabic)
        2. Base ALL numbers strictly on provided transaction data
        3. VERIFY total_spent calculation is mathematically correct
        4. Do NOT invent or assume data points
        5. Do NOT suggest budget amounts
        6. Do NOT explain your calculation methodology
        7. Output plain text only (no markdown, no formatting)
        8. When 2 months exist, month comparison is NON-NEGOTIABLE
        9. Use Egyptian Arabic for insights and savings_tips ONLY
        """
    response = llm.invoke(analysis_prompt)
    try:
        return {"response": expenses_response_parser.parse(response.content)}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
    
def receipt(image_base64: str):
    """Analyze receipt via Groq vision API. Image sent as image_url, not in prompt."""
    client = Groq(api_key=groq_api_key)
    text = f"""Analyze this receipt (Egyptian Arabic/English). Return amounts per category, no currency. Use Total if both exist.
Format: {format_instructions}
Single list only."""
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

