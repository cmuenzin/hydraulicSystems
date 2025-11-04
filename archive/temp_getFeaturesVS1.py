"""
Quick script to extract 8 features from the first row of VS1.txt
Demonstrates feature engineering on a single time-series.
"""

import numpy as np
from pathlib import Path

# Pfade
DATA_DIR = Path('data')
vs1_file = DATA_DIR / 'VS1.txt'

# Erste Zeile laden
with open(vs1_file, 'r') as f:
    first_row = f.readline().strip()

# In Zahlenwerte konvertieren (tab-getrennt)
values = np.array([float(x) for x in first_row.split('\t')])

print("=" * 70)
print("VS1 - ERSTE ZEILE (VIBRATIONSSENSOR)")
print("=" * 70)
print(f"Anzahl Messpunkte: {len(values)}")
print(f"Erste 10 Werte: {values[:10]}\n")

# Die 8 Features berechnen
features = {
    'mean': np.mean(values),
    'median': np.median(values),
    'std': np.std(values),
    'min': np.min(values),
    'max': np.max(values),
    'q25': np.percentile(values, 25),
    'q75': np.percentile(values, 75),
    'range': np.max(values) - np.min(values),
}

# Ausgabe
print("FEATURES FÜR ZYKLUS 1:")
print("-" * 70)
for feature_name, value in features.items():
    print(f"vs1_{feature_name:6s} = {value:10.4f}")

print("\n" + "=" * 70)
print("INTERPRETATION")
print("=" * 70)
print(f"Typischer Wert:        {features['mean']:.4f} mm/s")
print(f"Stabilität (Std Dev):  {features['std']:.4f} (niedrig = stabil)")
print(f"Schwankungsbereich:    {features['min']:.4f} bis {features['max']:.4f} mm/s")
print(f"Spannweite:            {features['range']:.4f} mm/s")