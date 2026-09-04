from sqlalchemy.orm import declarative_base
from sqlalchemy import DateTime
from sqlalchemy import Column, Integer, String
from datetime import datetime, timezone

# Base class used by SQLAlchemy to define database models
Base = declarative_base()

# User model represents a user stored in the database
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True) # Unique identifier for each user
    provider_id = Column(String) # Identifier for the authentication provider
    email = Column(String, unique=True) # User's email address
    name = Column(String) # User's name

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc)) # Timestamp indicating when the user was created
    last_login = Column(DateTime, default=lambda: datetime.now(timezone.utc)) # Timestamp indicating when the user last logged in