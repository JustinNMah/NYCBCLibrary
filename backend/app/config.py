from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_PATH = os.getenv("DATABASE_PATH", "library.db")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"