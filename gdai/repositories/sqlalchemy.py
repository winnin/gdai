"""SQLAlchemy base models and configuration.

DEPRECATED: The module-level engine and SessionLocal are deprecated.
Use DatabaseManager.get_engine() and DatabaseManager.create_session() instead.
"""

from sqlalchemy.orm import declarative_base

# Base declarative model for all SQLAlchemy models
Base = declarative_base()
