import os
from dotenv import load_dotenv

load_dotenv()

API_URL              = os.getenv("API_URL",  "https://sentinelfacebackend-production.up.railway.app/api")
N_FRAMES             = int(os.getenv("N_FRAMES",             "5"))
COOLDOWN             = float(os.getenv("COOLDOWN",           "4.0"))
FACE_STABLE_THRESHOLD= int(os.getenv("FACE_STABLE_THRESHOLD","8"))
CAP_WIDTH            = int(os.getenv("CAP_WIDTH",            "640"))
CAP_HEIGHT           = int(os.getenv("CAP_HEIGHT",           "480"))
JPEG_QUALITY         = int(os.getenv("JPEG_QUALITY",         "85"))
REQUEST_TIMEOUT      = int(os.getenv("REQUEST_TIMEOUT",      "20"))
