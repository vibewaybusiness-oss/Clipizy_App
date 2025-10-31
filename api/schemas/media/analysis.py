from typing import Any, Dict, Optional

from pydantic import BaseModel


class AnalysisResponse(BaseModel):
    track_id: Optional[str] = None
    video_id: Optional[str] = None
    image_id: Optional[str] = None
    analysis: Dict[str, Any]
    description: Optional[str] = None
