import os

from dotenv import load_dotenv

load_dotenv()

KEY = os.getenv(key="ACCESS_KEY")
ANKI_URL = f"http://{os.getenv(key='SERVER_IP')}:{os.getenv(key='SERVER_PORT')}"
OPENAI_MODEL = os.getenv(key="OPENAI_MODEL")
OPENAI_API_KEY = os.getenv(key="OPENAI_API_KEY")
