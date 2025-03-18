import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Fetch database URL from environment
db_url = os.getenv("DATABASE_URL")
if not db_url:
    raise ValueError("DATABASE_URL environment variable is not set")