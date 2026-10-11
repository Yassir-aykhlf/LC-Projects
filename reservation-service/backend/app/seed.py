from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from .db import DEFAULT_DATABASE_URL, assert_not_production, create_database_engine
from .models import EventSession, User


def seed(db: Session) -> None:
    """Insert the demo users and sessions after migrations have completed."""
    users = [User(id=1, name="Ada"), User(id=2, name="Lin"), User(id=3, name="Sam")]
    existing_user_ids = set(
        db.scalars(select(User.id).where(User.id.in_([1, 2, 3])))
    )
    db.add_all(user for user in users if user.id not in existing_user_ids)

    start = datetime.now(UTC).replace(microsecond=0) + timedelta(days=7)
    sessions = [
        EventSession(
            id=1,
            title="Morning Yoga Flow",
            starts_at=start,
            capacity=3,
            available_slots=3,
        ),
        EventSession(
            id=2,
            title="Pottery Wheel One-on-One",
            starts_at=start + timedelta(days=1),
            capacity=1,
            available_slots=1,
        ),
        EventSession(
            id=3,
            title="Hand-Drip Coffee Tasting",
            starts_at=start + timedelta(days=2),
            capacity=2,
            available_slots=2,
        ),
    ]
    existing_session_ids = set(
        db.scalars(select(EventSession.id).where(EventSession.id.in_([1, 2, 3])))
    )
    db.add_all(session for session in sessions if session.id not in existing_session_ids)
    db.commit()


if __name__ == "__main__":
    assert_not_production(
        DEFAULT_DATABASE_URL,
        operation="demo seeding",
        allow_override=False,
    )
    engine = create_database_engine(DEFAULT_DATABASE_URL)
    with sessionmaker(bind=engine, expire_on_commit=False)() as session:
        seed(session)
