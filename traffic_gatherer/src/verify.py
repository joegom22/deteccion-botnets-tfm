import os
import dotenv
from fastapi import Header, HTTPException

dotenv.load_dotenv()

AUTORIZED_TOKEN = os.getenv("GATHERING_REQUEST_TOKEN")

def verify_token(token):
    """
    Verify the provided token against a predefined secret.
    
    Args:
        token (str): The token to verify.
        
    Returns:
        bool: True if the token is valid, False otherwise.
    """    
    if not isinstance(token, str):
        raise ValueError("Token must be a string")
    
    return token == AUTORIZED_TOKEN

def token_verification_dependency(x_token: str = Header(...)):
    """
    FastAPI dependency for token validation via HTTP header.
    """
    if not verify_token(x_token):
        raise HTTPException(status_code=401, detail="Invalid or missing token")