import os
from dotenv import load_dotenv

load_dotenv()

API_URL              = os.getenv("API_URL") or "https://sentinelfacebackend-production.up.railway.app/api"
N_FRAMES             = int(os.getenv("N_FRAMES") or "90")
COOLDOWN             = float(os.getenv("COOLDOWN") or "4.0")
FACE_STABLE_THRESHOLD= int(os.getenv("FACE_STABLE_THRESHOLD") or "8")
CAP_WIDTH            = int(os.getenv("CAP_WIDTH") or "640")
CAP_HEIGHT           = int(os.getenv("CAP_HEIGHT") or "480")
JPEG_QUALITY         = int(os.getenv("JPEG_QUALITY") or "85")
REQUEST_TIMEOUT      = int(os.getenv("REQUEST_TIMEOUT") or "20")
