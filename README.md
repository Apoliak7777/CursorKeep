<div align="center">

[![Slovencina](https://img.shields.io/badge/SK-Sloven%C4%8Dina-2ea043?style=for-the-badge)](README.md) [![English](https://img.shields.io/badge/EN-English-30363d?style=for-the-badge)](README.en.md)

</div>

<div align="center">

# 🖱️ CursorKeep

**Udrží Windows počítač bdelý pomocou nenápadných, plynulých pohybov kurzora.**

![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=flat-square&logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?style=flat-square&logo=windows&logoColor=white)
![GUI](https://img.shields.io/badge/GUI-Tkinter-FF6F00?style=flat-square)
![Build](https://img.shields.io/badge/Build-PyInstaller-306998?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-2ea043?style=flat-square)
![Version](https://img.shields.io/badge/Version-2.3-8957e5?style=flat-square)

</div>

---

## 📑 Obsah

- [🔍 Prehľad](#-prehľad)
- [✨ Funkcie](#-funkcie)
- [📥 Inštalácia a spustenie](#-inštalácia-a-spustenie)
- [🚀 Prvé spustenie](#-prvé-spustenie)
- [🗂️ Štruktúra projektu](#️-štruktúra-projektu)
- [⌨️ Klávesové skratky a ovládanie](#️-klávesové-skratky-a-ovládanie)
- [⚙️ Konfigurácia](#️-konfigurácia)
- [🧠 Ako funguje pohyb myši](#-ako-funguje-pohyb-myši)
- [🧩 Použité knižnice](#-použité-knižnice)
- [⚠️ Upozornenia a obmedzenia](#️-upozornenia-a-obmedzenia)
- [📄 Licencia](#-licencia)

---

## 🔍 Prehľad

CursorKeep je jednosúborová Windows aplikácia (`cursorkeep.py`, verzia 2.3) s malým Tkinter GUI, ktorá v pravidelných, ale náhodných intervaloch presúva kurzor myši po primárnom monitore. Cieľom je, aby systém nevyhodnotil počítač ako nečinný — bez toho, aby pohyby vyzerali strojovo.

Program beží na pozadí v systémovej lište (tray), ukladá si nastavenia do JSON súboru vedľa seba a **automaticky sa zastaví, keď používateľ chytí myš**. Dá sa zabaliť do samostatného `.exe` súboru, ktorý nepotrebuje nainštalovaný Python.

> [!NOTE]
> Aplikácia je určená výhradne pre Windows — používa `winreg` pre autostart a `user32.dll` pre zistenie rozmerov primárneho monitora.

---

## ✨ Funkcie

- 🎯 **Prirodzený pohyb** — kurzor sa nepresúva len na náhodné miesto: skript vygeneruje 12 kandidátov a vyberie ten, ktorý smeruje čo najodlišnejšie od predchádzajúceho pohybu.
- 🎨 **Štyri štýly presunu** — klasický plynulý presun, dvoj-krok so zmenou smeru uprostred, rýchly pohyb s jemným „usadením" a dvojfázový presun s dorovnaním.
- 📈 **Náhodný easing** — každý presun použije jednu zo štyroch tween funkcií (`easeOutQuad`, `easeInOutQuad`, `easeOutCubic`, `easeInOutSine`) a trvanie 0,5 – 2,1 s.
- 🪶 **Jiggle v pokoji** — počas čakania medzi presunmi občas (každých ~5 – 13 s: prvý jiggle po presune o 5 – 12 s, ďalšie o 6 – 13 s) posunie kurzor o 1 – 4 px, aby aktivita nikdy úplne nezmizla.
- 🖐️ **Auto-stop pri dotyku myši** — samostatné monitorovacie vlákno kontroluje pozíciu kurzora každých 0,32 s; pri odchýlke nad 15 px v dvoch po sebe idúcich kontrolách sa program zastaví a zobrazí okno.
- 🛡️ **Bezpečná zóna** — veľké presuny vždy smerujú dovnútra zóny vzdialenej od okraja obrazovky o nastavené percento (predvolene 18 %); jemné usadenie na konci presunu a jiggle v pokoji ju môžu presiahnuť o pár pixelov.
- 🔔 **Tray ikona** — vygenerovaná za behu cez Pillow (modrý kruh so šípkou kurzora), s menu na zobrazenie okna, spustenie/zastavenie a ukončenie.
- ⌨️ **Vlastný toggle hotkey** — stlačíš tlačidlo v GUI, stlačíš klávesu a tá sa uloží do konfigurácie ako prepínač zapni/vypni.
- 🚨 **Núdzové zastavenie** — `Ctrl + Shift + Q` funguje počas behu pohybu; registruje sa pri kliknutí na `▶ Spustiť` a odregistruje sa pri zastavení.
- 🔁 **Autostart s Windows** — zápis do registra `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run` pod názvom `CursorKeep`.
- 👻 **Stealth režim** — pri prvom spustení sa okno vždy ukáže (kvôli nastaveniu), pri ďalších spusteniach sa môže rovno schovať do tray.
- 💾 **Okamžité ukladanie** — každá zmena v nastaveniach sa hneď zapíše do `cursorkeep_config.json`, netreba klikať na „Uložiť".

---

## 📥 Inštalácia a spustenie

### Možnosť A — hotový `.exe` (najjednoduchšie)

Stiahni najnovší `CursorKeep.exe` zo sekcie [Releases](https://github.com/Apoliak7777/CursorKeep/releases) a spusti ho. Žiadny Python, žiadny build.

Ak už `.exe` máš v priečinku projektu, spustíš ho aj cez:

```batch
run.bat
```

`run.bat` hľadá `CursorKeep.exe` najprv v aktuálnom priečinku, potom v `dist\`, a ak ani jeden neexistuje, vypíše pokyn spustiť build.

### Možnosť B — spustenie zo zdrojového kódu

```bash
pip install -r requirements.txt
python cursorkeep.py
```

### Možnosť C — vlastný build `.exe`

Automaticky (nainštaluje závislosti aj PyInstaller a skopíruje výsledok do koreňa projektu):

```batch
build_windows.bat
```

Alebo manuálne:

```bash
pip install pyautogui keyboard pystray pillow pyinstaller
pyinstaller --clean --noconfirm CursorKeep.spec
```

Výsledok nájdeš v `dist\CursorKeep.exe` — onefile, bez konzolového okna, s ikonou `CursorKeep.ico`.

> [!IMPORTANT]
> Pri manuálnom builde vždy použi `CursorKeep.spec`. Obsahuje `collect_all('pystray')` a `collect_all('PIL')` — bez toho tray ikona v zabalenom `.exe` spoľahlivo nefunguje.

---

## 🚀 Prvé spustenie

| Krok | Čo urob |
|------|---------|
| 1 | Spusti aplikáciu — pri prvom štarte sa okno **vždy** zobrazí, aj keď je `start_minimized` zapnuté (config súbor ešte neexistuje). |
| 2 | Klikni na `⚙ Nastavenia` a uprav intervaly, bezpečnú zónu, jiggle a autostart. |
| 3 | Klikni na tlačidlo `Hotkey: žiadny` a stlač klávesu, ktorou budeš program prepínať (`Esc` zruší zachytávanie). |
| 4 | Klikni na `▶ Spustiť`. Okno sa po ~120 ms samo schová do tray. |
| 5 | Pri ďalších spusteniach sa program schová do tray hneď — pokiaľ nevypneš voľbu „Pri spustení ihneď skryť (tray)". |

---

## 🗂️ Štruktúra projektu

```text
CursorKeep/
├── cursorkeep.py         # celá aplikácia: GUI, pohybová slučka, monitor, tray, config, registry
├── run.bat               # spúšťač hotového .exe (koreň projektu alebo dist\)
├── build_windows.bat     # inštalácia závislostí + PyInstaller build + kópia .exe do koreňa
├── CursorKeep.spec       # PyInstaller spec: onefile, console=False, collect_all pystray + PIL
├── CursorKeep.ico        # ikona zabaleného .exe
├── requirements.txt      # pyautogui, keyboard, pystray, pillow
├── .gitignore            # ignoruje build/, dist/, *.exe, cursorkeep_config.json, cursorkeep.log
├── LICENSE               # MIT License, Copyright (c) 2026 Apoliak7777
├── README.md             # tento súbor (slovenská verzia)
└── README.en.md          # anglická verzia
```

Súbory vytvárané za behu (nie sú v repozitári, sú v `.gitignore`):

| Súbor | Umiestnenie | Význam |
|-------|-------------|--------|
| `cursorkeep_config.json` | vedľa `.exe` alebo `.py` | uložené nastavenia; číta sa s kódovaním `utf-8-sig` (odolné voči BOM) |
| `cursorkeep.log` | vedľa `.exe` alebo `.py` | debug log; vzniká len pri chybách (napr. zlyhanie tray alebo hotkey) |

---

## ⌨️ Klávesové skratky a ovládanie

| Akcia | Ako |
|-------|-----|
| Zapnúť / vypnúť | Vlastný hotkey nastavený v GUI (predvolene žiadny) |
| Núdzové zastavenie | `Ctrl + Shift + Q` — registruje sa pri spustení pohybu a odregistruje pri zastavení (nie počas celého behu aplikácie) |
| Automatické zastavenie | Pohyb myšou nad 15 px v dvoch kontrolách za sebou |
| PyAutoGUI FailSafe | Presun kurzora do rohu obrazovky vyvolá `FailSafeException` a slučka sa ukončí |
| Zrušiť zachytávanie hotkey | `Esc` počas režimu „Stlač tlačidlo…" |
| Schovať okno | Tlačidlo `Skryť` alebo zatvorenie okna (pri bežiacom programe sa spýta: skryť / ukončiť) |
| Tray menu | `Zobraziť okno` · `▶ Spustiť` / `⏹ Zastaviť` · `Ukončiť` |

> [!WARNING]
> Zachytávanie vlastného hotkey ukladá **jednu klávesu** (`event.name`), nie kombináciu. Vyber si klávesu, ktorú bežne nepoužívaš — napríklad `f9` alebo `scroll lock`. Hotkey sa registruje so `suppress=True`, takže sa nedostane do ostatných aplikácií.

---

## ⚙️ Konfigurácia

Nastavenia sa ukladajú do `cursorkeep_config.json` v priečinku aplikácie. Neznáme kľúče sa pri načítaní ignorujú, hodnoty sa vždy zoseknú do platného rozsahu.

| Kľúč | Predvolené | Platný rozsah (po clamp) | Rozsah v GUI | Popis |
|------|-----------|--------------------------|--------------|-------|
| `min_interval` | `6` | 5 – 300 s | Spinbox 8 – 180 | Minimálna pauza medzi veľkými presunmi |
| `max_interval` | `18` | 10 – 600 s | Spinbox 15 – 300 | Maximálna pauza; ak je menšia alebo rovná min, prepočíta sa na `min + 10` |
| `safe_zone_percent` | `18` | 3 – 35 % | Posuvník 5 – 28 % | Okraj obrazovky, do ktorého veľké presuny nezachádzajú |
| `enable_jiggle` | `true` | `true` / `false` | Checkbox | Drobné pohyby (1 – 4 px) počas čakacej fázy |
| `run_at_startup` | `false` | `true` / `false` | Checkbox | Zápis / zmazanie hodnoty `CursorKeep` v registri Run |
| `start_minimized` | `true` | `true` / `false` | Checkbox | Pri štarte rovno schovať do tray (neplatí pri prvom spustení) |
| `toggle_hotkey` | `null` | názov klávesy | Tlačidlo Hotkey | Klávesa na prepínanie zapni/vypni |

Príklad súboru:

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
> Skutočná pauza sa počíta ako `random.uniform(min_interval, min(max_interval, 18))` — reálne čakanie preto nikdy nepresiahne 18 sekúnd, aj keď v konfigurácii nastavíš vyšší `max_interval`. Je to zámer: kurzor sa musí pohnúť do 20 sekúnd.

---

## 🧠 Ako funguje pohyb myši

| Fáza | Čo sa deje |
|------|-----------|
| **Výber cieľa** | Vygeneruje sa 12 náhodných bodov vnútri bezpečnej zóny. Každý dostane skóre: bonus za smer odlišný od predchádzajúceho pohybu (záporný dot product × 80), bonus za „príjemnú" vzdialenosť (najvyšší pre 80 – 350 px) a náhodný šum ±10. |
| **Jemné rozhodenie** | S pravdepodobnosťou 15 % sa cieľ ešte posunie o ±40 px vodorovne a ±30 px zvislo. |
| **Presun** | Náhodne sa zvolí jeden zo 4 štýlov a jedna zo 4 tween funkcií; celkové trvanie 0,5 – 2,1 s. |
| **Mikro-korekcia** | S pravdepodobnosťou 8 % nasleduje krátky „preklep" o ±5 px vodorovne a ±4 px zvislo a návrat späť. |
| **Grace perióda** | Pred presunom sa nastaví ochranné okno 3,5 s a po ňom ešte 1,8 s, počas ktorých monitor aktivity ignoruje rozdiel pozícií — inak by vlastný pohyb skriptu vyhodnotil ako zásah používateľa. |
| **Čakanie** | Slučka spí po náhodných úsekoch 0,7 – 2,2 s, aby vedela rýchlo zareagovať na zastavenie; medzitým prípadne vykoná jiggle. |
| **Monitorovanie** | Nezávislé vlákno každých 0,32 s porovnáva reálnu pozíciu kurzora s poslednou pozíciou nastavenou skriptom. |

---

## 🧩 Použité knižnice

| Knižnica | Povinná | Na čo slúži |
|----------|---------|-------------|
| `pyautogui` | ✅ áno | Presuny kurzora, easing funkcie, `FAILSAFE`, zistenie pozície |
| `keyboard` | ✅ áno | Globálne hotkeys (`Ctrl+Shift+Q`, vlastný toggle) a zachytávanie klávesy |
| `pystray` | ⚪ voliteľná | Ikona a menu v systémovej lište |
| `pillow` | ⚪ voliteľná | Vykreslenie tray ikony za behu (`Image`, `ImageDraw`) |
| `tkinter` | ✅ áno | GUI — súčasť štandardnej inštalácie Pythonu |
| `winreg`, `ctypes` | ✅ áno | Autostart v registri, rozmery primárneho monitora — štandardná knižnica Windows |

Ak chýbajú `pyautogui` alebo `keyboard`, program vypíše chybu a inštalačný príkaz a skončí. Ak chýba len `pystray` alebo `pillow`, program beží ďalej — len bez tray ikony (okno sa namiesto skrytia minimalizuje).

---

## ⚠️ Upozornenia a obmedzenia

> [!WARNING]
> **Len Windows.** Import `winreg` a volanie `user32.GetSystemMetrics` sú viazané na Windows. Na Linuxe a macOS aplikácia nefunguje.

- 🖥️ **Iba primárny monitor** — cieľové body sa počítajú z `SM_CXSCREEN` / `SM_CYSCREEN`, teda z rozmerov primárnej obrazovky, nie z celého virtuálneho desktopu.
- 🔐 **Globálne hotkeys môžu vyžadovať vyššie oprávnenia** — knižnica `keyboard` pracuje s nízkoúrovňovými hookmi; ak sa registrácia nepodarí, zapíše sa to do `cursorkeep.log` a aplikácia beží ďalej bez skratky.
- 🛑 **Antivírus a EDR** — zabalený `.exe` bez konzoly, ktorý simuluje vstup myši a zapisuje do registra pri štarte, môže byť vyhodnotený ako podozrivý. To je pri tomto type nástroja bežné.
- 🏢 **Firemné pravidlá** — obchádzanie časovača nečinnosti alebo zámku obrazovky môže porušovať IT politiku tvojej organizácie. Zodpovednosť za použitie je na tebe.
- 🚫 **Nevypína uzamknutie obrazovky** — po zamknutí Windows (`Win+L`) pohyby kurzora nepomôžu.
- ⏸️ **Po auto-zastavení treba spustiť znovu** — keď program zistí zásah používateľa, ukončí monitorovacie vlákno, zobrazí okno a hlášku; ďalší beh je nutné spustiť tlačidlom alebo hotkey.
- 🔄 **Rebuild po zmene kódu** — `run.bat` spúšťa hotový `.exe`, nie `cursorkeep.py`. Zmeny v zdrojovom kóde sa prejavia až po opätovnom builde alebo pri spustení cez `python cursorkeep.py`.

---

## 📄 Licencia

Projekt je uvoľnený pod **MIT License**, Copyright (c) 2026 Apoliak7777. Plné znenie nájdeš v súbore [LICENSE](LICENSE).

---

<div align="center">

Vytvoril **Alex Poliak** - [GitHub](https://github.com/Apoliak7777) - [alexpoliak21@gmail.com](mailto:alexpoliak21@gmail.com)

</div>
