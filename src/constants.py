import logging
import os
from dotenv import load_dotenv
import poe

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
POE_TOKEN = os.getenv("POE_TOKEN")

logging.info(f"OPENAI_API_KEY: {OPENAI_API_KEY}")
