from colorama import Fore, Style, init
from datetime import datetime

init(autoreset=True)

_TAGS = {
    "OK":   Fore.GREEN,
    "ERR":  Fore.RED,
    "WARN": Fore.YELLOW,
    "INFO": Fore.CYAN,
    "CAM":  Fore.MAGENTA,
}


def log(tag: str, msg: str, cam_id: int | None = None):
    color  = _TAGS.get(tag, "")
    ts     = datetime.now().strftime("%H:%M:%S")
    prefix = f"[CAM {cam_id}] " if cam_id is not None else ""
    print(f"  {Fore.WHITE}{ts}{Style.RESET_ALL}  {color}[{tag}]{Style.RESET_ALL}  {prefix}{msg}")
