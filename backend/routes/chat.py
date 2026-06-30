from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from database import get_db
from models import ChatMessage
from utils.assistant import AIAssistant

router = APIRouter(prefix="/api")

from pydantic import BaseModel
from typing import Optional, Dict, Any

class ChatRequest(BaseModel):
    question: str
    session_id: Optional[str] = "default"
    selected_location: Optional[Dict[str, Any]] = None

@router.post("/chat")
async def chat_assistant(
    req: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    Interfaces with the UHI Climatology AI Assistant to respond to environmental queries.
    Stores messages in history for persistent chat logs.
    """
    # Create Assistant instance linked to active DB session
    assistant = AIAssistant(db_session=db)
    
    # Save user message
    user_msg = ChatMessage(session_id=req.session_id, role="user", content=req.question)
    db.add(user_msg)
    db.commit()
    
    # Get response with selected location context
    answer = assistant.answer_question(req.question, session_id=req.session_id, selected_location=req.selected_location)
    
    # Save assistant message
    assistant_msg = ChatMessage(session_id=req.session_id, role="assistant", content=answer)
    db.add(assistant_msg)
    db.commit()
    
    return {
        "question": req.question,
        "answer": answer,
        "session_id": req.session_id
    }

@router.get("/chat/history")
async def get_chat_history(session_id: str = "default", db: Session = Depends(get_db)):
    """
    Retrieves conversational logs for the active assistant session.
    """
    msgs = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).order_by(ChatMessage.timestamp.asc()).all()
    return [{"role": m.role, "content": m.content, "timestamp": m.timestamp.isoformat()} for m in msgs]

@router.delete("/chat/history")
async def clear_chat_history(session_id: str = "default", db: Session = Depends(get_db)):
    """
    Clears all chat logs.
    """
    db.query(ChatMessage).filter(ChatMessage.session_id == session_id).delete()
    db.commit()
    return {"message": "Chat history cleared successfully."}
