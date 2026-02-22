from pydantic import BaseModel

class SymptomRequest(BaseModel):
    symptoms: str