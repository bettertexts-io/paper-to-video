import logging
import os
from dotenv import load_dotenv
import poe


logging.basicConfig(level=logging.INFO)

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
POE_TOKEN = os.getenv("POE_TOKEN")

logging.info(f"OPENAI_API_KEY: {OPENAI_API_KEY}")
