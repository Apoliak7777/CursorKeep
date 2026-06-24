#!/usr/bin/env python3
"""
CursorKeep v2.3
Moderný nástroj na plynulé a inteligentné hýbanie myšou na Windows.

Vylepšenia v2.3:
- Vlastný nastaviteľný hotkey na toggle (v GUI)
- Prvý štart vždy ukáže okno (pre setup), potom stealth podľa nastavenia
- Väčšie GUI + lepšie formátovanie textu dole (binds)
- GitHub promo priamo v mini GUI
- Lepšia detekcia falošného pohybu myši (vyšší threshold + consecutive checks)
- Rôzne štýly pohybov pre prirodzenosť + smerová rozmanitosť
- Max interval ~18s (pohyb do 20s)

Pôvodné v2.2:
- Spoľahlivejší .exe + primary monitor podpora
- Odolnosť voči BOM v configu, lepšie hotkey
"""

import tkinter as tk
from tkinter import ttk, messagebox
import pyautogui
import random
import time
import threading
import sys
import os
import json
import keyboard
import webbrowser

# Windows-only
try:
    import winreg
except ImportError:
    winreg = None

# Helper na získanie primárnej obrazovky (aj pri viacerých monitoroch)
try:
    import ctypes
    _user32 = ctypes.windll.user32
except Exception:
    _user32 = None
    ctypes = None

try:
    import pystray
    from PIL import Image, ImageDraw
    HAS_TRAY = True
except ImportError:
    HAS_TRAY = False

# ==================== GLOBÁLNE STAVY ====================
is_running = False
move_thread = None
monitor_thread = None
last_script_pos = None
moving_grace_until = 0
tray_icon = None
hotkey_registered = False
current_toggle_hotkey = None
hotkey_button = None
capturing_hotkey = False

# Konfigurácia (s defaultmi)
DEFAULT_CONFIG = {
    "min_interval": 6,
    "max_interval": 18,
    "safe_zone_percent": 18,
    "enable_jiggle": True,
    "run_at_startup": False,
    "start_minimized": True,   # pri spustení ihneď schovať do tray
    "toggle_hotkey": None,
}

current_config = DEFAULT_CONFIG.copy()
CONFIG_FILENAME = "cursorkeep_config.json"


