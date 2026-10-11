from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import EventSession
from ..schemas import SessionResponse

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


@router.get("", response_model=list[SessionResponse])
def list_sessions(db: Session = Depends(get_db)):
    return db.scalars(select(EventSession).order_by(EventSession.starts_at)).all()
