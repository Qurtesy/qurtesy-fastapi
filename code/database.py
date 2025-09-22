import json
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from config import db_path

# Create the SQLAlchemy engine
connect_args = {"check_same_thread": False}
engine = create_engine(f"sqlite:///{db_path}", connect_args=connect_args)

schema_path = 'schema.json'
init_db_path = 'initDb.sql'

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Initialize database schema
def init_db():
    print("""Initialize the database schema""")
    from models.base import Base
    # Create all tables
    Base.metadata.create_all(bind=engine)
    with engine.connect() as conn:
        try:
            with open(schema_path, 'r') as schema:
                common = None
                schemas = []
                for s in schema:
                    if s.name == 'common':
                        common = s
                    else:
                        schemas.append(s)
                initSql = ''
                for s in schemas:
                    fields = []
                    for f in common.fields:
                        fields.append(f"{f.name} {f.type} {'NOT NULL' if f.required else ''} ${f.attrs if f.attrs else ''}")
                    initSql += f"""
                        CREATE TABLE IF NOT EXISTS {s.name} (
                            {',\n'.join(fields)}
                        );
                    """
                print("Initializing Tables")
                print(initSql)
                conn.execute(initSql)
            with open(init_db_path, 'r') as file:
                print("Inserting Records")
                content = file.read()
                print(content)
                conn.execute(text(content))
        except Exception as e:
            print(f"Error occurred while initializing database: {e}")
        conn.commit()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
