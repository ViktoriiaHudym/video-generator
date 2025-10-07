import os

from dotenv import load_dotenv

from app.logger import get_logger

logger = get_logger(name='main_logger')

load_dotenv()

GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
