# SENTINEL_FACE_RECOGNITION

Cliente de reconocimiento facial para el sistema Sentinel Face.  
Corre en PC Windows/Linux/macOS o Raspberry Pi. Detecta caras con la cámara disponible y envía los frames al backend en Railway.

## Requisitos

- Python 3.10 o superior
- OpenCV compatible con la cámara (USB o integrada)
- Raspberry Pi: Raspberry Pi OS Bullseye o Bookworm con cámara habilitada

## Instalación

```bash
git clone https://github.com/tu-usuario/SENTINEL_FACE_RECOGNITION.git
cd SENTINEL_FACE_RECOGNITION

uv venv

# Windows
.venv\Scripts\activate
# Linux / macOS / Raspberry Pi
source .venv/bin/activate

uv sync
```

## Configuración

```bash
cp .env.example .env
```

Edita `.env` y establece al menos `API_URL` con la URL de tu backend en Railway.

## Uso

```bash
python main.py
```

Al iniciar, se muestran las cámaras detectadas:

```
  Cámaras disponibles:

    [0] Cámara 0 (integrada)
    [1] Cámara 1 (externa/USB)

    [a] Usar todas (2 cámaras simultáneas)
    [q] Salir

  Selección:
```

Elige el número de cámara, `a` para usarlas todas en simultáneo, o `q` para salir.

### Teclas durante la sesión

| Tecla | Acción |
|---|---|
| `ESPACIO` | Forzar un reconocimiento inmediato si hay cara detectada |
| `Q` | Cerrar la sesión |

## Comportamiento

1. La cámara detecta caras localmente con Haar Cascade (sin costo de red).
2. Cuando una cara permanece estable por `FACE_STABLE_THRESHOLD` frames consecutivos, se capturan `N_FRAMES` frames y se envían a `POST /api/recognize`.
3. El resultado (GRANTED / DENIED / SPOOFING) se muestra en el overlay de la ventana.
4. El backend escribe el log y genera alertas automáticamente si corresponde.
5. La app móvil de administración refleja los eventos a través del polling.

## Variables de entorno

| Variable | Por defecto | Descripción |
|---|---|---|
| `API_URL` | URL Railway | URL base del backend sin slash final |
| `N_FRAMES` | `5` | Frames enviados por reconocimiento |
| `COOLDOWN` | `4.0` | Segundos entre reconocimientos por cámara |
| `FACE_STABLE_THRESHOLD` | `8` | Frames consecutivos con cara para disparar |
| `CAP_WIDTH` | `640` | Resolución horizontal de captura |
| `CAP_HEIGHT` | `480` | Resolución vertical de captura |
| `JPEG_QUALITY` | `85` | Calidad JPEG de los frames (0-100) |
| `REQUEST_TIMEOUT` | `20` | Timeout HTTP en segundos |

## Raspberry Pi — notas adicionales

En Raspberry Pi con cámara CSI (módulo oficial), habilitar la cámara:

```bash
sudo raspi-config
# Interface Options → Camera → Enable
```

Instalar dependencias del sistema si `opencv-python` falla:

```bash
sudo apt-get install -y python3-opencv libatlas-base-dev
```

Si la cámara CSI no aparece como `/dev/video0`, instalar el bridge V4L2:

```bash
sudo modprobe bcm2835-v4l2
# Para que persista entre reinicios:
echo "bcm2835-v4l2" | sudo tee -a /etc/modules
```

Para ejecutar automáticamente al arrancar el Raspberry Pi:

```bash
# Crear servicio systemd
sudo nano /etc/systemd/system/sentinel-cam.service
```

Contenido del servicio:

```ini
[Unit]
Description=Sentinel Face Recognition Client
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/SENTINEL_FACE_RECOGNITION
ExecStart=/home/pi/SENTINEL_FACE_RECOGNITION/.venv/bin/python main.py
Restart=on-failure
RestartSec=5
Environment=DISPLAY=:0

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable sentinel-cam
sudo systemctl start sentinel-cam
```
