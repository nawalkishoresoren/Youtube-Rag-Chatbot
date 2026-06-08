from pydantic import BaseModel,Field

class InputRequest(BaseModel):
    url:str = Field(...,description="Complete ULR of the video")