def get_app_dir():
    """Vráti priečinok, kde beží exe alebo .py (pre config)."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def get_config_path():
    return os.path.join(get_app_dir(), CONFIG_FILENAME)


def _log(msg):
    """Jednoduchý log chýb vedľa exe (len pre debug, nevytvára sa pri normálnom behu)."""
    try:
        log_path = os.path.join(get_app_dir(), "cursorkeep.log")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    except Exception:
        pass


def load_config():
    """Načíta config z JSONu (ak existuje)."""
    global current_config
    path = get_config_path()
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8-sig") as f:
                loaded = json.load(f)
            current_config.update({k: v for k, v in loaded.items() if k in DEFAULT_CONFIG})
    except Exception as e:
        print(f"Chyba pri načítaní configu: {e}")
        _log(f"load_config error: {e}")
    # Clamp hodnoty
    _clamp_config()


def save_config():
    """Uloží aktuálny config."""
    path = get_config_path()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(current_config, f, indent=2)
    except Exception as e:
        print(f"Chyba pri ukladaní configu: {e}")
        _log(f"save_config error: {e}")


def _clamp_config():
    """Zabezpečí platné hodnoty."""
    c = current_config
    c["min_interval"] = max(5, min(int(c.get("min_interval", 25)), 300))
    c["max_interval"] = max(10, min(int(c.get("max_interval", 95)), 600))
    if c["min_interval"] >= c["max_interval"]:
        c["max_interval"] = c["min_interval"] + 10
    c["safe_zone_percent"] = max(3, min(int(c.get("safe_zone_percent", 18)), 35))
    c["enable_jiggle"] = bool(c.get("enable_jiggle", True))
    c["run_at_startup"] = bool(c.get("run_at_startup", False))


def _should_start_hidden():
    """Prvýkrát ukáž okno (aby používateľ vedel čo spustil), potom podľa nastavenia stealth."""
    try:
        if not os.path.exists(get_config_path()):
            return False  # first run -> show the small window
    except Exception:
        pass
    return bool(current_config.get("start_minimized", True))


def _get_primary_size():
    """Vráti (width, height) primárneho monitora (nie virtuálny desktop)."""
    try:
        if _user32:
            w = _user32.GetSystemMetrics(0)  # SM_CXSCREEN
            h = _user32.GetSystemMetrics(1)  # SM_CYSCREEN
            if w > 100 and h > 100:
                return int(w), int(h)
    except Exception:
        pass
    # fallback
    try:
        return pyautogui.size()
    except Exception:
        return 1920, 1080


# ==================== WINDOWS STARTUP ====================
def is_in_startup():
    """Zistí, či je CursorKeep v registroch pre spustenie pri štarte."""
    if not winreg:
        return False
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_READ
        )
        val, _ = winreg.QueryValueEx(key, "CursorKeep")
        winreg.CloseKey(key)
        return bool(val)
    except Exception:
        return False


def set_startup(enabled: bool):
    """Zapne/vypne spustenie pri štarte Windows."""
    if not winreg:
        return False
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_SET_VALUE
        )
        if enabled:
            if getattr(sys, 'frozen', False):
                exe_path = sys.executable
            else:
                exe_path = os.path.abspath(sys.argv[0])
            # Použijeme úvodzovky pre cesty s medzerami
            command = f'"{exe_path}"'
            winreg.SetValueEx(key, "CursorKeep", 0, winreg.REG_SZ, command)
        else:
            try:
                winreg.DeleteValue(key, "CursorKeep")
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
        return True
    except Exception as e:
        print(f"Chyba pri nastavovaní startupu: {e}")
        return False


# ==================== TRAY ICON ====================
def create_tray_image():
    """Vytvorí jednoduchú modernú ikonu pre tray (modrý kruh + kurzor)."""
    if not HAS_TRAY:
        return None
    size = 64
    img = Image.new("RGB", (size, size), color=(248, 250, 252))
    d = ImageDraw.Draw(img)

    # Hlavný kruh (modrý)
    margin = 6
    d.ellipse([margin, margin, size-margin, size-margin], fill=(30, 64, 175), outline=(15, 23, 42))

    # Biely vnútorný kruh
    d.ellipse([14, 14, 50, 50], fill=(255, 255, 255))

    # Jednoduchý kurzor (šípka)
    d.polygon([(30, 22), (30, 42), (38, 34)], fill=(30, 64, 175))
    d.polygon([(32, 24), (32, 38), (37, 33)], fill=(248, 250, 252))

    return img


def ensure_tray():
    """Vytvorí tray ikonu, ak ešte neexistuje."""
    global tray_icon
    if not HAS_TRAY or tray_icon is not None:
        return
    try:
        image = create_tray_image()
        menu = pystray.Menu(
            pystray.MenuItem("Zobraziť okno", show_window_from_tray),
            pystray.MenuItem(
                lambda item: "⏹ Zastaviť" if is_running else "▶ Spustiť",
                toggle_from_tray
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Ukončiť", quit_from_tray),
        )
        tray_icon = pystray.Icon("CursorKeep", image, "CursorKeep", menu)  # tooltip in tray
        threading.Thread(target=tray_icon.run, daemon=True).start()
    except Exception as e:
        print(f"Chyba pri vytváraní tray: {e}")
        _log(f"ensure_tray error: {e}")


def remove_tray():
    global tray_icon
    if tray_icon:
        try:
            tray_icon.stop()
        except Exception:
            pass
        tray_icon = None


def show_window_from_tray(icon=None, item=None):
    """Zobrazí hlavné okno z tray menu."""
    try:
        root.after(0, _show_window_safe)
    except Exception:
        pass


def _show_window_safe():
    try:
        root.deiconify()
        root.lift()
        root.focus_force()
    except Exception:
        pass


def toggle_from_tray(icon=None, item=None):
    """Prepne spustenie/zastavenie z tray menu."""
    try:
        root.after(0, _toggle_robot_safe)
    except Exception:
        pass


def _toggle_robot_safe():
    if is_running:
        stop_robot()
    else:
        start_robot()


def quit_from_tray(icon=None, item=None):
    """Ukončí aplikáciu z tray."""
    global is_running
    is_running = False
    try:
        remove_tray()
    except Exception:
        pass
    try:
        root.after(0, root.destroy)
    except Exception:
        os._exit(0)


# ==================== HLAVNÁ LOGIKA POHYBU ====================
def move_mouse_loop():
    """Hlavná slučka – prirodzené pohyby myšou."""
    global is_running, last_script_pos, moving_grace_until

    last_dx = 0
    last_dy = 0

    while is_running:
        try:
            screen_width, screen_height = _get_primary_size()

            margin_pct = current_config["safe_zone_percent"] / 100.0
            margin_x = int(screen_width * margin_pct)
            margin_y = int(screen_height * margin_pct)

            current_x, current_y = pyautogui.position()

            # Algoritmus na výber cieľa: náhodný, ale nie rovnakým smerom ako predtým
            # + rôzne vzdialenosti pre prirodzenosť
            best_target = None
            best_score = -999
            for _ in range(12):
                tx = random.randint(margin_x, screen_width - margin_x)
                ty = random.randint(margin_y, screen_height - margin_y)
                dx = tx - current_x
                dy = ty - current_y
                dist = (dx * dx + dy * dy) ** 0.5

                # Skóre za rozmanitosť smeru (chceme iný smer ako last)
                dir_score = 0
                if last_dx != 0 or last_dy != 0:
                    # dot product - čím menší/negatívny, tým lepšie (iný/opačný smer)
                    dot = (dx * last_dx + dy * last_dy) / (dist + 1)
                    dir_score = -dot * 80   # vyššie skóre pre odlišný smer

                # Preferuj rôzne vzdialenosti (nie vždy rovnako ďaleko)
                dist_pref = 30
                if 80 < dist < 350:
                    dist_pref = 80
                elif 350 < dist < 700:
                    dist_pref = 60
                elif dist < 50:
                    dist_pref = 10

                score = dir_score + dist_pref + random.uniform(-10, 10)
                if score > best_score:
                    best_score = score
                    best_target = (tx, ty, dx, dy)

            target_x, target_y, new_dx, new_dy = best_target

            # Občas ešte jemne posuň cieľ pre extra náhodnosť
            if random.random() < 0.15:
                target_x = max(margin_x, min(screen_width - margin_x, target_x + random.randint(-40, 40)))
                target_y = max(margin_y, min(screen_height - margin_y, target_y + random.randint(-30, 30)))

            # Nastav grace hneď, aby počas celej sekvencie pohybov monitor nezasiahol
            moving_grace_until = time.time() + 3.5
            last_script_pos = (target_x, target_y)

            # === Algoritmus pohybu: rôzne štýly pre prirodzenosť ===
            move_duration = random.uniform(0.5, 2.1)

            # Náhodný easing pre prirodzené zrýchlenie
            tweens = [
                pyautogui.easeOutQuad,
                pyautogui.easeInOutQuad,
                pyautogui.easeOutCubic,
                pyautogui.easeInOutSine
            ]
            tween = random.choice(tweens)

            style = random.randint(1, 4)

            if style == 1:
                # Klasický plynulý pohyb s easingom
                pyautogui.moveTo(target_x, target_y, duration=move_duration, tween=tween)

            elif style == 2:
                # Jemný dvoj-krok (malá zmena smeru uprostred - vyzerá ľudsky)
                mid_x = current_x + int((target_x - current_x) * 0.55) + random.randint(-18, 18)
                mid_y = current_y + int((target_y - current_y) * 0.55) + random.randint(-14, 14)
                mid_x = max(margin_x, min(screen_width - margin_x, mid_x))
                mid_y = max(margin_y, min(screen_height - margin_y, mid_y))
                pyautogui.moveTo(mid_x, mid_y, duration=move_duration * 0.4, tween=tween)
                time.sleep(random.uniform(0.03, 0.09))
                pyautogui.moveTo(target_x, target_y, duration=move_duration * 0.6, tween=tween)

            elif style == 3:
                # Rýchlejší malý pohyb + jemné "usadenie"
                pyautogui.moveTo(target_x, target_y, duration=min(0.9, move_duration), tween=pyautogui.easeOutQuad)
                time.sleep(random.uniform(0.05, 0.15))
                # malé finálne usadenie iným smerom
                fin_x = target_x + random.randint(-7, 7)
                fin_y = target_y + random.randint(-5, 5)
                pyautogui.moveTo(fin_x, fin_y, duration=0.12)
                try:
                    actual = pyautogui.position()
                    last_script_pos = (actual[0], actual[1])
                except Exception:
                    pass

            else:
                # Krátky pohyb v novom smere + druhá fáza
                pyautogui.moveTo(target_x, target_y, duration=move_duration * 0.7, tween=tween)
                time.sleep(random.uniform(0.04, 0.1))
                # druhá fáza trochu inam (náhodný malý posun)
                adj_x = target_x + random.randint(-15, 15)
                adj_y = target_y + random.randint(-10, 10)
                adj_x = max(margin_x, min(screen_width - margin_x, adj_x))
                adj_y = max(margin_y, min(screen_height - margin_y, adj_y))
                pyautogui.moveTo(adj_x, adj_y, duration=move_duration * 0.3)
                try:
                    actual = pyautogui.position()
                    last_script_pos = (actual[0], actual[1])
                except Exception:
                    pass

            # Veľmi občasná drobná korekcia (aby to nebolo stále dokonalé)
            if random.random() < 0.08:
                time.sleep(random.uniform(0.03, 0.1))
                corr_x = target_x + random.randint(-5, 5)
                corr_y = target_y + random.randint(-4, 4)
                corr_x = max(margin_x, min(screen_width - margin_x, corr_x))
                corr_y = max(margin_y, min(screen_height - margin_y, corr_y))
                pyautogui.moveTo(corr_x, corr_y, duration=0.08)
                time.sleep(0.04)
                pyautogui.moveTo(target_x, target_y, duration=0.06)
                try:
                    actual = pyautogui.position()
                    last_script_pos = (actual[0], actual[1])
                except Exception:
                    pass

            # Uložíme smer pre ďalší výber cieľa (aby sa neopakoval rovnaký smer)
            last_dx = new_dx
            last_dy = new_dy

            # Aktualizuj last_script_pos na skutočnú pozíciu (nie plánovanú)
            # – zabraňuje falošným detekciám
            try:
                actual = pyautogui.position()
                last_script_pos = (actual[0], actual[1])
            except Exception:
                pass

            # Predĺž grace ešte o chvíľu po dokončení
            moving_grace_until = time.time() + 1.8

            # Náhodný interval podľa nastavení (max ~18-20s aby sa myš pohla do 20 sekúnd)
            min_int = current_config["min_interval"]
            max_int = current_config["max_interval"]
            sleep_time = random.uniform(min_int, min(max_int, 18))

            # Idle fáza – väčšinou pokoj, len občas veľmi jemný pohyb
            # (pôvodný štýl, ale s väčšou náhodnosťou v časovaní a veľkosti)
            elapsed = 0.0
            jiggle_enabled = current_config.get("enable_jiggle", True)
            next_jiggle = time.time() + random.uniform(5, 12)

            while elapsed < sleep_time and is_running:
                chunk = random.uniform(0.7, 2.2)
                time.sleep(chunk)
                elapsed += chunk

                now = time.time()
                if jiggle_enabled and now > next_jiggle:
                    try:
                        pos = pyautogui.position()
                        # Veľmi malé a nepravidelné
                        amt = random.randint(1, 4)
                        jx = max(0, min(screen_width - 1, pos[0] + random.randint(-amt, amt)))
                        jy = max(0, min(screen_height - 1, pos[1] + random.randint(-amt, amt)))
                        # Grace pred pohybom
                        moving_grace_until = time.time() + 1.2
                        pyautogui.moveTo(jx, jy, duration=random.uniform(0.08, 0.16))
                        try:
                            actual = pyautogui.position()
                            last_script_pos = (actual[0], actual[1])
                        except Exception:
                            last_script_pos = (jx, jy)
                        moving_grace_until = time.time() + 1.2
                    except Exception:
                        pass

                    # Ďalší malý pohyb s náhodným oneskorením (aby to nebolo pravidelné)
                    next_jiggle = now + random.uniform(6, 13)

        except pyautogui.FailSafeException:
            print("FailSafe aktivovaný.")
            is_running = False
            break
        except Exception as e:
            print(f"Chyba v move loop: {e}")
            time.sleep(4)


def mouse_activity_monitor():
    """Detekcia, že používateľ sa dotkol myši."""
    global is_running, last_script_pos, moving_grace_until

    THRESHOLD = 15          # zvýšené, aby sa menej falošne spúšťalo
    CHECK_EVERY = 0.32
    consecutive = 0

    while True:
        if not is_running:
            time.sleep(0.8)
            continue

        try:
            if last_script_pos is not None and time.time() > moving_grace_until:
                current = pyautogui.position()
                dx = abs(current[0] - last_script_pos[0])
                dy = abs(current[1] - last_script_pos[1])

                if dx > THRESHOLD or dy > THRESHOLD:
                    consecutive += 1
                    if consecutive >= 2:   # vyžadujeme dve po sebe idúce detekcie
                        print("Používateľ prevzal myš – automatické zastavenie.")
                        is_running = False
                        last_script_pos = None

                        try:
                            root.after(0, show_user_took_control)
                        except Exception:
                            pass
                        break
                else:
                    consecutive = 0
            else:
                consecutive = 0

            time.sleep(CHECK_EVERY)
        except Exception:
            time.sleep(1.0)


def show_user_took_control():
    """Zobrazí okno + správu po automatickom zastavení."""
    try:
        _show_window_safe()
        status_label.config(text="○ Zastavený (používateľ)", foreground="#b91c1c")
        start_button.config(text="▶ Spustiť", command=start_robot)
        messagebox.showinfo(
            "CursorKeep",
            "Dotkol si sa myši.\nCursorKeep sa automaticky zastavil."
        )
    except Exception:
        pass


# ==================== OVLÁDANIE ====================
def start_robot():
    global is_running, move_thread, monitor_thread

    if is_running:
        return

    is_running = True

    # Krátky diskrétny stav
    status_label.config(
        text="● Beží",
        foreground="#166534"
    )
    start_button.config(text="⏹ Zastaviť", command=stop_robot)
    start_button.state(["!disabled"])

    # Spusti vlákna
    move_thread = threading.Thread(target=move_mouse_loop, daemon=True)
    move_thread.start()

    if monitor_thread is None or not monitor_thread.is_alive():
        monitor_thread = threading.Thread(target=mouse_activity_monitor, daemon=True)
        monitor_thread.start()

    # Odstrániť starý hotkey pred pridaním (vyhnúť sa duplicitám)
    global hotkey_registered
    try:
        keyboard.remove_hotkey('ctrl+shift+q')
    except Exception:
        pass
    try:
        keyboard.add_hotkey('ctrl+shift+q', stop_from_hotkey, suppress=True)
        hotkey_registered = True
    except Exception as e:
        _log(f"add_hotkey failed: {e}")

    # Ihneď schovať do tray – chce to nenápadné
    root.after(120, minimize_to_tray)


def stop_robot():
    global is_running, last_script_pos, hotkey_registered
    is_running = False
    last_script_pos = None
    try:
        keyboard.remove_hotkey('ctrl+shift+q')
    except Exception:
        pass
    hotkey_registered = False

    status_label.config(
        text="○ Zastavený",
        foreground="#1e40af"
    )
    start_button.config(text="▶ Spustiť", command=start_robot)


def stop_from_hotkey():
    global is_running, last_script_pos, hotkey_registered
    if not is_running:
        return
    is_running = False
    last_script_pos = None
    try:
        keyboard.remove_hotkey('ctrl+shift+q')
    except Exception:
        pass
    hotkey_registered = False

    try:
        root.after(0, lambda: (
            _show_window_safe(),
            status_label.config(text="○ Zastavený (Ctrl+Shift+Q)", foreground="#1e40af"),
            start_button.config(text="▶ Spustiť", command=start_robot)
        ))
    except Exception:
        pass


def register_toggle_hotkey(hotkey_str):
    """Zaregistruje používateľský hotkey na toggle (zapni/vypni)."""
    global current_toggle_hotkey
    if current_toggle_hotkey:
        try:
            keyboard.remove_hotkey(current_toggle_hotkey)
        except Exception:
            pass
    current_toggle_hotkey = None
    if not hotkey_str:
        return
    try:
        keyboard.add_hotkey(hotkey_str, toggle_robot_from_hotkey, suppress=True)
        current_toggle_hotkey = hotkey_str
    except Exception as e:
        print(f"Hotkey chyba: {e}")


def toggle_robot_from_hotkey():
    """Callback pre custom hotkey."""
    try:
        root.after(0, _toggle_robot_safe)
    except Exception:
        pass


def update_hotkey_button():
    """Aktualizuje text tlačidla hotkey."""
    global hotkey_button
    if hotkey_button is None:
        return
    key = current_config.get("toggle_hotkey") or "žiadny"
    hotkey_button.config(text=f"Hotkey: {key}")


def set_custom_hotkey():
    """Spustí zachytávanie nového hotkey."""
    global capturing_hotkey, hotkey_button
    if capturing_hotkey:
        return
    capturing_hotkey = True

    # Zruš aktuálny ak je
    if current_toggle_hotkey:
        try:
            keyboard.remove_hotkey(current_toggle_hotkey)
        except Exception:
            pass

    if hotkey_button:
        hotkey_button.config(text="Stlač tlačidlo... (Esc zruší)")

    def on_key_event(event):
        global capturing_hotkey
        if not capturing_hotkey:
            return False
        if event.name.lower() == "esc":
            capturing_hotkey = False
            update_hotkey_button()
            try:
                keyboard.unhook(on_key_event)
            except Exception:
                pass
            return False

        key = event.name
        current_config["toggle_hotkey"] = key
        save_config()
        register_toggle_hotkey(key)
        capturing_hotkey = False
        update_hotkey_button()
        try:
            keyboard.unhook(on_key_event)
        except Exception:
            pass
        return False

    try:
        keyboard.hook(on_key_event)
    except Exception as e:
        print(f"Hotkey capture error: {e}")
        capturing_hotkey = False
        update_hotkey_button()


# ==================== GUI AKCIE ====================
def minimize_to_tray():
    """Skryje okno do tray (alebo len minimalizuje ak tray nie je dostupný)."""
    if HAS_TRAY:
        root.withdraw()
        ensure_tray()
    else:
        root.iconify()


def apply_settings_from_vars():
    """Prevezme hodnoty z GUI do configu a uloží."""
    try:
        current_config["min_interval"] = int(min_interval_var.get())
        current_config["max_interval"] = int(max_interval_var.get())
        current_config["safe_zone_percent"] = int(safe_zone_var.get())
        current_config["enable_jiggle"] = bool(jiggle_var.get())
    except (ValueError, tk.TclError):
        pass

    _clamp_config()

    # Aktualizuj premenné
    min_interval_var.set(current_config["min_interval"])
    max_interval_var.set(current_config["max_interval"])
    safe_zone_var.set(current_config["safe_zone_percent"])

    save_config()


def on_setting_changed(*args):
    """Okamžite uloží zmenu nastavení."""
    apply_settings_from_vars()


def toggle_startup():
    """Zapne/vypne startup + uloží."""
    enabled = bool(startup_var.get())
    current_config["run_at_startup"] = enabled
    if set_startup(enabled):
        save_config()
    else:
        # Ak zlyhalo, vráť späť
        startup_var.set(not enabled)
        current_config["run_at_startup"] = not enabled


def reset_to_defaults():
    """Obnoví predvolené nastavenia."""
    if messagebox.askyesno("Obnoviť predvolené?", "Naozaj chceš vrátiť všetky nastavenia na predvolené hodnoty?"):
        current_config.clear()
        current_config.update(DEFAULT_CONFIG.copy())

        min_interval_var.set(current_config["min_interval"])
        max_interval_var.set(current_config["max_interval"])
        safe_zone_var.set(current_config["safe_zone_percent"])
        jiggle_var.set(current_config["enable_jiggle"])
        startup_var.set(current_config["run_at_startup"])
        current_config["toggle_hotkey"] = None
        if current_toggle_hotkey:
            try:
                keyboard.remove_hotkey(current_toggle_hotkey)
            except Exception:
                pass
        update_hotkey_button()

        apply_settings_from_vars()

        # Startup vypneme explicitne
        if current_config["run_at_startup"]:
            set_startup(False)
            current_config["run_at_startup"] = False
            startup_var.set(False)
            save_config()


def on_closing():
    global is_running
    if is_running:
        choice = messagebox.askyesnocancel(
            "CursorKeep",
            "Beží na pozadí.\n\nÁno = skryť do tray\nNie = ukončiť"
        )
        if choice is None:   # Cancel
            return
        if choice:           # Yes -> tray
            root.withdraw()
            ensure_tray()
            return
        else:                # No -> quit
            is_running = False

    # Ukončenie
    if current_toggle_hotkey:
        try:
            keyboard.remove_hotkey(current_toggle_hotkey)
        except Exception:
            pass
    remove_tray()
    root.destroy()


def open_settings_dialog():
    """Malé diskrétne okno s nastaveniami."""
    dlg = tk.Toplevel(root)
    dlg.title("Nastavenia")
    dlg.geometry("340x260")
    dlg.resizable(False, False)
    dlg.configure(bg="#f8fafc")
    dlg.transient(root)
    dlg.grab_set()

    # Nastavenia obsahu
    pad = 12
    frame = ttk.Frame(dlg, padding=pad)
    frame.pack(fill="both", expand=True)

    # Interval
    ttk.Label(frame, text="Interval (s):").pack(anchor="w", pady=(0, 2))
    int_frame = ttk.Frame(frame)
    int_frame.pack(fill="x", pady=2)

    min_interval_var.set(current_config["min_interval"])
    max_interval_var.set(current_config["max_interval"])

    ttk.Label(int_frame, text="Min:").pack(side="left")
    ttk.Spinbox(int_frame, from_=8, to=180, width=5, textvariable=min_interval_var, command=on_setting_changed).pack(side="left", padx=4)
    ttk.Label(int_frame, text="Max:").pack(side="left", padx=(10,0))
    ttk.Spinbox(int_frame, from_=15, to=300, width=5, textvariable=max_interval_var, command=on_setting_changed).pack(side="left", padx=4)

    # Safe zone
    ttk.Label(frame, text="Bezpečná zóna (% od okraja):").pack(anchor="w", pady=(10, 2))
    zone_frame = ttk.Frame(frame)
    zone_frame.pack(fill="x")
    safe_zone_var.set(current_config["safe_zone_percent"])
    zone_pct = ttk.Label(zone_frame, text=f"{current_config['safe_zone_percent']} %", width=5)
    def _update_zone(v=None):
        try:
            zone_pct.config(text=f"{int(safe_zone_var.get())} %")
        except:
            pass
        on_setting_changed()
    ttk.Scale(zone_frame, from_=5, to=28, orient="horizontal", length=180, variable=safe_zone_var,
              command=_update_zone).pack(side="left")
    zone_pct.pack(side="left", padx=8)

    # Jiggle + Startup
    jiggle_var.set(current_config["enable_jiggle"])
    ttk.Checkbutton(frame, text="Malé pohyby (jiggle)", variable=jiggle_var, command=on_setting_changed).pack(anchor="w", pady=(10, 2))

    startup_var.set(current_config.get("run_at_startup", False))
    if is_in_startup():
        startup_var.set(True)

    ttk.Checkbutton(frame, text="Spustiť pri štarte Windows", variable=startup_var, command=toggle_startup).pack(anchor="w")

    # Nová voľba pre stealth
    start_min_var = tk.BooleanVar(value=current_config.get("start_minimized", True))
    def toggle_min():
        current_config["start_minimized"] = start_min_var.get()
        save_config()
    ttk.Checkbutton(frame, text="Pri spustení ihneď skryť (tray)", variable=start_min_var, command=toggle_min).pack(anchor="w", pady=(4, 0))

    ttk.Button(frame, text="Zavrieť", command=dlg.destroy).pack(pady=(14, 4), anchor="e")

    # GitHub ad
    gh = ttk.Label(frame, text="⭐ Podpor ma: github.com/Apoliak7777", font=("Segoe UI", 8), foreground="#64748b", cursor="hand2")
    gh.pack(pady=(6, 0))
    gh.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/Apoliak7777/CursorKeep"))

    # Pozn: žiadne dlg.mainloop() – dialog beží v rámci hlavného mainloop (grab_set)


# ==================== VYTVORENIE GUI ====================
def create_gui():
    global root, status_label, start_button, hotkey_button
    global min_interval_var, max_interval_var, safe_zone_var, jiggle_var, startup_var

    load_config()

    # Načítaj custom toggle hotkey
    if current_config.get("toggle_hotkey"):
        register_toggle_hotkey(current_config["toggle_hotkey"])

    # Vytvor root OKAMŽITE — tk.*Var() musia byť vytvorené až po existencii root okna
    root = tk.Tk()
    root.title("CursorKeep")
    root.geometry("400x320")
    root.resizable(False, False)
    root.configure(bg="#f8fafc")

    # Inicializuj premenné pre nastavenia (používa ich aj dialóg)
    min_interval_var = tk.IntVar(value=current_config["min_interval"])
    max_interval_var = tk.IntVar(value=current_config["max_interval"])
    safe_zone_var = tk.IntVar(value=current_config["safe_zone_percent"])
    jiggle_var = tk.BooleanVar(value=current_config["enable_jiggle"])
    startup_var = tk.BooleanVar(value=current_config.get("run_at_startup", False))

    # Jednoduchý čistý štýl
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TLabel", background="#f8fafc", font=("Segoe UI", 10))
    style.configure("Title.TLabel", background="#f8fafc", font=("Segoe UI", 14, "bold"), foreground="#1e40af")
    style.configure("TButton", font=("Segoe UI", 11, "bold"), padding=6)
    style.configure("Gray.TButton", background="#64748b", foreground="white")
    style.configure("Start.TButton", background="#16a34a", foreground="white")
    style.configure("Stop.TButton", background="#dc2626", foreground="white")

    # Minimalistická hlavička
    ttk.Label(root, text="CursorKeep", style="Title.TLabel").pack(pady=(10, 2))

    # GitHub reklama priamo v mini GUI - viditeľné hneď pod titulkom
    git_frame = ttk.Frame(root, style="TFrame")
    git_frame.pack(pady=3, fill="x", padx=10)
    git_label = ttk.Label(git_frame, text="⭐ Podpor ma: github.com/Apoliak7777", 
                          font=("Segoe UI", 8), foreground="#1e40af", cursor="hand2", background="#f0f4ff")
    git_label.pack(padx=5, pady=2)
    git_label.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/Apoliak7777/CursorKeep"))

    # Status - veľmi krátky
    status_label = ttk.Label(
        root,
        text="○ Zastavený",
        font=("Segoe UI", 12),
        foreground="#1e40af",
        background="#f8fafc"
    )
    status_label.pack(pady=4)

    # Veľké tlačidlo na spustenie/zastavenie
    start_button = ttk.Button(
        root,
        text="▶ Spustiť",
        style="Start.TButton",
        width=20,
        command=start_robot
    )
    start_button.pack(pady=8)

    # Custom hotkey row - viditeľné v mini GUI pre bind
    hotkey_frame = ttk.Frame(root)
    hotkey_frame.pack(pady=6)
    ttk.Label(hotkey_frame, text="Custom toggle hotkey:", font=("Segoe UI", 11)).pack(side="left")
    hotkey_button = ttk.Button(hotkey_frame, text="Hotkey: žiadny", width=14, command=set_custom_hotkey)
    hotkey_button.pack(side="left", padx=6)
    update_hotkey_button()

    # Malý spacer pre lepšiu viditeľnosť dole
    ttk.Frame(root, height=10).pack()

    # Malé ovládacie tlačidlá
    bottom = ttk.Frame(root)
    bottom.pack(pady=(8, 12))

    ttk.Button(bottom, text="Skryť", width=10, command=minimize_to_tray).pack(side="left", padx=3)
    ttk.Button(bottom, text="⚙ Nastavenia", width=12, command=open_settings_dialog).pack(side="left", padx=3)

    # Bind
    root.protocol("WM_DELETE_WINDOW", on_closing)

    # Vždy sa pokús o tray (ikona v lište), aj keď je okno viditeľné
    if HAS_TRAY:
        try:
            ensure_tray()
        except Exception:
            pass

    # Stealth: prvýkrát ukáž UI, potom podľa nastavenia (nenápadné po setup-e)
    # Na prvýkrát NEmiminimalizuj (aby používateľ videl GUI a mohol nastaviť)
    if os.path.exists(get_config_path()) and current_config.get("start_minimized", True):
        root.after(80, minimize_to_tray)

    root.mainloop()


# ==================== ENTRY POINT ====================
if __name__ == "__main__":
    missing = []
    for lib in ("pyautogui", "keyboard"):
        try:
            __import__(lib)
        except ImportError:
            missing.append(lib)

    if "pyautogui" not in missing and "keyboard" not in missing:
        # Tray je voliteľný, ale upozorníme
        if not HAS_TRAY:
            print("Upozornenie: pystray + pillow nie sú nainštalované. Tray nebude fungovať.")
            print("Nainštaluj: pip install pystray pillow")

    if missing:
        print("CHYBA: Chýbajú tieto knižnice:", ", ".join(missing))
        print("Nainštaluj ich príkazom:")
        print("   pip install pyautogui keyboard pystray pillow")
        input("Stlač ENTER pre ukončenie...")
        sys.exit(1)

    pyautogui.FAILSAFE = True

    # Naštartuj s načítaným configom
    load_config()
    if current_config["run_at_startup"]:
        # Len overíme (už je v registry)
        pass

    create_gui()
