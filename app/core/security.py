import os
from datetime import UTC, datetime, timedelta

import jwt

from app.models.users import UserResponse

key = os.getenv("JWT_SECRET_KEY")
token_algorithm = os.getenv("JWT_ALGORITHM")
expires_in = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
data = {
    "sub":str,
    "exp": expires_in
}

def create_access_token(user: UserResponse):
    to_encode = data.copy()
    expiration = datetime.now(UTC) + timedelta(minutes=expires_in)
    to_encode.update({
        "sub": str(user.id),
        "exp": expiration
    })

    token = jwt.encode(
        payload=to_encode,
        key=key,
        algorithm=token_algorithm
    )

    return token

def decode_access_token(user_token):
    payload = jwt.decode(user_token, key, algorithms=[token_algorithm])
    return payload