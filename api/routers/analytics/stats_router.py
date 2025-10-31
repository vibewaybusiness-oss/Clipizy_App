from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.services.database import get_db
from api.models import User, Stats
from api.schemas import StatsRead
from api.services.auth import get_current_user

router = APIRouter(prefix="/api/stats", tags=["Stats"])


@router.get("/{project_id}", response_model=list[StatsRead])
def get_project_stats(project_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user_id = str(current_user.id)
    return db.query(Stats).filter_by(project_id=project_id, user_id=user_id).all()
