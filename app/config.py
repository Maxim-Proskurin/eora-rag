import os

from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

class Settings:
    open_api_key: str
    chroma_persist_dir: str
    debug: bool

    def __init__(self):
        open_api_key = os.getenv("OPEN_API_KEY")
        if open_api_key is None:
            raise ValueError("OPEN_API_KEY is not set in environment or .env file")
        self.open_api_key = open_api_key
        self.chroma_persist_dir = os.getenv("CHROMA_PERSIST_DIR", "./chroma")
        self.debug = os.getenv("DEBUG", "False").lower() == "true"

settings = Settings()