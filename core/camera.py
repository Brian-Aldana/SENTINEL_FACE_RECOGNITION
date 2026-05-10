import cv2
import platform
from utils.logger import log


def list_cameras(max_index: int = 10) -> list[dict]:
    """
    Prueba índices 0..max_index-1 y retorna los que OpenCV puede abrir.
    Cada entrada: {"index": int, "label": str, "backend": int}
    """
    available = []
    system    = platform.system()

    for i in range(max_index):
        if system == "Linux":
            cap = cv2.VideoCapture(i, cv2.CAP_V4L2)
        else:
            cap = cv2.VideoCapture(i)

        if cap.isOpened():
            ok, _ = cap.read()
            if ok:
                label = f"Cámara {i}"
                if i == 0:
                    label += " (integrada)"
                else:
                    label += " (externa/USB)"
                available.append({
                    "index":   i,
                    "label":   label,
                    "backend": cv2.CAP_V4L2 if system == "Linux" else cv2.CAP_ANY,
                })
            cap.release()

    return available


def open_camera(index: int, width: int, height: int) -> cv2.VideoCapture:
    system = platform.system()
    if system == "Linux":
        cap = cv2.VideoCapture(index, cv2.CAP_V4L2)
    else:
        cap = cv2.VideoCapture(index)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    cap.set(cv2.CAP_PROP_BUFFERSIZE,   2)

    if not cap.isOpened():
        raise RuntimeError(f"No se pudo abrir cámara {index}")

    return cap


def encode_frame(frame, quality: int = 85) -> bytes:
    _, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, quality])
    return buf.tobytes()


_cascade = None

def detect_faces(frame) -> tuple[bool, list]:
    global _cascade
    if _cascade is None:
        _cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
    
    gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray  = cv2.equalizeHist(gray)
    faces = _cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(70, 70),
        flags=cv2.CASCADE_SCALE_IMAGE,
    )
    return len(faces) > 0, faces if len(faces) > 0 else []
