from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import google.generativeai as genai
from app.core.config import settings
from typing import List

router = APIRouter(prefix="/api/chat", tags=["chat"])

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = []

# Initialize Gemini
if settings.gemini_api_key:
    genai.configure(api_key=settings.gemini_api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
else:
    model = None

system_prompt = """
Kamu adalah asisten pintar bernama 'HydroBot' di aplikasi HydroCare.
Tugas utamamu adalah menjawab pertanyaan seputar hidrasi, air minum, kesehatan ginjal, dan efek cuaca terhadap kebutuhan air.
Berikan jawaban yang singkat, ramah, menggunakan bahasa Indonesia yang santai tapi informatif, dan gunakan emoji.
Jika pengguna bertanya di luar topik kesehatan dan hidrasi, tolak dengan sopan dan arahkan kembali ke topik hidrasi.
"""

@router.post("/")
async def chat_with_ai(req: ChatRequest):
    if not model:
        # Fallback rule-based if no API key
        return {"success": True, "reply": "Maaf, fitur AI sedang tidak tersedia karena API Key belum dikonfigurasi. 🤖💧"}
    
    try:
        # Convert history format
        formatted_history = []
        for msg in req.history:
            role = "user" if msg.role == "user" else "model"
            formatted_history.append({"role": role, "parts": [msg.content]})

        # Add system prompt context if it's a new conversation or we prepend it to the message
        # A simple way to enforce system prompt in single turn is to prepend it to the current message
        # But since we have history, we can start a chat session
        chat_session = model.start_chat(history=formatted_history)
        
        full_prompt = f"System Instruction: {system_prompt}\n\nUser Message: {req.message}"
        
        response = chat_session.send_message(full_prompt)
        
        return {"success": True, "reply": response.text}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
