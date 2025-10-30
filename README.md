# Hydraulic Systems - Data Preparation

## 📊 Projekt-Übersicht

Datenaufbereitung und Exploration des **UCI Hydraulic Systems Dataset** für Condition Monitoring.

---

## 🚨 WICHTIG: Datenstruktur-Korrektur

### ❌ Falsche Interpretation (ursprünglich):
- Alle 43.680 Zeitpunkte als separate Features behandelt
- → 43.680 Spalten → ~1,9 Milliarden Paarvergleiche für Korrelation
- → Nicht praktikabel!

### ✅ Korrekte Interpretation:
Die Rohdaten sind **Zeitreihen**:
- **Zeilen** = Zyklen (2.205 Messzyklen à 60 Sekunden)
- **Spalten** = Zeitpunkte innerhalb eines Zyklus

**Sensor-Sampling-Raten:**
| Sensor | Einheit | Sampling | Spalten |
|--------|---------|----------|---------|
| PS1-PS6 | bar | 100 Hz | 6.000 |
| EPS1 | W | 100 Hz | 6.000 |
| FS1-FS2 | l/min | 10 Hz | 600 |
| TS1-TS4 | °C | 1 Hz | 60 |
| VS1 | mm/s | 1 Hz | 60 |
| CE, CP, SE | %, kW, % | 1 Hz | 60 |

---

## 🎯 Lösung: Feature Engineering

Statt alle Zeitpunkte zu nutzen, extrahieren wir **aggregierte Features** pro Zyklus:

**8 Features pro Sensor:**
- `mean` - Durchschnitt
- `std` - Standardabweichung (Variabilität)
- `min` - Minimum
- `max` - Maximum
- `median` - Median
- `q25` - 25%-Quantil
- `q75` - 75%-Quantil
- `range` - Spannweite (max - min)

**Ergebnis:**
- 17 Sensoren × 8 Features = **136 Features**
- 5 Zielvariablen
- **141 Spalten gesamt** (statt 43.680!)

---

## 📁 Ordnerstruktur

```
HydraulicSystems/
├── data/              # Rohdaten (17 .txt-Dateien)
│   ├── CE.txt         # Cooling efficiency (1 Hz, 60 Spalten)
│   ├── PS1.txt        # Pressure Sensor 1 (100 Hz, 6000 Spalten)
│   └── ...
├── docs/              # Dokumentation
│   ├── description.txt
│   ├── documentation.txt
│   └── profile.txt    # Zielvariablen (5 Spalten)
├── out/               # Exportierte Ergebnisse
│   ├── features_complete.parquet  ⭐ HAUPTDATEI
│   ├── features_complete.csv
│   ├── feature_stats.csv
│   ├── correlation.csv
│   ├── correlation_heatmap.png
│   ├── mutual_information.csv
│   ├── feature_distributions.png
│   └── boxplots_by_target.png
├── notebooks/
│   └── 01_data_exploration.ipynb  # Interaktive Exploration
├── prep_corrected.py  ⭐ KORRIGIERTES SKRIPT
├── prep.py            # (alt - nicht verwenden!)
└── requirements.txt
```

---

## 🚀 Schnellstart

### 1. Installation
```powershell
pip install -r requirements.txt
```

### 2. Datenaufbereitung ausführen
```powershell
python prep_corrected.py
```

**Laufzeit:** ~5-10 Sekunden ✅ (statt 1+ Stunde ❌)

### 3. Interaktive Exploration
Öffne `notebooks/01_data_exploration.ipynb` in Jupyter/VS Code

---

## 📤 Ausgabe-Dateien

### Hauptdatensatz
- **`features_complete.parquet`** - Kompakt, schnell (empfohlen)
- **`features_complete.csv`** - Lesbar, größer

**Struktur:**
- 2.205 Zeilen (Zyklen)
- 136 Feature-Spalten
- 5 Zielvariablen-Spalten

### Analysen
- **`feature_stats.csv`** - Deskriptive Statistiken (count, mean, std, min, max, missing%)
- **`correlation.csv`** - Pearson-Korrelationsmatrix (136×136)
- **`correlation_heatmap.png`** - Visualisierung
- **`mutual_information.csv`** - Feature Importance für `cooler_condition`

### Visualisierungen
- **`feature_distributions.png`** - Histogramme der Mean-Features
- **`boxplots_by_target.png`** - Feature-Verteilungen nach Cooler Condition

---

## 🎯 Zielvariablen (aus profile.txt)

| Variable | Werte | Bedeutung |
|----------|-------|-----------|
| **cooler_condition** | 3, 20, 100 | Kühler-Zustand (3=defekt, 100=optimal) |
| **valve_condition** | 73, 80, 90, 100 | Ventil-Zustand |
| **pump_leakage** | 0, 1, 2 | Pumpen-Leckage-Level |
| **accumulator_pressure** | 90, 100, 115, 130 | Akkumulator-Druck (bar) |
| **stable_flag** | 0, 1 | Stabilitäts-Flag |

---

## 🔍 Top Feature Importance

**Mutual Information für `cooler_condition`:**

1. `ce_max` - 1.093
2. `ce_q75` - 1.093
3. `ce_median` - 1.089
4. `ce_mean` - 1.089
5. `ce_min` - 1.088

→ **Cooling Efficiency (CE)** ist das wichtigste Feature für Kühler-Zustand!

---

## 📊 Nächste Schritte

### Für Modellierung:
```python
import pandas as pd

# Lade Daten
df = pd.read_parquet('out/features_complete.parquet')

# Features & Targets trennen
features = df.drop(columns=['cooler_condition', 'valve_condition', 
                             'pump_leakage', 'accumulator_pressure', 'stable_flag'])
target = df['cooler_condition']  # Oder andere Zielvariable

# → Machine Learning (Klassifikation/Regression)
```

### Mögliche Analysen:
- ✅ **Klassifikation:** Vorhersage von Fehlertypen
- ✅ **Anomalie-Erkennung:** Ungewöhnliche Zyklus-Muster
- ✅ **Feature Selection:** Wichtigste Sensoren identifizieren
- ✅ **Time Series Analysis:** Trend-Erkennung über Zyklen

---

## 📝 Technische Details

### Dependencies
```
pandas
numpy
matplotlib
seaborn
scikit-learn
pyarrow
```

### Performance
- **Alte Version:** 43.680 Features → ~1h für Korrelation
- **Neue Version:** 136 Features → ~5 Sekunden ✅

---

## ✅ Akzeptanzkriterien (erfüllt)

- ✅ `out/features_complete.parquet` existiert (2.205 × 141)
- ✅ `out/feature_stats.csv` existiert
- ✅ `out/correlation.csv` + Heatmap PNG existieren
- ✅ `out/mutual_information.csv` existiert
- ✅ Notebook `01_data_exploration.ipynb` läuft fehlerfrei
- ✅ Laufzeit < 1 Minute

---

## 📚 Referenzen

- **Dataset:** [UCI Machine Learning Repository - Condition monitoring of hydraulic systems](https://archive.ics.uci.edu/ml/datasets/Condition+monitoring+of+hydraulic+systems)
- **Paper:** Schneider et al., "Investigate Sensor Data of Hydraulic Test Rig"

---

**Erstellt:** Oktober 2025  
**Version:** 2.0 (Korrigiert)
