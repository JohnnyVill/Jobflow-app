import jwt
import os
from app.models.users import UserResponse



key = os.getenv("JWT_SECRET_KEY")

def create_access_token(user: UserResponse):
    data = {
        "sub":str(user.id),
    }

    token = jwt.encode(
        payload=data,
        key=key,
        algorithm="HS256"
    )

    return token

