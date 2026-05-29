from locust import HttpUser, task, between

class RagAPIUser(HttpUser):
    wait_time = between(1, 3)  # har request ke beech 1-3 sec wait

    @task(3)                   # 3x zyada hit hoga
    def ask_question(self):
        self.client.post("/ask", json={
            "question": "what are my technical skills?"
        })

    @task(2)
    def health_check(self):
        self.client.get("/health")

    @task(1)                   # 1x hit hoga
    def start_session(self):
        response = self.client.post("/chat/start")
        if response.status_code == 200:
            session_id = response.json().get("session_id")
            if session_id:
                self.client.post(f"/chat/{session_id}", json={
                    "question": "what is my experience?"
                })