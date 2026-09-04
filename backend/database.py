from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Create SQLite database
engine = create_engine('sqlite:///users.db',
                       connect_args={"check_same_thread": False})

# Create database sessions (queries and transactions)
SessionLocal = sessionmaker(bind=engine)