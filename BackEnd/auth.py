from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError, decode
from sqlalchemy.orm import Session
from database import SessionLocal
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        if not token:
            logger.error("No token provided in Authorization header")
            raise HTTPException(status_code=401, detail="Token não fornecido")
        logger.info(f"Decoding token: {token[:10]}...")  # Log partial token for debugging
        payload = decode(token, "secret_key", algorithms=["HS256"])
        user_id = payload.get("user_id")
        if user_id is None:
            logger.error("Token missing user_id")
            raise HTTPException(status_code=401, detail="Token inválido: user_id ausente")
        logger.info(f"Token valid, user_id: {user_id}")
        return user_id
    except PyJWTError as e:
        logger.error(f"JWT decode error: {str(e)}")
        raise HTTPException(status_code=401, detail=f"Erro ao validar token: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in get_current_user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")