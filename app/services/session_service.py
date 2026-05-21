import redis
import json
import uuid
from app.config import Settings

class SessionService:
    def __init__(self):
        try:
            self.redis = redis.Redis(
                host=Settings.REDIS_HOST,
                port=Settings.REDIS_PORT,
                password=Settings.REDIS_PASSWORD,
                decode_responses=True
            )
            self.redis.ping()
            print("Redis connected successfully!")
        except Exception as e:
            print(f"Error initializing Redis: {e}")
            raise
        self.session_ttl = 60*60*24

    def create_session(self) -> str:
        session_id = str(uuid.uuid4())
        self.redis.setex(
            f"session:{session_id}",
            self.session_ttl,
            json.dumps([])
        )
        return session_id
    
    def get_history(self, session_id: str) -> list:
        data = self.redis.get(f"session:{session_id}")
        if data is None:
            return []
        return json.loads(data)
    
    def add_messages(self, session_id: str, question: str, answer: str):
        history = self.get_history(session_id)
        history.append({"role": "human", "content": question})
        history.append({"role": "ai", "content": answer})
        self.redis.setex(
            f"session:{session_id}",
            self.session_ttl,
            json.dumps(history)
        )

    def delete_session(self, session_id: str):
        delete = self.redis.delete(f"session:{session_id}")
        if delete == 0:
            return False
        return True