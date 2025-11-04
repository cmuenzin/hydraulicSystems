# Einfache Übersicht: Statistiken & Zielvariablen

## 🎯 Was sind die Zielvariablen?

Das sind die **5 Werte, die wir vorhersagen wollen** (aus `docs/profile.txt`):

### 1. **cooler_condition** (Kühler-Zustand)
- **Was:** Wie gut funktioniert der Kühler?
- **Werte:** 3, 20, 100
  - **100** = perfekt, volle Effizienz
  - **20** = reduzierte Effizienz
  - **3** = kurz vorm Totalausfall
- **Verteilung:** 741 Zyklen bei 100, 732 bei 20, 732 bei 3

### 2. **valve_condition** (Ventil-Zustand)
- **Was:** Wie gut schaltet das Ventil?
- **Werte:** 73, 80, 90, 100 (in %)
  - **100** = optimal
  - **73** = kurz vorm Totalausfall

### 3. **pump_leakage** (Pumpen-Leckage)
- **Was:** Wie stark leckt die Pumpe?
- **Werte:** 0, 1, 2
  - **0** = keine Leckage
  - **1** = schwach
  - **2** = stark

### 4. **accumulator_pressure** (Akkumulator-Druck)
- **Was:** Druck im Akkumulator
- **Werte:** 90, 100, 115, 130 (in bar)
  - **130** = optimal
  - **90** = kurz vorm Totalausfall

### 5. **stable_flag** (Stabilitätsflag)
- **Was:** War der Zyklus stabil?
- **Werte:** 0, 1
  - **0** = stabil
  - **1** = instabil (Messung evtl. noch nicht eingependelt)

---

## 📊 Statistiken für alle Features

> **Hinweis:** Wir haben **136 Features** aus 17 Sensoren (je 8 Features pro Sensor).  
> Hier eine Auswahl der wichtigsten:

### **Cooling Efficiency (CE)** — Kühleffizienz in %

| Feature | Mean | Std | Min | Max | Median | Interpretation |
|---------|------|-----|-----|-----|--------|----------------|
| ce_mean | 31.30 | 11.58 | 17.56 | 47.90 | 27.39 | Durchschnittliche Kühlleistung pro Zyklus |
| ce_std | 0.29 | 0.20 | 0.06 | 6.37 | 0.26 | Schwankung innerhalb eines Zyklus (niedrig = stabil) |
| ce_min | 30.79 | 11.58 | 17.04 | 47.63 | 26.86 | Niedrigster Wert pro Zyklus |
| ce_max | 31.88 | 11.60 | 18.14 | 48.78 | 27.98 | Höchster Wert pro Zyklus |

**→ CE ist DAS wichtigste Feature für Kühler-Diagnose!**

---

### **Cooling Power (CP)** — Kühlleistung in kW

| Feature | Mean | Std | Min | Max | Median | Interpretation |
|---------|------|-----|-----|-----|--------|----------------|
| cp_mean | 1.81 | 0.28 | 1.06 | 2.84 | 1.74 | Durchschnittliche Leistung |
| cp_std | 0.02 | 0.01 | 0.01 | 0.34 | 0.02 | Sehr stabil (geringe Schwankung) |
| cp_min | 1.77 | 0.28 | 1.02 | 2.77 | 1.70 | Minimale Leistung |
| cp_max | 1.86 | 0.28 | 1.11 | 2.91 | 1.79 | Maximale Leistung |

---

### **Pressure Sensors (PS1-PS6)** — Druck in bar

**Beispiel: PS1**

| Feature | Mean | Std | Min | Max | Median | Interpretation |
|---------|------|-----|-----|-----|--------|----------------|
| ps1_mean | 153.23 | 8.33 | 100.79 | 166.06 | 154.06 | Durchschnittsdruck sehr stabil |
| ps1_std | 9.51 | 4.39 | 2.73 | 41.38 | 8.83 | Geringe Schwankungen |
| ps1_min | 127.13 | 11.22 | 73.68 | 149.24 | 129.33 | Niedrigster Druck |
| ps1_max | 179.17 | 8.00 | 135.78 | 192.26 | 179.72 | Höchster Druck |

**→ PS1-PS6 sind stark korreliert (messen ähnliches)**

---

### **Temperature Sensors (TS1-TS4)** — Temperatur in °C

**Beispiel: TS1**

| Feature | Mean | Std | Min | Max | Median | Interpretation |
|---------|------|-----|-----|-----|--------|----------------|
| ts1_mean | 35.21 | 3.13 | 30.53 | 41.29 | 33.88 | Durchschnittstemperatur |
| ts1_std | 0.31 | 0.13 | 0.06 | 1.36 | 0.30 | Sehr stabil |
| ts1_min | 34.46 | 3.16 | 29.93 | 40.52 | 33.02 | Niedrigste Temperatur |
| ts1_max | 36.00 | 3.12 | 31.15 | 42.18 | 34.68 | Höchste Temperatur |

**→ Temperatur steigt wenn Kühler defekt!**

---

### **Flow Sensors (FS1-FS2)** — Volumenstrom in l/min

**Beispiel: FS1**

