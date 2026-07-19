<div align="center">

[![Slovencina](https://img.shields.io/badge/SK-Sloven%C4%8Dina-30363d?style=for-the-badge)](README.md) [![English](https://img.shields.io/badge/EN-English-2ea043?style=for-the-badge)](README.en.md)

</div>

<div align="center">

# 🖱️ CursorKeep

**Keeps your Windows computer awake with subtle, smooth cursor movements.**

![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=flat-square&logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?style=flat-square&logo=windows&logoColor=white)
![GUI](https://img.shields.io/badge/GUI-Tkinter-FF6F00?style=flat-square)
![Build](https://img.shields.io/badge/Build-PyInstaller-306998?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-2ea043?style=flat-square)
![Version](https://img.shields.io/badge/Version-2.3-8957e5?style=flat-square)

</div>

---

## 📑 Contents

- [🔍 Overview](#-overview)
- [✨ Features](#-features)
- [📥 Installation and launch](#-installation-and-launch)
- [🚀 First launch](#-first-launch)
- [🗂️ Project structure](#️-project-structure)
- [⌨️ Keyboard shortcuts and controls](#️-keyboard-shortcuts-and-controls)
- [⚙️ Configuration](#️-configuration)
- [🧠 How the mouse movement works](#-how-the-mouse-movement-works)
- [🧩 Libraries used](#-libraries-used)
- [⚠️ Warnings and limitations](#️-warnings-and-limitations)
- [📄 License](#-license)

---

## 🔍 Overview

CursorKeep is a single-file Windows application (`cursorkeep.py`, version 2.3) with a small Tkinter GUI that moves the mouse cursor around the primary monitor at regular but randomised intervals. The goal is to keep the system from marking the computer as idle — without the movements looking mechanical.

The program runs in the background in the system tray, stores its settings in a JSON file next to itself, and **stops automatically as soon as the user grabs the mouse**. It can be bundled into a standalone `.exe` file that does not require Python to be installed.

> [!NOTE]
> The application is intended exclusively for Windows — it uses `winreg` for autostart and `user32.dll` to determine the dimensions of the primary monitor.

---

## ✨ Features

- 🎯 **Natural movement** — the cursor does not simply jump to a random spot: the script generates 12 candidates and picks the one heading in the direction most different from the previous move.
- 🎨 **Four movement styles** — a classic smooth glide, a two-step move with a change of direction halfway through, a fast move with a gentle "settling", and a two-phase move with a final adjustment.
- 📈 **Random easing** — every move uses one of four tween functions (`easeOutQuad`, `easeInOutQuad`, `easeOutCubic`, `easeInOutSine`) and lasts 0.5 – 2.1 s.
- 🪶 **Idle jiggle** — while waiting between moves it occasionally (every ~5 – 13 s: the first jiggle after a move comes in 5 – 12 s, later ones in 6 – 13 s) nudges the cursor by 1 – 4 px so that activity never disappears entirely.
- 🖐️ **Auto-stop on mouse touch** — a separate monitoring thread checks the cursor position every 0.32 s; if it deviates by more than 15 px in two consecutive checks, the program stops and shows the window.
- 🛡️ **Safe zone** — the large moves always aim inside a zone kept the configured percentage away from the screen edge (18 % by default); the gentle settling step at the end of a move and the idle jiggle can drift a few pixels outside it.
- 🔔 **Tray icon** — generated at runtime via Pillow (a blue circle with a cursor arrow), with a menu to show the window, start/stop, and quit.
- ⌨️ **Custom toggle hotkey** — you press a button in the GUI, press a key, and it is saved to the configuration as the on/off toggle.
- 🚨 **Emergency stop** — `Ctrl + Shift + Q` works while the movement is running; it is registered when you press `▶ Spustiť` (Start) and unregistered when the movement stops.
- 🔁 **Autostart with Windows** — writes to the registry key `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run` under the name `CursorKeep`.
- 👻 **Stealth mode** — on the very first launch the window is always shown (so you can configure it); on subsequent launches it can go straight to the tray.
- 💾 **Instant saving** — every change in the settings is written to `cursorkeep_config.json` immediately, no need to click "Save".

---

## 📥 Installation and launch

### Option A — prebuilt `.exe` (easiest)

Download the latest `CursorKeep.exe` from the [Releases](https://github.com/Apoliak7777/CursorKeep/releases) section and run it. No Python, no build.

If you already have the `.exe` in the project folder, you can also start it via:

```batch
run.bat
```

`run.bat` looks for `CursorKeep.exe` first in the current folder, then in `dist\`, and if neither exists it prints instructions to run the build.

### Option B — running from source

```bash
pip install -r requirements.txt
python cursorkeep.py
```

### Option C — building your own `.exe`

Automatically (installs the dependencies and PyInstaller and copies the result into the project root):

```batch
build_windows.bat
```

Or manually:

```bash
pip install pyautogui keyboard pystray pillow pyinstaller
pyinstaller --clean --noconfirm CursorKeep.spec
```

You will find the result in `dist\CursorKeep.exe` — onefile, no console window, with the `CursorKeep.ico` icon.

> [!IMPORTANT]
> Always use `CursorKeep.spec` for manual builds. It contains `collect_all('pystray')` and `collect_all('PIL')` — without them the tray icon in the bundled `.exe` will not work reliably.

---

## 🚀 First launch

| Step | What to do |
|------|------------|
| 1 | Start the application — on the first launch the window is **always** shown, even if `start_minimized` is enabled (the config file does not exist yet). |
| 2 | Click `⚙ Nastavenia` (Settings) and adjust the intervals, safe zone, jiggle, and autostart. |
| 3 | Click the `Hotkey: žiadny` (Hotkey: none) button and press the key you want to use to toggle the program (`Esc` cancels the capture). |
| 4 | Click `▶ Spustiť` (Start). The window hides itself into the tray after ~120 ms. |
| 5 | On subsequent launches the program goes straight to the tray — unless you disable the "Pri spustení ihneď skryť (tray)" (Hide to tray immediately on startup) option. |

---

## 🗂️ Project structure

```text
CursorKeep/
├── cursorkeep.py         # the whole app: GUI, movement loop, monitor, tray, config, registry
├── run.bat               # launcher for the prebuilt .exe (project root or dist\)
├── build_windows.bat     # dependency install + PyInstaller build + copy of the .exe to the root
├── CursorKeep.spec       # PyInstaller spec: onefile, console=False, collect_all pystray + PIL
├── CursorKeep.ico        # icon of the bundled .exe
├── requirements.txt      # pyautogui, keyboard, pystray, pillow
├── .gitignore            # ignores build/, dist/, *.exe, cursorkeep_config.json, cursorkeep.log
├── LICENSE               # MIT License, Copyright (c) 2026 Apoliak7777
├── README.md             # the Slovak README
└── README.en.md          # this file (English version)
```

Files created at runtime (not in the repository, they are in `.gitignore`):

| File | Location | Meaning |
|------|----------|---------|
| `cursorkeep_config.json` | next to the `.exe` or `.py` | saved settings; read with the `utf-8-sig` encoding (BOM-tolerant) |
| `cursorkeep.log` | next to the `.exe` or `.py` | debug log; created only on errors (e.g. a tray or hotkey failure) |

---

## ⌨️ Keyboard shortcuts and controls

| Action | How |
|--------|-----|
| Turn on / off | The custom hotkey configured in the GUI (none by default) |
| Emergency stop | `Ctrl + Shift + Q` — registered when the movement is started and unregistered when it is stopped (not for the whole lifetime of the app) |
| Automatic stop | Mouse movement over 15 px in two consecutive checks |
| PyAutoGUI FailSafe | Moving the cursor into a screen corner raises `FailSafeException` and the loop terminates |
| Cancel hotkey capture | `Esc` during the "Stlač tlačidlo…" (Press a key…) mode |
| Hide the window | The `Skryť` (Hide) button or closing the window (while the program is running it asks: hide / quit) |
| Tray menu | `Zobraziť okno` (Show window) · `▶ Spustiť` (Start) / `⏹ Zastaviť` (Stop) · `Ukončiť` (Quit) |

> [!WARNING]
> The custom hotkey capture stores **a single key** (`event.name`), not a combination. Pick a key you do not normally use — for example `f9` or `scroll lock`. The hotkey is registered with `suppress=True`, so it will not reach other applications.

---

## ⚙️ Configuration

Settings are stored in `cursorkeep_config.json` in the application folder. Unknown keys are ignored on load, and values are always clamped into a valid range.

| Key | Default | Valid range (after clamping) | Range in the GUI | Description |
|-----|---------|------------------------------|------------------|-------------|
| `min_interval` | `6` | 5 – 300 s | Spinbox 8 – 180 | Minimum pause between large moves |
| `max_interval` | `18` | 10 – 600 s | Spinbox 15 – 300 | Maximum pause; if it is lower than or equal to the minimum, it is recalculated as `min + 10` |
| `safe_zone_percent` | `18` | 3 – 35 % | Slider 5 – 28 % | The screen margin the large moves will not enter |
| `enable_jiggle` | `true` | `true` / `false` | Checkbox | Tiny movements (1 – 4 px) during the waiting phase |
| `run_at_startup` | `false` | `true` / `false` | Checkbox | Writes / deletes the `CursorKeep` value in the Run registry key |
| `start_minimized` | `true` | `true` / `false` | Checkbox | Go straight to the tray at startup (does not apply to the first launch) |
| `toggle_hotkey` | `null` | key name | Hotkey button | The key used to toggle on/off |

Example file:

```json
{
  "min_interval": 6,
  "max_interval": 18,
  "safe_zone_percent": 18,
  "enable_jiggle": true,
  "run_at_startup": false,
  "start_minimized": true,
  "toggle_hotkey": "f9"
}
```

> [!NOTE]
> The actual pause is computed as `random.uniform(min_interval, min(max_interval, 18))` — so the real wait never exceeds 18 seconds, even if you set a higher `max_interval` in the configuration. This is intentional: the cursor has to move within 20 seconds.

---

## 🧠 How the mouse movement works

| Phase | What happens |
|-------|--------------|
| **Target selection** | 12 random points inside the safe zone are generated. Each gets a score: a bonus for a direction different from the previous move (negative dot product × 80), a bonus for a "comfortable" distance (highest for 80 – 350 px), and random noise of ±10. |
| **Slight scatter** | With a probability of 15 % the target is shifted by a further ±40 px horizontally and ±30 px vertically. |
| **The move** | One of the 4 styles and one of the 4 tween functions are picked at random; total duration 0.5 – 2.1 s. |
| **Micro-correction** | With a probability of 8 % a short "slip" of ±5 px horizontally and ±4 px vertically follows, then a move back. |
| **Grace period** | Before the move a protective window of 3.5 s is set, plus another 1.8 s after it, during which the activity monitor ignores position differences — otherwise it would treat the script's own movement as user input. |
| **Waiting** | The loop sleeps in random chunks of 0.7 – 2.2 s so that it can react quickly to a stop request; in the meantime it may perform a jiggle. |
| **Monitoring** | An independent thread compares the real cursor position with the last position set by the script every 0.32 s. |

---

## 🧩 Libraries used

| Library | Required | What it is for |
|---------|----------|----------------|
| `pyautogui` | ✅ yes | Cursor moves, easing functions, `FAILSAFE`, position lookup |
| `keyboard` | ✅ yes | Global hotkeys (`Ctrl+Shift+Q`, the custom toggle) and key capture |
| `pystray` | ⚪ optional | System tray icon and menu |
| `pillow` | ⚪ optional | Drawing the tray icon at runtime (`Image`, `ImageDraw`) |
| `tkinter` | ✅ yes | GUI — part of the standard Python installation |
| `winreg`, `ctypes` | ✅ yes | Autostart in the registry, primary monitor dimensions — the standard Windows library |

If `pyautogui` or `keyboard` is missing, the program prints an error and the installation command, then exits. If only `pystray` or `pillow` is missing, the program keeps running — just without the tray icon (the window is minimised instead of hidden).

---

## ⚠️ Warnings and limitations

> [!WARNING]
> **Windows only.** The `winreg` import and the `user32.GetSystemMetrics` call are tied to Windows. The application does not work on Linux or macOS.

- 🖥️ **Primary monitor only** — target points are computed from `SM_CXSCREEN` / `SM_CYSCREEN`, i.e. from the dimensions of the primary screen, not from the whole virtual desktop.
- 🔐 **Global hotkeys may require elevated privileges** — the `keyboard` library works with low-level hooks; if registration fails, it is recorded in `cursorkeep.log` and the application keeps running without the shortcut.
- 🛑 **Antivirus and EDR** — a bundled console-less `.exe` that simulates mouse input and writes to the registry at startup may be flagged as suspicious. That is common for this kind of tool.
- 🏢 **Corporate policy** — bypassing an idle timer or screen lock may violate your organisation's IT policy. Responsibility for using it is yours.
- 🚫 **It does not disable the screen lock** — once Windows is locked (`Win+L`), cursor movements will not help.
- ⏸️ **After an auto-stop you have to start it again** — when the program detects user input, it terminates the monitoring thread, shows the window and a message; the next run has to be started with the button or the hotkey.
- 🔄 **Rebuild after changing the code** — `run.bat` launches the prebuilt `.exe`, not `cursorkeep.py`. Changes to the source code only take effect after a rebuild or when running via `python cursorkeep.py`.

---

## 📄 License

The project is released under the **MIT License**, Copyright (c) 2026 Apoliak7777. You can find the full text in the [LICENSE](LICENSE) file.

---

<div align="center">

Built by **Alex Poliak** - [GitHub](https://github.com/Apoliak7777) - [alexpoliak21@gmail.com](mailto:alexpoliak21@gmail.com)

</div>
