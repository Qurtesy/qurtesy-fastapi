from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from config import db_url

# Create the SQLAlchemy engine
engine = create_engine(
    db_url, 
    connect_args={"options": "-csearch_path=finance"},
    echo=False  # Set to True for SQL debugging
)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Initialize database schema
def init_db():
    """Initialize the database schema"""
    from models import Base
    
    # Create the finance schema if it doesn't exist
    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS finance"))
        conn.commit()
    
    # Create all tables
    Base.metadata.create_all(bind=engine)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
