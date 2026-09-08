import jwt
import os
from app.models.users import UserResponse
from datetime import datetime, timedelta, timezone



key = os.getenv("JWT_SECRET_KEY")
token_algorithm = os.getenv("JWT_ALGORITHM")
expires_in = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES",30))

def create_access_token(user: UserResponse):
    expiration = datetime.now(timezone.utc) + timedelta(minutes=expires_in)

    data = {
        "sub":str(user.id),
        "exp": expiration
    }

    token = jwt.encode(
        payload=data,
        key=key,
        algorithm=token_algorithm
    )

    return token

