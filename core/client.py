import requests
from config import API_URL, REQUEST_TIMEOUT
from utils.logger import log


def recognize(frame_bytes: list[bytes], cam_id: int) -> dict:
    """
    Envía N frames al endpoint POST /api/recognize.
    Retorna el JSON de respuesta o un dict de error.
    """
    files = {
        f"frame_{i:03d}": (f"frame_{i:03d}.jpg", b, "image/jpeg")
        for i, b in enumerate(frame_bytes)
    }
    try:
        r = requests.post(
            f"{API_URL}/recognize",
            files=files,
            timeout=REQUEST_TIMEOUT,
        )
        r.raise_for_status()
        return r.json()
    except requests.exceptions.Timeout:
        log("ERR", "Timeout - el backend tardó demasiado", cam_id)
        return {"access": "ERROR", "liveness": "UNKNOWN", "person": "Timeout", "confidence": 0.0}
    except requests.exceptions.ConnectionError:
        log("ERR", "Sin conexión al backend", cam_id)
        return {"access": "ERROR", "liveness": "UNKNOWN", "person": "Sin conexión", "confidence": 0.0}
    except requests.exceptions.HTTPError as e:
        log("ERR", f"HTTP {e.response.status_code}: {e.response.text[:80]}", cam_id)
        return {"access": "ERROR", "liveness": "UNKNOWN", "person": f"HTTP {e.response.status_code}", "confidence": 0.0}
    except Exception as e:
        log("ERR", str(e)[:80], cam_id)
        return {"access": "ERROR", "liveness": "UNKNOWN", "person": "Error", "confidence": 0.0}
