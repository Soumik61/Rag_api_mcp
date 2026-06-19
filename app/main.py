from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi_mcp import FastApiMCP
from httpcore import request
from app.config import Settings
from app.models import QueryRequest, ChatRequest, SessionChatRequest
from app.services.rag_service import RagService
from app.services.session_service import SessionService
from prometheus_fastapi_instrumentator import Instrumentator

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.rag_service = RagService()
    app.state.session_service = SessionService()
    yield
    app.state.rag_service = None
    app.state.session_service = None

app = FastAPI(title=Settings.APP_NAME, lifespan=lifespan)

Instrumentator().instrument(app).expose(app)

@app.get("/")
def root():
    return {
        "message": "RAG API is running",
        "docs_url": "/docs",
        "health_url": "/health",
        "ask_url": "/ask",
        "chat_url": "/chat",
        "mcp_url": "/mcp",
    }

@app.get("/health")
def health():
    try:
        return app.state.rag_service.health()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/ask")
def ask_question(request: QueryRequest):
    try:
        return app.state.rag_service.ask(request.question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/chat")
def chat_question(request: ChatRequest):
    try:
        return app.state.rag_service.chat(
            question=request.question,
            chat_history=request.chat_history,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.post("/chat/start")
def start_session():
    try:
        session_id = app.state.session_service.create_session()
        return {
            "session_id": session_id,
            "message": "Session started! Use this session_id for all future messages."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.post("/chat/{session_id}")
def chat_with_session(session_id: str, request: SessionChatRequest):
    try:
        session_service = app.state.session_service
        rag_service = app.state.rag_service
        history = session_service.get_history(session_id)
        if history is None:
            raise HTTPException(status_code=404, detail="Session not found")
        result = rag_service.chat(
            question=request.question,
            chat_history=history
        )
        session_service.add_messages(
            session_id=session_id,
            question=request.question,
            answer=result["answer"],
        )
        return {
            "result": result,
            "session_id": session_id,
        }   
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/chat/{session_id}/history")
def get_session_history(session_id: str):
    try:
        history = app.state.session_service.get_history(session_id)
        if history is None:
            raise HTTPException(status_code=404, detail="Session not found")
        return {
            "session_id": session_id,
            "history": history,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
    
@app.delete("/chat/{session_id}")
def end_session(session_id: str):
    try:
        deleted = app.state.session_service.delete_session(session_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Session not found")
        return {
            "session_id": session_id,
            "message": "Session ended and history deleted.",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

mcp =FastApiMCP(app)
mcp.mount()

