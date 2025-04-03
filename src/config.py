import os

from dotenv import load_dotenv

load_dotenv()

KEY = os.getenv(key="ACCESS_KEY")
ANKI_URL = f"http://{os.getenv(key='SERVER_IP')}:{os.getenv(key='SERVER_PORT')}"
