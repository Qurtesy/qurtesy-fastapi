import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Fetch database URL from environment
db_url = os.getenv("DATABASE_URL")
if not db_url:
    raise ValueError("DATABASE_URL environment variable is not set")

# Fetch dynamodb URL from environment
dynamodb_host = os.getenv("DYNAMODB_HOST")
if not dynamodb_host:
    raise ValueError("DYNAMODB_HOST environment variable is not set")

dynamodb_region = os.getenv("DYNAMODB_REGION")
if not dynamodb_region:
    raise ValueError("DYNAMODB_REGION environment variable is not set")
