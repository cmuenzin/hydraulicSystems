# Hydraulic Systems - Data Preparation

## � Was ist das hier?

Dieses Projekt bereitet den **UCI Hydraulic Systems Dataset** auf — ein Datensatz mit Sensor-Messungen von einem Hydraulik-Teststand.

**Die Challenge:** Die Rohdaten haben **43.680 Spalten**. Ja, richtig gelesen! 🤯

Das ist viel zu viel für sinnvolle Analysen. Deshalb machen wir hier **Feature Engineering** und reduzieren die Daten auf überschaubare **136 Features**.

---

## 🔍 Der Datensatz

### Was wurde gemessen?

Ein Hydraulik-Teststand wurde **2.205 mal** für jeweils **60 Sekunden** durchlaufen. 

Dabei wurden **17 Sensoren** ausgelesen:
- **Drucksensoren** (PS1-PS6): Druck in bar
- **Temperatursensoren** (TS1-TS4): Temperatur in °C  
- **Durchflusssensoren** (FS1-FS2): Volumenstrom in l/min
- **Vibrationssensor** (VS1): Vibration in mm/s
- **Motor-Power** (EPS1): Leistung in Watt
- **Effizienz-Sensoren** (CE, CP, SE): Kühleffizienz, Kühlleistung, Effizienzfaktor

### Das Problem: Zeitreihen-Daten

Die Sensoren messen mit unterschiedlichen **Sampling-Raten**:

| Sensor | Rate | Messpunkte pro Zyklus |
|--------|------|---------------------|
| PS1-PS6, EPS1 | 100 Hz | 6.000 |
| FS1-FS2 | 10 Hz | 600 |
| TS1-TS4, VS1, CE, CP, SE | 1 Hz | 60 |

**Insgesamt:** 2.205 Zyklen × 43.680 Zeitpunkte = viel zu viele Spalten!

### Was wollen wir vorhersagen?

Der Datensatz enthält **5 Zielvariablen** (`docs/profile.txt`), die den Zustand der Hydraulik beschreiben:

1. **Kühler-Zustand** (cooler_condition):
   - 3 = kurz vorm Totalausfall
   - 20 = reduzierte Effizienz  
   - 100 = volle Effizienz

2. **Ventil-Zustand** (valve_condition):
   - 73-100% (optimal bis defekt)

3. **Pumpen-Leckage** (pump_leakage):
   - 0 = keine, 1 = schwach, 2 = stark

4. **Akkumulator-Druck** (accumulator_pressure):
   - 90-130 bar (defekt bis optimal)

5. **Stabilitäts-Flag** (stable_flag):
   - 0 = stabil, 1 = instabil

---

## � Unsere Lösung: Feature Engineering

Statt alle 43.680 Zeitpunkte einzeln zu analysieren, **aggregieren** wir die Zeitreihen pro Sensor:

### Die 8 Features pro Sensor:

| Feature | Beschreibung | Warum wichtig? |
|---------|--------------|----------------|
| `mean` | Durchschnitt | Typischer Wert während des Zyklus |
| `median` | Median | Robuster gegen Ausreißer |
| `std` | Standardabweichung | Wie stark schwankt der Sensor? |
| `min` | Minimum | Niedrigster Wert |
| `max` | Maximum | Höchster Wert |
| `q25` | 25%-Quantil | Unteres Quartil |
| `q75` | 75%-Quantil | Oberes Quartil |
| `range` | Spannweite (max - min) | Bandbreite der Werte |

**Ergebnis:**  
17 Sensoren × 8 Features = **136 Features** (statt 43.680!) 🎉

---

## 🚀 Installation & Ausführung

### 0. Daten herunterladen (falls noch nicht vorhanden)

Die Rohdaten sind **nicht** im Repo enthalten (zu groß). Lade sie hier herunter:

