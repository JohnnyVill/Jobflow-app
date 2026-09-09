import jwt
import os
from app.models.users import UserResponse
from datetime import datetime, timedelta, timezone




key = os.getenv("JWT_SECRET_KEY")
token_algorithm = os.getenv("JWT_ALGORITHM")
expires_in = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES",30))
data = {
    "sub":int,
    "exp": expires_in
}

def create_access_token(user: UserResponse):
    to_encode = data.copy()
    expiration = datetime.now(timezone.utc) + timedelta(minutes=expires_in)
    to_encode.update({
        "sub": user.id,
        "exp": expiration
    })

    token = jwt.encode(
        payload=to_encode,
        key=key,
        algorithm=token_algorithm
    )

    return token

