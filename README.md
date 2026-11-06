# Labor Elektrische Maschinen – Versuch 2: Drehstromtransformator

| Datei | Inhalt |
|---|---|
| `Versuch_2/main.tex` → `main.pdf` | Versuchsprotokoll (pdfLaTeX + BibTeX) |
| `Versuch_2/vorbereitung.tex` | Versuchsvorbereitende Aufgaben (wird in `main.tex` eingebunden) |
| `Versuch_2/auswertung.py` | Auswertung der CSV-Messdaten, erzeugt `abbildungen/*.pdf` und `abbildungen/kennwerte.txt` |
| `Versuch_2/Messdaten_05_11_26/` | Rohdaten der Messung vom 05.11.2026 |
| `Erklaerung/Erklaerung_Versuch2.tex` → `.pdf` | Erklärung des Versuchs auf Deutsch, Französisch und Arabisch (XeLaTeX) |

## Kompilieren

```bash
cd Versuch_2
python3 auswertung.py            # Abbildungen neu erzeugen (matplotlib, numpy)
pdflatex main && bibtex main && pdflatex main && pdflatex main

cd ../Erklaerung
xelatex Erklaerung_Versuch2 && xelatex Erklaerung_Versuch2   # benötigt Schrift "Amiri"
```
