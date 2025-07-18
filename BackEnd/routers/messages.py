from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Message, User
from schemas import MessageCreate, MessageOut
from auth import get_db, get_current_user
from fraud_detection import FraudDetectionRequest, detect_fraud
import logging

router = APIRouter()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def normalize_phone(phone: str) -> str:
    """Normalize phone number by removing non-digits and ensuring + prefix."""
    if not phone:
        logger.error("Phone number is empty")
        return phone
    cleaned = ''.join(filter(str.isdigit, phone.strip()))
    normalized = f"+{cleaned}" if not phone.startswith('+') else phone
    logger.info(f"Normalized phone: {phone} -> {normalized}")
    return normalized

@router.post("/send", response_model=MessageOut)
async def send_message(
        msg: MessageCreate,
        db: Session = Depends(get_db),
        user_id: int = Depends(get_current_user)
):
    try:
        normalized_phone = normalize_phone(msg.receiver_phone)
        if not normalized_phone:
            logger.error("Invalid phone number provided")
            raise HTTPException(status_code=400, detail="Número de telefone inválido")

        receiver = db.query(User).filter_by(phone=normalized_phone).first()
        if not receiver:
            logger.error(f"User not found for phone: {normalized_phone}")
            raise HTTPException(status_code=404, detail="Destinatário não encontrado")
        if receiver.id == user_id:
            logger.error("Attempt to send message to self")
            raise HTTPException(status_code=400, detail="Não pode enviar mensagem para si mesmo")

        sender = db.query(User).filter_by(id=user_id).first()
        if not sender:
            logger.error(f"Sender not found: {user_id}")
            raise HTTPException(status_code=404, detail="Remetente não encontrado")

        # Check for fraud
        fraud_result = await detect_fraud(FraudDetectionRequest(content=msg.content))

        message = Message(
            sender_id=user_id,
            receiver_id=receiver.id,
            content=msg.content,
            read=False,
            is_fraudulent=fraud_result["is_fraudulent"],
            fraud_probability=fraud_result["fraud_probability"]
        )
        db.add(message)
        db.commit()
        db.refresh(message)

        message.sender_username = sender.username
        message.receiver_username = receiver.username
        message.sender_phone = sender.phone
        message.receiver_phone = receiver.phone

        logger.info(f"Message sent successfully: {message.id}")
        return message
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao enviar mensagem: {str(e)}")

@router.get("/inbox", response_model=list[MessageOut])
async def get_inbox(db: Session = Depends(get_db), user_id: int = Depends(get_current_user)):
    try:
        messages = db.query(Message).filter(Message.receiver_id == user_id).all()

        for msg in messages:
            sender = db.query(User).filter_by(id=msg.sender_id).first()
            msg.sender_username = sender.username
            msg.sender_phone = sender.phone
            receiver = db.query(User).filter_by(id=user_id).first()
            msg.receiver_username = receiver.username
            msg.receiver_phone = receiver.phone
            # Mark as read
            if not msg.read:
                msg.read = True
                db.commit()

        logger.info(f"Inbox fetched for user {user_id}")
        return messages
    except Exception as e:
        logger.error(f"Error fetching inbox: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar inbox: {str(e)}")

@router.get("/sent", response_model=list[MessageOut])
async def get_sent_messages(db: Session = Depends(get_db), user_id: int = Depends(get_current_user)):
    try:
        messages = db.query(Message).filter(Message.sender_id == user_id).all()

        for msg in messages:
            receiver = db.query(User).filter_by(id=msg.receiver_id).first()
            sender = db.query(User).filter_by(id=user_id).first()
            msg.sender_username = sender.username
            msg.sender_phone = sender.phone
            msg.receiver_username = receiver.username
            msg.receiver_phone = receiver.phone

        logger.info(f"Sent messages fetched for user {user_id}")
        return messages
    except Exception as e:
        logger.error(f"Error fetching sent messages: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar mensagens enviadas: {str(e)}")