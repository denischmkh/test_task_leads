import uuid

from pydantic import BaseModel


class CreateTokenSchema(BaseModel):
    affiliate_id: uuid.UUID

class TokenData(BaseModel):
    access_token: str
    token_type: str