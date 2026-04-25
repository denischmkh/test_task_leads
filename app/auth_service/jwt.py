from datetime import timedelta, datetime, timezone

from jwt import InvalidTokenError

from .schema import CreateTokenSchema
import uuid
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette import status
from app.config import settings

oauth2_scheme = HTTPBearer()


def create_access_token(payload_data: CreateTokenSchema):
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    affiliate_id_str = str(payload_data.affiliate_id)
    to_encode = {
        "affiliate_id": affiliate_id_str,
        "exp": expire
    }
    encoded_jwt = jwt.encode(
        payload=to_encode,
        key=settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt




async def get_current_affiliate_id(
    auth: HTTPAuthorizationCredentials = Depends(oauth2_scheme)
) -> uuid.UUID:
    token = auth.credentials

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )

        affiliate_id: str = payload.get("affiliate_id")

        if not affiliate_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token payload missing affiliate_id"
            )

        return uuid.UUID(affiliate_id)

    except (InvalidTokenError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )