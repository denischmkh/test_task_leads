from fastapi import FastAPI

from app.auth_service.jwt import create_access_token
from app.auth_service.schema import TokenData, CreateTokenSchema

app = FastAPI()


@app.post("/token", response_model=TokenData)
async def generate_token(data: CreateTokenSchema):
    """Generate new token with affiliate_id"""
    token = create_access_token(payload_data=data)
    return TokenData(
        access_token=token,
        token_type="bearer",
    )