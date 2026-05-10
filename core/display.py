import cv2
from datetime import datetime

STATUS_COLORS = {
    "GRANTED":  (40,  200,  80),
    "DENIED":   (50,   50, 220),
    "SPOOFING": (0,    80, 220),
    "ERROR":    (100, 100, 100),
    "WAITING":  (160, 160, 160),
}

FONT       = cv2.FONT_HERSHEY_SIMPLEX
FONT_BOLD  = cv2.FONT_HERSHEY_DUPLEX


def draw_frame(frame, result: dict, faces, cam_label: str, collecting: bool, collect_progress: float):
    """
    Dibuja el overlay de resultado sobre el frame.
    - result: dict con access, liveness, person, confidence
    - faces: lista de (x,y,w,h) de las caras detectadas
    - collecting: True mientras se capturan frames
    - collect_progress: 0.0-1.0 barra de progreso de captura
    """
    h, w = frame.shape[:2]

    access   = result.get("access",   "WAITING")
    liveness = result.get("liveness", "")
    person   = result.get("person",   "")
    conf     = result.get("confidence", 0.0)

    if liveness == "SPOOFING":
        access = "SPOOFING"

    color = STATUS_COLORS.get(access, STATUS_COLORS["WAITING"])

    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, 56), (10, 10, 20), -1)
    cv2.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)

    status_lbl = access
    cv2.putText(frame, status_lbl, (14, 38), FONT_BOLD, 1.0, color, 2, cv2.LINE_AA)

    if person:
        detail = f"{person}  {conf:.0%}" if conf > 0 else person
        cv2.putText(frame, detail, (180, 38), FONT, 0.7, (230, 230, 230), 1, cv2.LINE_AA)

    ts = datetime.now().strftime("%H:%M:%S")
    cv2.putText(frame, ts, (w - 88, 38), FONT, 0.55, (140, 140, 140), 1, cv2.LINE_AA)

    cv2.putText(frame, cam_label, (14, h - 12), FONT, 0.45, (120, 120, 120), 1, cv2.LINE_AA)

    for (x, y, fw, fh) in faces:
        cv2.rectangle(frame, (x, y), (x + fw, y + fh), color, 2)
        cv2.rectangle(frame, (x, y - 22), (x + fw, y), color, -1)
        cv2.putText(frame, "Detectado", (x + 4, y - 6), FONT, 0.45, (15, 15, 15), 1, cv2.LINE_AA)

    if collecting:
        bar_w = int(collect_progress * (w - 4))
        cv2.rectangle(frame, (2, h - 6), (2 + bar_w, h - 2), (0, 200, 100), -1)
        cv2.putText(frame, "Procesando...", (14, h - 14), FONT, 0.45, (0, 200, 100), 1, cv2.LINE_AA)

    cv2.rectangle(frame, (0, 0), (w - 1, h - 1), color, 2)

    return frame
