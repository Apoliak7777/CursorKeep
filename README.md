# 🖱️ CursorKeep

**Moderný a inteligentný nástroj na plynulé hýbanie myšou na Windows**

CursorKeep udržiava tvoj počítač aktívne pomocou **nenápadných, plynulých pohybov kurzora**. Je navrhnutý tak, aby bol maximálne diskrétny a užívateľsky prívetivý.

## ✨ Funkcie

- Vlastný nastaviteľný hotkey na toggle (zapni/vypni)
- Prvý štart vždy ukáže okno (pre jednoduchý setup)
- Väčšie a prehľadné GUI
- Systémová lišta (tray) – plne skryteľné okno
- Spustenie pri štarte Windows
- Nastavenia v GUI (intervaly, bezpečná zóna, jiggle)
- Prirodzené pohyby (rôzne štýly a smery)
- Automatické zastavenie pri dotyku myši
- Ochrana pred falošnou detekciou pohybu

## 📥 Stiahnutie (najjednoduchšie)

1. Choď na **[Releases](https://github.com/Apoliak7777/CursorKeep/releases)**
2. Stiahni najnovší CursorKeep.exe
3. Spusti ho – hotovo!

Žiadny Python, žiadny build. Len spusti exe.

## 🛠️ Build zo zdrojov

`ash
pip install -r requirements.txt
pyinstaller --clean --noconfirm CursorKeep.spec
`

Výsledok nájdeš v dist/CursorKeep.exe.

## ⚙️ Použitie

- Prvýkrát sa otvorí okno.
- Nastav si vlastný hotkey (klikni na "Custom toggle hotkey").
- Klikni **Spustiť**.
- Skry okno do tray.

**Ovládanie:**
- Vlastný hotkey = toggle
- Ctrl + Shift + Q = núdzové zastavenie
- Dotyk myšou = automatické zastavenie

## 📄 Licencia

MIT License – pozri LICENSE súbor.

## 🔗 Odkazy

- GitHub: https://github.com/Apoliak7777/CursorKeep

Vytvorené pre pohodlie pri práci.