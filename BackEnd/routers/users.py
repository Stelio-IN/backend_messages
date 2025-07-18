from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from models import User
from schemas import UserCreate, UserLogin, Token
from utils.security import hash_password, verify_password, create_access_token
from auth import get_db, get_current_user
import logging

router = APIRouter()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.post("/register")
async def register(user: UserCreate, db: Session = Depends(get_db)):
    try:
        if db.query(User).filter_by(username=user.username).first():
            logger.error(f"Username already in use: {user.username}")
            raise HTTPException(status_code=400, detail="Username já em uso")
        if db.query(User).filter_by(phone=user.phone).first():
            logger.error(f"Phone number already registered: {user.phone}")
            raise HTTPException(status_code=400, detail="Número de celular já registrado")

        hashed = hash_password(user.password)
        db_user = User(
            username=user.username,
            phone=user.phone,
            password=hashed
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        logger.info(f"User registered successfully: {user.username}")
        return {"msg": "Usuário registrado com sucesso"}
    except Exception as e:
        logger.error(f"Error registering user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao registrar usuário: {str(e)}")

@router.post("/login", response_model=Token)
async def login(data: UserLogin, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter_by(phone=data.phone).first()
        if not user or not verify_password(data.password, user.password):
            logger.error(f"Invalid credentials for phone: {data.phone}")
            raise HTTPException(status_code=401, detail="Credenciais inválidas")

        token = create_access_token({"user_id": user.id, "sub": user.username})
        logger.info(f"User logged in successfully: {user.username}, token: {token[:10]}...")
        return {
            "access_token": token,
            "token_type": "bearer",
            "user_id": user.id,
            "username": user.username
        }
    except Exception as e:
        logger.error(f"Error logging in: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao fazer login: {str(e)}")

@router.get("/find")
async def find_user_by_contact(
        contact: str = Query(..., description="Número de telefone do usuário"),
        db: Session = Depends(get_db)
):
    try:
        user = db.query(User).filter(User.phone == contact).first()
        if not user:
            logger.error(f"User not found for contact: {contact}")
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        logger.info(f"User found: {user.username}")
        return {
            "id": user.id,
            "username": user.username,
            "phone": user.phone
        }
    except Exception as e:
        logger.error(f"Error finding user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar usuário: {str(e)}")

@router.get("/me")
async def get_current_user_profile(
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            logger.error(f"Current user not found: {user_id}")
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        logger.info(f"Profile fetched for user: {user.username}")
        return {
            "id": user.id,
            "username": user.username,
            "phone": user.phone
        }
    except Exception as e:
        logger.error(f"Error fetching user profile: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar perfil: {str(e)}")