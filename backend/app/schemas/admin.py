from pydantic import BaseModel


class SystemStats(BaseModel):
    users: int
    sessions: int
    messages: int
    active_memories: int
    deleted_memories: int
    evaluation_runs: int
    vector_store_available: bool