👉 [UCI Machine Learning Repository - Hydraulic Systems](https://archive.ics.uci.edu/ml/datasets/Condition+monitoring+of+hydraulic+systems)

Entpacke die ZIP und kopiere die `.txt`-Dateien in den `data/` Ordner:
```
data/
├── CE.txt
├── CP.txt
├── EPS1.txt
├── FS1.txt
├── FS2.txt
├── PS1.txt
├── PS2.txt
├── PS3.txt
├── PS4.txt
├── PS5.txt
├── PS6.txt
├── SE.txt
├── TS1.txt
├── TS2.txt
├── TS3.txt
├── TS4.txt
└── VS1.txt
```

Außerdem: `docs/profile.txt` (Zielvariablen) muss ebenfalls aus dem Download stammen.

### 1. Requirements installieren
```powershell
pip install -r requirements.txt
```

### 2. Datenaufbereitung starten
```powershell
python prep_corrected.py
```

**Laufzeit:** ~5-10 Sekunden

### 3. Ergebnisse ansehen
Die Outputs landen im `out/` Ordner:
- `features_complete.csv` — Der fertige Datensatz (2.205 × 141)
- `feature_stats.csv` — Statistiken (mean, std, min, max, ...)
- `correlation.csv` + `correlation_heatmap.png` — Korrelationen
- `mutual_information.csv` — Feature Importance
- Verschiedene Plots (Verteilungen, Boxplots)

---

## 📊 Was haben wir herausgefunden?

### 1. Datenqualität: Top! ✓
- **Keine Missing Values** im Datensatz
- Nur wenige Typos, die automatisch bereinigt wurden
- Alle 2.205 Zyklen komplett

### 2. Welche Features sind wichtig?

Die **Top 5 Features** für die Vorhersage des Kühler-Zustands (laut Mutual Information):

1. `ce_max` — Maximale Kühleffizienz (!)
2. `ce_q75` — 75%-Quantil der Kühleffizienz
3. `ce_median` — Median der Kühleffizienz
4. `ce_mean` — Durchschnittliche Kühleffizienz
5. `ce_min` — Minimale Kühleffizienz

**Erkenntnis:** Der **Cooling Efficiency Sensor (CE)** ist extrem wichtig für die Kühler-Diagnose! 

Das macht Sinn: Wenn der Kühler kaputt geht, sinkt die Kühleffizienz direkt. 💡

### 3. Korrelationen

Viele Features sind **stark korreliert** (z.B. `ps1_mean` mit `ps2_mean`):
- Macht Sinn: Die Drucksensoren messen ähnliche Phänomene
- Bedeutet: Wir könnten evtl. Features reduzieren (Feature Selection)
- Für erste Analysen ok, für ML später optimierbar

### 4. Verteilungen

Die meisten Features zeigen **Normalverteilung** oder zumindest symmetrische Verteilungen:
- Gut für viele ML-Algorithmen!
- Keine extremen Schiefe
- Ausreißer sind vorhanden, aber moderat

---

## 🎯 Nächste Schritte (für ML-Projekte)

Falls du später damit arbeiten willst:

1. **Feature Selection:** Reduziere redundante Features (Korrelation > 0.9)
2. **Modellierung:** Klassifikation der Zielvariablen (z.B. Random Forest, SVM)
3. **Cross-Validation:** Teste die Modelle robust
4. **Anomalie-Erkennung:** Finde ungewöhnliche Zyklen

Aber: **Für dieses Modul sind wir fertig!** ✓

---

## 📁 Repo-Struktur

```
HydraulicSystems/
├── data/                  # Rohdaten (17 .txt-Dateien)
├── docs/                  # Dokumentation + profile.txt (Zielvariablen)
├── notebooks/             # Jupyter Notebook für Exploration
├── out/                   # Generierte Outputs (CSVs, PNGs)
├── prep_corrected.py      # ⭐ DAS Hauptskript
├── archive_prep.py        # Alte Version (nur als Referenz)
└── requirements.txt
```

---

## 📚 Quellen

- **Dataset:** [UCI Machine Learning Repository](https://archive.ics.uci.edu/ml/datasets/Condition+monitoring+of+hydraulic+systems)
- **Paper:** Helwig et al., "Condition Monitoring of a Complex Hydraulic System Using Multivariate Statistics" (2015)

---

**Erstellt:** November 2025  
**Level:** Data Preparation (Einsteiger-Modul)  
**Ziel:** Zeitreihen → kompakte Features → sauberer Datensatz ✓

