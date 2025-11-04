# Projekt-Zusammenfassung: Hydraulic Systems Data Preparation

**Modul:** Data Preparation  
**Level:** Einsteiger  
**Datum:** November 2025

---

## 📋 Aufgabenstellung & Umsetzung

### 1. Datensatz aussuchen ✓

**Gewählt:** UCI Hydraulic Systems Dataset

**Warum dieser Datensatz?**
- Realistische Industriedaten (Condition Monitoring)
- Gut dokumentiert
- Interessante Challenge: 43.680 Spalten (Zeitreihen)
- Mehrere Zielvariablen → vielseitig für Analysen
- Keine Missing Values → Fokus auf Feature Engineering statt Datenbereinigung

**Quelle:** [UCI Machine Learning Repository](https://archive.ics.uci.edu/ml/datasets/Condition+monitoring+of+hydraulic+systems)

---

### 2. Datensatz beschreiben ✓

**Was wurde gemessen?**
- **2.205 Messzyklen** à 60 Sekunden auf einem Hydraulik-Teststand
- **17 Sensoren** mit unterschiedlichen Sampling-Raten:
  - Drucksensoren (PS1-PS6): 100 Hz → 6.000 Messpunkte/Zyklus
  - Durchflusssensoren (FS1-FS2): 10 Hz → 600 Messpunkte/Zyklus
  - Temperatursensoren (TS1-TS4): 1 Hz → 60 Messpunkte/Zyklus
  - Weitere: Vibration (VS1), Motor-Power (EPS1), Effizienz-Sensoren (CE, CP, SE)

**Problem:** 
- Rohdaten = 2.205 Zeilen × 43.680 Spalten
- Viel zu viele Features für sinnvolle Analysen!

**Lösung:**
- Feature Engineering: Zeitreihen aggregieren
- Statt 43.680 Zeitpunkte → 136 aussagekräftige Features

📄 **Siehe:** `README.md` (Abschnitt "Was ist das hier?" & "Der Datensatz")

---

### 3. Typos bereinigen ✓

**Vorgehen:**
```python
df_numeric = df.apply(pd.to_numeric, errors='coerce')
```

**Was passiert:**
- Alle nicht-numerischen Werte werden zu `NaN` konvertiert
- Typos (z.B. falsche Zeichen, Buchstaben) werden automatisch erkannt

**Ergebnis:**
- Laut Datenquelle: **Keine Missing Values** im Datensatz
- Auch nach Typo-Bereinigung: **0% Missing Values** ✓
- Datensatz ist sauber!

📄 **Siehe:** `prep_corrected.py` (Zeile 44-45 in `extract_features()`)

**Output:**
- `out/feature_stats.csv` → Spalte `pct_missing` zeigt 0.0 für alle Features

---

### 4. Missing Value Handling ✓

**Strategie:**

Da der Datensatz **keine Missing Values** hat, brauchten wir keine komplexe Strategie!

**Trotzdem vorbereitet (falls doch welche auftauchen):**
- Automatische Konvertierung via `pd.to_numeric(errors='coerce')`
- Check in Statistiken: `n_missing` und `pct_missing`

**Entscheidung:**
- Keine Imputation nötig
- Keine Spalten droppen nötig
- Einfacher Check: ✓ bestanden

📄 **Siehe:** `out/feature_stats.csv` → Alle Features zeigen `pct_missing = 0.0`

---

### 5. Werte je Attribut prüfen ✓

**Durchgeführte Analysen:**

#### a) **Deskriptive Statistiken** (min/max, mean, median, std)

**Beispiel: Cooling Efficiency (CE) - Mean-Feature**
```
mean:   31.30  (typischer Wert)
std:    11.58  (moderate Schwankung)
min:    17.56  (niedrigster Durchschnitt)
max:    47.90  (höchster Durchschnitt)
median: 27.39  (Median niedriger als Mean → rechtsschiefe Verteilung)
```

**Beispiel: Pressure Sensor 1 (PS1) - Mean-Feature**
```
mean:   153.23 bar
std:    8.33   (geringe Schwankung → stabiler Sensor)
min:    100.79 bar
max:    166.06 bar
```

📄 **Output:** `out/feature_stats.csv` (vollständige Statistiken für alle 136 Features)

---

#### b) **Korrelationsanalyse**

**Top-Korrelationen gefunden:**
- `ps1_mean` ↔ `ps2_mean`: r ≈ 0.99 (sehr hohe Korrelation)
- `ts1_mean` ↔ `ts2_mean`: r ≈ 0.95 (Temperatursensoren messen ähnlich)
- `ce_*` Features untereinander: r > 0.99 (mean, median, max sehr ähnlich)

**Bedeutung:**
- Viele Sensoren messen redundante Informationen
- Für ML-Modelle: Feature Selection sinnvoll (z.B. nur PS1 statt PS1-PS6)
- Für Einsteiger-Analyse: ok so!

📄 **Output:** 
- `out/correlation.csv` (136×136 Korrelationsmatrix)
- `out/correlation_heatmap.png` (Visualisierung)

---

#### c) **Feature Importance** (Mutual Information)

**Top 5 Features für Vorhersage von `cooler_condition`:**

1. `ce_max` — 1.093 (Maximale Kühleffizienz)
2. `ce_q75` — 1.093 (75%-Quantil Kühleffizienz)
3. `ce_median` — 1.089 (Median Kühleffizienz)
4. `ce_mean` — 1.089 (Durchschnitt Kühleffizienz)
5. `ce_min` — 1.088 (Minimale Kühleffizienz)

**Erkenntnis:**
- **Cooling Efficiency (CE)** ist DAS wichtigste Feature!
- Macht Sinn: Defekter Kühler → Kühleffizienz sinkt direkt

📄 **Output:** `out/mutual_information.csv`

---

#### d) **Verteilungen**

**Visualisiert:** Histogramme der Mean-Features

**Erkenntnisse:**
- Meiste Features zeigen **annähernde Normalverteilung**
- Einige bi-modale Verteilungen (z.B. CE → 2 Cluster: defekte vs. funktionierende Kühler)
- Keine extremen Ausreißer

📄 **Output:** `out/feature_distributions.png`

---

#### e) **Boxplots nach Zielvariable**

**Beispiel: TS1 Mean nach Cooler Condition**
- Kühler bei 100% (optimal) → niedrigere Temperatur
- Kühler bei 3% (defekt) → höhere Temperatur
- Klare Trennung der Gruppen ✓

📄 **Output:** `out/boxplots_by_target.png`

---

### 6. Feature Engineering ✓

**Problem:** 43.680 Spalten sind nicht handhabbar!

**Ansatz:** Zeitreihen-Aggregation pro Sensor

**Die 8 gewählten Features:**

| Feature | Bedeutung | Warum wichtig? |
|---------|-----------|----------------|
| `mean` | Durchschnitt | Typischer Wert im Zyklus |
| `median` | Median | Robust gegen Ausreißer |
| `std` | Standardabweichung | Wie stark schwankt der Sensor? |
| `min` | Minimum | Niedrigster Wert |
| `max` | Maximum | Höchster Wert |
| `q25` | 25%-Quantil | Unteres Quartil |
| `q75` | 75%-Quantil | Oberes Quartil |
| `range` | Spannweite (max - min) | Bandbreite |

**Ergebnis:**
- 17 Sensoren × 8 Features = **136 Features**
- Von 43.680 → 136 = **99,7% Reduktion** 🎉
- Behält trotzdem wichtige Informationen bei!

**Begründung:**
- **Lage-Maße** (mean, median): Wo liegt der Sensor typischerweise?
- **Streuungs-Maße** (std, range, Quartile): Wie variabel ist er?
- **Extremwerte** (min, max): Gibt es Spitzen?

📄 **Code:** `prep_corrected.py` → Funktion `extract_features()`

---

## 📊 Finale Outputs

### Generierte Dateien (in `out/`):

1. **`features_complete.csv`** (2.205 × 141)
   - Hauptdatensatz: 136 Features + 5 Zielvariablen

2. **`feature_stats.csv`**
   - Deskriptive Statistiken: count, mean, std, min, max, Quartile, Missing%

3. **`correlation.csv`** + `correlation_heatmap.png`
   - Korrelationsmatrix (136×136)
   - Visualisierung

4. **`mutual_information.csv`**
   - Feature Importance für Cooler Condition

5. **`feature_distributions.png`**
   - Histogramme der Mean-Features

6. **`boxplots_by_target.png`**
   - Feature-Verteilungen nach Cooler Condition

---

## 🎯 Zusammenfassung der Ergebnisse

### Datenqualität: ⭐⭐⭐⭐⭐
- Keine Missing Values
- Keine Typos
- Saubere Zeitreihen
- Gut dokumentiert

### Feature Engineering: ⭐⭐⭐⭐⭐
- 99,7% Dimensionsreduktion
- Behält wichtige Informationen
- Interpretierbare Features

### Analysen: ⭐⭐⭐⭐⭐
- Klare Korrelationen identifiziert
- Feature Importance berechnet
- Verteilungen visualisiert
- Zusammenhänge mit Zielvariablen erkennbar

---

## 💡 Key Insights

1. **Cooling Efficiency (CE)** ist der wichtigste Sensor für Kühler-Diagnose
2. Viele Sensoren messen redundante Informationen (hohe Korrelation)
3. Features zeigen gute Normalverteilungen → gut für ML
4. Klare Trennung zwischen Zustandsklassen (z.B. defekt vs. optimal)
5. Datensatz ist sehr sauber → perfekt für Einsteiger-Analysen

---

## 🚀 Nächste Schritte (optional, für ML-Projekte)

- Feature Selection: Redundante Features entfernen
- Klassifikation: Random Forest, SVM für Zustandsvorhersage
- Anomalie-Erkennung: Ungewöhnliche Zyklen finden
- Time Series Analysis: Degradation über Zeit

**Aber:** Für Data Preparation Modul → **Fertig!** ✓

---

**Bearbeitet von:** Christian Münzinger  
**Datum:** 04.11.2025  
**Tools:** Python, pandas, matplotlib, seaborn, scikit-learn
