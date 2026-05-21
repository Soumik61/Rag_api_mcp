import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

print("REDIS_HOST:", os.getenv("REDIS_HOST"))  # ← debug ke liye
print("REDIS_PORT:", os.getenv("REDIS_PORT"))  # ← debug ke liye
print("REDIS_PASSWORD:", os.getenv("REDIS_PASSWORD"))  # ← debug ke liye



class Settings:
    APP_NAME: str = "RAG API V4.0 - Production + MCP"
    GOOGLE_API_KEY: str | None = os.getenv("GOOGLE_API_KEY")
    CHROMA_API_KEY: str | None = os.getenv("CHROMA_API_KEY")
    CHROMA_TENANT: str | None = os.getenv("CHROMA_TENANT")
    CHROMA_DATABASE: str | None = os.getenv("CHROMA_DATABASE")
    CHROMA_COLLECTION_NAME: str = "rag_collection"
    REDIS_HOST: str = os.getenv("REDIS_HOST")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT"))
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD")
