# config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file as early as possible
load_dotenv()

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable not set. Please set it in your .env file.")
MODEL = "gpt-4o"
MAX_COST = 100.0  # Maximum cost in USD

# Folder Configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEASE_FOLDER = os.path.join(BASE_DIR, "data", "leases")
PROMPT_FOLDER = os.path.join(BASE_DIR, "data", "prompts")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "output")
EXCEPTIONS_FOLDER = os.path.join(BASE_DIR, "exceptions")

# Cost Estimation (approximate)
# These values may need adjustment based on actual pricing
TOKEN_COSTS = {
    "gpt-4o": {
        "input": 0.0000025,  # $2.50 per million tokens
        "output": 0.00003,   # $30 per million tokens
    },
    "o3-mini": {
        "input": 0.0000011,  # $1.10 per million tokens
        "output": 0.0000044  # $4.40 per million tokens
    }
}
