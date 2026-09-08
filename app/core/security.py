import jwt
import os
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("JWT_SECRET_KEY")
algorithm_type = os.getenv("ALGORITHM")

data = {
    "payload":"",
    "token_type":"bearer"
}

token = jwt.encode(
    payload=data,
    key=key,
    algorithm=algorithm_type
)

payload = jwt.decode(
    token,
    key,
    algorithms=algorithm_type,
)