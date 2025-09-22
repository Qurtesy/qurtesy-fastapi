import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Fetch database URL from environment
db_path = os.getenv("SQLITE_DATABASE_FILE_PATH")
if not db_path:
    raise ValueError("SQLITE_DATABASE_FILE_PATH environment variable is not set")
