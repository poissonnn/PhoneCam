"""
MADE BY CLAUDE
Lib maison pour piloter et lire la souris sous Wayland/Sway.
 
- Pilotage (move/click/drag/scroll) : via ydotool
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
import subprocess, json
import time
 
# Codes boutons ydotool (cf. man ydotool)
BUTTON_LEFT = "0xC0"
BUTTON_RIGHT = "0xC1"
BUTTON_MIDDLE = "0xC2"
 
_NUM_RE = re.compile(r"-?\d+")
 
# Position mémorisée en interne, mise à jour par move_to/click/drag_to.
# Utile comme fallback rapide si tu n'as pas besoin de la vraie lecture
# (évite de relancer un process à chaque appel).
_last_position = (0, 0)
 
 
# -------------------- MOVE (Sway natif) --------------------

def move_to(x: int, y: int):
    global _last_position

    subprocess.run(
        ["swaymsg", "seat", "seat0", "cursor", "set", str(x), str(y)],
        check=True,
    )

    _last_position = (x, y)

# -------------------- Pilotage souris (ydotool) --------------------

 
def click(x: int = None, y: int = None, button: str = "left"):
    """Clique au point (x, y). Si x/y omis, clique à la position actuelle."""
    if x is not None and y is not None:
        move_to(x, y)
 
    code = {
        "left": BUTTON_LEFT,
        "right": BUTTON_RIGHT,
        "middle": BUTTON_MIDDLE,
    }.get(button, BUTTON_LEFT)
 
    subprocess.run(["ydotool", "click", code], check=True)
 
 
def right_click(x: int = None, y: int = None):
    click(x, y, button="right")

def left_click(x: int = None, y: int = None):
    click(x, y, button="left")
 
 
def double_click(x: int = None, y: int = None, button: str = "left"):
    click(x, y, button)
    click(button=button)  # second clic à la même position
 
 
def drag_to(x: int, y: int, button: str = "left"):
    """Maintient le bouton et glisse jusqu'à (x, y). Simple, sans vitesse."""
    code = {
        "left": BUTTON_LEFT,
        "right": BUTTON_RIGHT,
        "middle": BUTTON_MIDDLE,
    }.get(button, BUTTON_LEFT)
 
    subprocess.run(["ydotool", "click", "--button", code, "--", "press"], check=True)
    move_to(x, y)  # met aussi à jour _last_position
    subprocess.run(["ydotool", "click", "--button", code, "--", "release"], check=True)
 
 
def scroll(amount: int):
    """Scroll vertical. Positif = vers le haut, négatif = vers le bas."""
    direction = "4" if amount > 0 else "5"
    for _ in range(abs(amount)):
        subprocess.run(["ydotool", "click", direction], check=False)
 
 
# -------------------- Multi-écrans (offset des outputs Sway) --------------------
 
def _get_outputs():
    """
    Renvoie la liste des écrans (sorties) avec leur position globale,
    via `swaymsg -t get_outputs`. Format attendu par sortie :
    {"name": "DP-1", "rect": {"x":0,"y":0,"width":1920,"height":1080}, "focused": bool, ...}
    """
    try:
        import json
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
    wl-find-cursor renvoie des coordonnées LOCALES à l'écran actif
    (pas globales). On ne peut pas deviner directement quel écran avec
    juste x/y locaux (puisque chaque écran recommence à 0,0). La seule
    info fiable est de savoir quel écran a le focus / curseur dessus
    -- on utilise donc l'output marqué "focused" par Sway.
    """
    for out in outputs:
        if out.get("focused"):
            return out
    # fallback : premier écran actif si aucun focused trouvé
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
            ["wl-find-cursor", "-p"],  # -p = skip animation, sortie immédiate
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
            # Pas de Sway / swaymsg dispo : on renvoie tel quel (mono-écran)
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
    """
    Renvoie la dernière position FIXÉE par ce script (move_to/click/drag_to).
    Rapide (pas de subprocess) mais faux si la souris bouge par ailleurs.
    """
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
 
    print("\nTracking en direct pendant 5s (bouge la souris)...")
    start = time.time()
    for x, y in position_generator(interval=0.2):
        print(f"Curseur à : ({x}, {y})")
        if time.time() - start > 5:
            break
 
    print("Terminé.")
 
