from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import db_url

# Create the SQLAlchemy engine
engine = create_engine(db_url, connect_args={"options": "-csearch_path=qurtesy"})

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