| Feature | Mean | Std | Min | Max | Median | Interpretation |
|---------|------|-----|-----|-----|--------|----------------|
| fs1_mean | 8.55 | 0.36 | 6.83 | 9.26 | 8.57 | Durchschnittlicher Durchfluss |
| fs1_std | 0.44 | 0.08 | 0.26 | 1.05 | 0.43 | Moderate Schwankung |
| fs1_min | 7.28 | 0.43 | 5.37 | 8.25 | 7.33 | Minimaler Durchfluss |
| fs1_max | 9.78 | 0.40 | 8.12 | 10.46 | 9.81 | Maximaler Durchfluss |

---

### **Motor Power (EPS1)** — Leistung in Watt

| Feature | Mean | Std | Min | Max | Median | Interpretation |
|---------|------|-----|-----|-----|--------|----------------|
| eps1_mean | 2495.51 | 73.84 | 2361.75 | 2740.64 | 2480.93 | Durchschnittsleistung Motor |
| eps1_std | 203.49 | 27.77 | 185.11 | 294.05 | 196.15 | Schwankung der Leistung |
| eps1_min | 2267.72 | 65.42 | 2097.80 | 2384.00 | 2260.00 | Niedrigste Leistung |
| eps1_max | 2900.79 | 49.65 | 2813.40 | 2995.20 | 2897.40 | Höchste Leistung |

---

### **Vibration (VS1)** — Vibration in mm/s

| Feature | Mean | Std | Min | Max | Median | Interpretation |
|---------|------|-----|-----|-----|--------|----------------|
| vs1_mean | 0.52 | 0.04 | 0.43 | 0.64 | 0.51 | Durchschnittliche Vibration |
| vs1_std | 0.01 | 0.00 | 0.00 | 0.02 | 0.01 | Sehr gering (stabil) |
| vs1_min | 0.51 | 0.04 | 0.42 | 0.63 | 0.50 | Minimale Vibration |
| vs1_max | 0.54 | 0.04 | 0.44 | 0.66 | 0.53 | Maximale Vibration |

---

### **Efficiency Factor (SE)** — Effizienzfaktor in %

| Feature | Mean | Std | Min | Max | Median | Interpretation |
|---------|------|-----|-----|-----|--------|----------------|
| se_mean | 16.80 | 1.01 | 12.91 | 18.73 | 17.02 | Durchschnittliche System-Effizienz |
| se_std | 0.21 | 0.09 | 0.06 | 1.18 | 0.20 | Geringe Schwankung |
| se_min | 16.35 | 1.04 | 12.42 | 18.27 | 16.58 | Niedrigste Effizienz |
| se_max | 17.26 | 1.01 | 13.47 | 19.30 | 17.47 | Höchste Effizienz |

---

## 🔗 Top-Korrelationen

**Welche Sensoren messen ähnliches?**

| Sensor 1 | Sensor 2 | Korrelation | Bedeutung |
|----------|----------|-------------|-----------|
| ps1_mean | ps2_mean | ≈ 0.99 | Drucksensoren messen fast identisch |
| ps1_mean | ps3_mean | ≈ 0.98 | Auch sehr ähnlich |
| ts1_mean | ts2_mean | ≈ 0.95 | Temperaturen korrelieren stark |
| ce_mean | ce_median | ≈ 0.99 | Mean & Median fast gleich (symmetrische Verteilung) |
| ce_mean | ce_max | ≈ 0.99 | Alle CE-Features sehr ähnlich |

**→ Viele Sensoren sind redundant! Für ML könnte man z.B. nur PS1 statt alle PS1-PS6 nehmen.**

---

## 💡 Einfache Interpretation

### Was bedeuten die Werte?

**Mean (Durchschnitt):**
- Der typische Wert während eines 60-Sekunden-Zyklus
- Beispiel: `ce_mean = 31.30` → Im Schnitt 31,3% Kühleffizienz

**Std (Standardabweichung):**
- Wie stark schwankt der Sensor?
- Hohe Std = instabil, niedrige Std = stabil
- Beispiel: `ce_std = 0.29` → sehr stabil!

**Min / Max:**
- Niedrigster / höchster Wert im Zyklus
- Zeigt Extremwerte und Spitzen

**Median:**
- Mittlerer Wert (50%-Marke)
- Robust gegen Ausreißer
- Wenn Median < Mean → rechtsschiefe Verteilung (wenige hohe Werte ziehen den Schnitt hoch)

---

## 🎯 Was ist jetzt wichtig für dich?

### Für die Analyse:
1. **Zielvariable wählen:** z.B. `cooler_condition` (am einfachsten)
2. **Wichtigste Features:** CE (Cooling Efficiency) ist top!
3. **Korrelationen beachten:** Viele Sensoren redundant

### Für ML (später):
- `cooler_condition` als Ziel → Klassifikation (3 Klassen: 3, 20, 100)
- Top-Features: CE, TS (Temperatur), evtl. PS (Druck)
- Rest kann man weglassen (zu ähnlich)

---

**Vollständige Statistiken:** `out/feature_stats.csv`  
**Korrelationen:** `out/correlation.csv` oder `correlation_heatmap.png`
