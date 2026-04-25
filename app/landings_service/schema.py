from pydantic import BaseModel, Field, field_validator
import uuid
import re


class LeadCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    phone: str
    country: str = Field(..., min_length=2, max_length=2)
    offer_id: uuid.UUID
    affiliate_id: uuid.UUID

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not re.match(r"^\+?1?\d{9,15}$", v):
            raise ValueError("Invalid phone format")
        return v

    @field_validator("country")
    @classmethod
    def validate_country(cls, v: str) -> str:
        v = v.upper()
        if not re.match(r"^[A-Z]{2}$", v):
            raise ValueError("Invalid ISO country code")
        return v