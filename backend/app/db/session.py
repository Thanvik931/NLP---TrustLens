"""
SQLAlchemy async session factory.
Reads DATABASE_URL from environment (set in .env or docker-compose).
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,        # reconnect on stale connections
    pool_size=10,
    max_overflow=20,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db():
    """FastAPI dependency — yields DB session, closes on exit."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
