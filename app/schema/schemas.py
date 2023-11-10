from pydantic import BaseModel


class LikedPodcastRequest(BaseModel):
    podcast_id: str


from typing import List, Optional


class LikedPodcastResponse(BaseModel):
    _user_id: Optional[str]
    podcast_id: str
