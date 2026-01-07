from langchain.memory import ConversationBufferMemory

class MemoryService:
    def __init__(self):
        self.sessions = {}

    def get(self, session_id: str):
        if session_id not in self.sessions:
            self.sessions[session_id] = ConversationBufferMemory(
                memory_key="history",
                return_messages=False
            )
        return self.sessions[session_id]

memory_service = MemoryService()
