import jwt
import os
from app.models.users import UserResponse
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("JWT_SECRET_KEY")
algorithm_type = os.getenv("ALGORITHM")

def create_access_token(user: UserResponse):
    data = {
        "sub":str(user.id),
    }

    token = jwt.encode(
        payload=data,
        key=key,
        algorithm=algorithm_type
    )

    return token

