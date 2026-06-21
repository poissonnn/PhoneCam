"""
MADE BY CLAUDE
Lib maison pour piloter et lire la souris sous Wayland/Sway.
 
- Pilotage move : via swaymsg seat cursor set (coordonnées globales fiables)
- Clics / press / release / drag / scroll : via ydotool
- Lecture de la position réelle du curseur : via wl-find-cursor
 
Pré-requis :
- ydotool installé (pacman -S ydotool) + ydotoold lancé en arrière-plan
- utilisateur dans le groupe `input`
- wl-find-cursor compilé et installé (voir github.com/cjacker/wl-find-cursor)
  git clone https://github.com/cjacker/wl-find-cursor
  cd wl-find-cursor && make
  sudo cp wl-find-cursor /usr/local/bin/
"""
 
import re
import subprocess
import json
import time
 
# Codes boutons ydotool (cf. man ydotool)
BUTTON_LEFT = "0xC0"
BUTTON_RIGHT = "0xC1"
BUTTON_MIDDLE = "0xC2"
 
_NUM_RE = re.compile(r"-?\d+")
 
# Position mémorisée en interne, mise à jour par move_to/click/drag_to.
_last_position = (0, 0)
 
 
# -------------------- MOVE (Sway natif) --------------------
 
def move_to(x: int, y: int):
    """Déplace la souris à des coordonnées absolues GLOBALES (x, y)."""
    global _last_position
    subprocess.run(
        ["swaymsg", "seat", "seat0", "cursor", "set", str(x), str(y)],
        check=True,
    )
    _last_position = (x, y)
 
 
# -------------------- Pilotage souris (ydotool) --------------------
 
def _button_code(button: str) -> str:
    return {
        "left": BUTTON_LEFT,
        "right": BUTTON_RIGHT,
        "middle": BUTTON_MIDDLE,
    }.get(button, BUTTON_LEFT)
 
 
def click(x: int = None, y: int = None, button: str = "left"):
    """Clique au point (x, y). Si x/y omis, clique à la position actuelle."""
    if x is not None and y is not None:
        move_to(x, y)
    subprocess.run(["ydotool", "click", _button_code(button)], check=True, capture_output=True)
 
 
def right_click(x: int = None, y: int = None):
    click(x, y, button="right")
 
 
def left_click(x: int = None, y: int = None):
    click(x, y, button="left")
 
 
def double_click(x: int = None, y: int = None, button: str = "left"):
    click(x, y, button)
    click(button=button)  # second clic à la même position
 
 
def _button_base(button: str) -> int:
    """Code de base du bouton (sans bit press/release)."""
    return {
        "left": 0x00,
        "right": 0x01,
        "middle": 0x02,
    }.get(button, 0x00)
 
 
def mouse_down(button: str = "left"):
    """Maintient le bouton enfoncé (sans le relâcher)."""
    code = 0x40 | _button_base(button)
    subprocess.run(["ydotool", "click", f"0x{code:02X}"], check=True, capture_output=True)
 
 
def mouse_up(button: str = "left"):
    """Relâche le bouton précédemment maintenu."""
    code = 0x80 | _button_base(button)
    subprocess.run(["ydotool", "click", f"0x{code:02X}"], check=True, capture_output=True)
 
 
def drag_to(x: int, y: int, button: str = "left"):
    """Maintient le bouton et glisse jusqu'à (x, y). Simple, sans vitesse."""
    mouse_down(button)
    move_to(x, y)  # met aussi à jour _last_position
    mouse_up(button)
 
 
def scroll(amount: int):
    """Scroll vertical. Positif = vers le haut, négatif = vers le bas."""
    direction = "4" if amount > 0 else "5"
    for _ in range(abs(amount)):
        subprocess.run(["ydotool", "click", direction], check=False)
 
 
# -------------------- Multi-écrans (offset des outputs Sway) --------------------
 
def _get_outputs():
    """
    Renvoie la liste des écrans (sorties) avec leur position globale,
    via `swaymsg -t get_outputs`.
    """
    try:
        p = subprocess.run(
            ["swaymsg", "-t", "get_outputs"],
            capture_output=True,
            text=True,
            timeout=0.5,
        )
        return json.loads(p.stdout)
    except Exception as e:
        print(f"Erreur lecture outputs Sway : {e}")
        return []
 
 
def _find_output_for_local_pos(local_x, local_y, outputs):
    """
    wl-find-cursor renvoie des coordonnées LOCALES à l'écran actif.
    On utilise l'output marqué "focused" par Sway comme référence.
    """
    for out in outputs:
        if out.get("focused"):
            return out
    for out in outputs:
        if out.get("active"):
            return out
    return None
 
 
# -------------------- Lecture position réelle (wl-find-cursor) --------------------
 
def get_position():
    """
    Lit la VRAIE position actuelle du curseur en coordonnées GLOBALES
    (cumulées sur tous les écrans), corrigeant le bug de wl-find-cursor
    qui renvoie des coordonnées locales à l'écran actif.
    """
    try:
        p = subprocess.run(
            ["wl-find-cursor", "-p"],
            capture_output=True,
            text=True,
            timeout=0.5,
        )
        nums = _NUM_RE.findall(p.stdout)
        if len(nums) < 2:
            return None
 
        local_x, local_y = int(nums[0]), int(nums[1])
 
        outputs = _get_outputs()
        if not outputs:
            return local_x, local_y
 
        out = _find_output_for_local_pos(local_x, local_y, outputs)
        if out is None:
            return local_x, local_y
 
        rect = out.get("rect", {})
        offset_x = rect.get("x", 0)
        offset_y = rect.get("y", 0)
 
        return local_x + offset_x, local_y + offset_y
 
    except FileNotFoundError:
        raise RuntimeError(
            "wl-find-cursor introuvable. Installe-le :\n"
            "  git clone https://github.com/cjacker/wl-find-cursor\n"
            "  cd wl-find-cursor && make\n"
            "  sudo cp wl-find-cursor /usr/local/bin/"
        )
    except Exception as e:
        print(f"Erreur lecture position : {e}")
    return None
 
 
def get_last_known_position():
    """Renvoie la dernière position FIXÉE par ce script (move_to/click/drag_to)."""
    return _last_position
 
 
def position_generator(interval: float = 0.1):
    """Générateur infini : yield (x, y) la vraie position, en continu."""
    while True:
        pos = get_position()
        if pos:
            yield pos
        time.sleep(interval)
 
 
if __name__ == "__main__":
    print("Déplacement vers (100, 100)...")
    move_to(100, 100)
    print("Position lue :", get_position())
 
    print("Déplacement vers (800, 600)...")
    move_to(800, 600)
    print("Position lue :", get_position())
 
    print("Clic gauche à (500, 300)...")
    click(500, 300)
    print("Position lue :", get_position())
 
    print("\nTest press / release...")
    mouse_down("left")
    time.sleep(0.5)
    mouse_up("left")
 
    print("Terminé.")
 
