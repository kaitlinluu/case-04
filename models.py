from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, validator
import hashlib

def sha256_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()

class SurveySubmission(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    age: int = Field(..., ge=13, le=120)
    consent: bool = Field(..., description="Must be true to accept")
    rating: int = Field(..., ge=1, le=5)
    comments: Optional[str] = Field(None, max_length=1000)
    user_agent: Optional[str] = None
    submission_id: Optional[str] = None
  

    @validator("comments")
    def _strip_comments(cls, v):
        return v.strip() if isinstance(v, str) else v

    @validator("consent")
    def _must_consent(cls, v):
        if v is not True:
            raise ValueError("consent must be true")
        return v
        
#Good example of inheritance
class StoredSurveyRecord(SurveySubmission):
    received_at: datetime
    ip: str

    @validator("email", pre=True)
    def _hash_email(cls, v):
        return sha256_hash(v)

    @validator("age", pre=True)
    def _hash_age(cls, v):
        return sha256_hash(str(v))

    @validator("submission_id", always=True, pre=True)
    def _generate_submission_id(cls, v, values):
        if v:  # frontend provided one
            return v
        email = values.get("email", "")
        timestamp = datetime.utcnow().strftime("%Y%m%d%H")
        return sha256_hash(email + timestamp)