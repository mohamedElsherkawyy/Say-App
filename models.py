
from pydantic import BaseModel , Field
from typing import List, Union, Optional

class Category(BaseModel):
    food: Optional[str] = Field(default=None, description="The amount of money spent on food , drinks , coffee shops , restaurants , etc")
    transportation: Optional[str] = Field(default=None, description="The amount of money spent on transportation , taxi , bus , metro , etc")
    travel: Optional[str] = Field(default=None, description="The amount of money spent on travel , hotel , airbnb , etc")
    shopping: Optional[str] = Field(default=None, description="The amount of money spent on shopping , clothes , shoes , etc , not including food and drinks")
    fitness: Optional[str] = Field(default=None, description="The amount of money spent on fitness , gym , yoga , etc")
    entertainment: Optional[str] = Field(default=None, description="The amount of money spent on entertainment , movies , concerts , games , etc")
    healthCare: Optional[str] = Field(default=None, description="The amount of money spent on health care , doctor , hospital , insurance , pharmacy, etc")
    education: Optional[str] = Field(default=None, description="The amount of money spent on education , school , university , etc")
    carServices: Optional[str] = Field(default=None, description="The amount of money spent on car services , car repair , car maintenance , car cleaning , fuel, etc")
class STTResponse(BaseModel):
    category: list[Category]

class STTRequest(BaseModel):
    stt_text: str


class Transaction(BaseModel): 
    month: str
    amount: float
    category: str

class ExpensesAnalysisRequest(BaseModel):
    transactions: List[Transaction]

class CategorySummary(BaseModel):
    category: str
    total: float
    percent: float

class ExpensesAnalysisResponse(BaseModel):
    month: str  
    total_spent: float
    categories: List[CategorySummary]
    top_categories: List[CategorySummary]
    insights: List[str]
    savings_tips: List[str]