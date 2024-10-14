from pydantic import BaseModel

class BadmintonCourtStatus(BaseModel):
    start_time: str
    end_time: str
    available_count: int
