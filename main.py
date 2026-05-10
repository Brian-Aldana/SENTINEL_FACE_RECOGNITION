import sys
import time
import threading
import cv2

import config
from core.camera  import list_cameras, open_camera, encode_frame, detect_faces
from core.client  import recognize
from core.display import draw_frame
from utils.logger import log


def camera_worker(cam_info: dict, stop_event: threading.Event):
    """
    Hilo independiente para una sola cámara.
    Detecta caras localmente y dispara reconocimientos contra el backend.
    """
    idx       = cam_info["index"]
    label     = cam_info["label"]
    win_title = f"Sentinel Face — {label}"

    log("CAM", f"Abriendo {label}...", idx)

    try:
        cap = open_camera(idx, config.CAP_WIDTH, config.CAP_HEIGHT)
    except RuntimeError as e:
        log("ERR", str(e), idx)
        return

    log("OK", f"{label} activa ({config.CAP_WIDTH}x{config.CAP_HEIGHT})", idx)

    last_result    = {"access": "WAITING", "liveness": "", "person": "Acércate a la cámara", "confidence": 0.0}
    last_faces     = []
    last_time      = 0.0
    face_stable    = 0
    collecting     = False
    collected      = []

    cv2.namedWindow(win_title, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(win_title, config.CAP_WIDTH, config.CAP_HEIGHT)

    while not stop_event.is_set():
        ok, frame = cap.read()
        if not ok:
            log("WARN", "Frame vacío, reintentando...", idx)
            time.sleep(0.1)
            continue

        frame      = cv2.flip(frame, 1)
        now        = time.time()
        face_found, faces = detect_faces(frame)

        if face_found:
            face_stable += 1
            last_faces   = faces
        else:
            face_stable = max(0, face_stable - 1)
            if face_stable == 0 and not collecting:
                last_faces = []

        auto_trigger  = face_stable >= config.FACE_STABLE_THRESHOLD and (now - last_time) > config.COOLDOWN
        key           = cv2.waitKey(1) & 0xFF
        space_trigger = key == 32 and face_found and (now - last_time) > 1.0

        if (auto_trigger or space_trigger) and not collecting:
            collecting  = True
            collected   = []
            face_stable = 0
            log("INFO", f"Capturando {config.N_FRAMES} frames...", idx)

        if collecting:
            collected.append(encode_frame(frame, config.JPEG_QUALITY))
            progress = len(collected) / config.N_FRAMES

            if len(collected) >= config.N_FRAMES:
                collecting  = False
                last_time   = now

                result      = recognize(collected, idx)
                last_result = result

                access   = result.get("access",   "?")
                liveness = result.get("liveness", "?")
                person   = result.get("person",   "?")
                conf     = result.get("confidence", 0.0)
                tag      = "OK" if access == "GRANTED" else "WARN" if liveness == "SPOOFING" else "INFO"
                log(tag, f"{access} | {liveness} | {person} ({conf:.0%})", idx)
        else:
            progress = 0.0

        display = draw_frame(
            frame.copy(),
            last_result,
            last_faces if face_found else [],
            label,
            collecting,
            progress,
        )

        cv2.imshow(win_title, display)

        if key == ord("q"):
            stop_event.set()
            break

    cap.release()
    cv2.destroyWindow(win_title)
    log("INFO", f"{label} cerrada.", idx)


def select_cameras(cameras: list[dict]) -> list[dict]:
    print("\n  Cámaras disponibles:\n")
    for cam in cameras:
        print(f"    [{cam['index']}] {cam['label']}")

    print(f"\n    [a] Usar todas ({len(cameras)} cámaras simultáneas)")
    print( "    [q] Salir\n")

    while True:
        choice = input("  Selección: ").strip().lower()

        if choice == "q":
            sys.exit(0)

        if choice == "a":
            return cameras

        try:
            idx = int(choice)
            match = [c for c in cameras if c["index"] == idx]
            if match:
                return match
            print("  Índice no válido. Intenta de nuevo.")
        except ValueError:
            print("  Entrada no reconocida. Escribe un número, 'a' o 'q'.")


def main():
    print("\n" + "═" * 52)
    print("  Sentinel Face — Cliente de reconocimiento facial")
    print("═" * 52)
    print(f"  Backend : {config.API_URL}")
    print(f"  Frames  : {config.N_FRAMES} por reconocimiento")
    print(f"  Cooldown: {config.COOLDOWN}s  |  Estabilidad: {config.FACE_STABLE_THRESHOLD} frames")
    print( "  Teclas  : ESPACIO = forzar reconocimiento  |  Q = salir")
    print("═" * 52 + "\n")

    log("INFO", "Detectando cámaras disponibles...")
    cameras = list_cameras(max_index=10)

    if not cameras:
        log("ERR", "No se encontró ninguna cámara. Conecta una y vuelve a intentarlo.")
        sys.exit(1)

    log("OK", f"{len(cameras)} cámara(s) encontrada(s).")

    selected = select_cameras(cameras)

    stop_event = threading.Event()
    threads    = []

    for cam in selected:
        t = threading.Thread(target=camera_worker, args=(cam, stop_event), daemon=True)
        t.start()
        threads.append(t)
        time.sleep(0.3)

    log("INFO", "Presiona Q en cualquier ventana para salir.\n")

    try:
        while not stop_event.is_set():
            time.sleep(0.25)
    except KeyboardInterrupt:
        log("INFO", "Interrupción recibida. Cerrando...")
        stop_event.set()

    for t in threads:
        t.join(timeout=3)

    cv2.destroyAllWindows()
    log("OK", "Sesión terminada.")


if __name__ == "__main__":
    main()
