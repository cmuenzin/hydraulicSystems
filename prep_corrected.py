"""
Hydraulic Systems - Data Preparation
=====================================
Feature Extraction aus Zeitreihen-Sensordaten

KONZEPT:
Die Rohdaten sind Zeitreihen mit 43.680 Spalten - viel zu viel!
Deshalb: Feature Engineering = Zeitreihen pro Sensor zusammenfassen

- Rohdaten: Zeilen = Zyklen (2205), Spalten = Zeitpunkte (bis zu 6000 pro Sensor)
- Output: 136 aggregierte Features (8 pro Sensor)
  
Warum diese 8 Features?
- mean/median: Typischer Wert während des Zyklus
- min/max: Extremwerte zeigen Spitzen/Täler
- std: Wie stark schwankt der Sensor?
- q25/q75/range: Streuung und Bandbreite
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict
from sklearn.feature_selection import mutual_info_classif


def extract_features(df: pd.DataFrame, sensor_name: str) -> pd.DataFrame:
    """
    Extrahiert 8 aggregierte Features aus Zeitreihen-DataFrame.
    
    Warum aggregieren? 
    - Ein Sensor liefert bis zu 6000 Werte pro Zyklus
    - Für Analysen/ML brauchen wir kompakte, aussagekräftige Features
    
    Die 8 Features beschreiben:
    - Lage: mean, median (typischer Wert)
    - Streuung: std (Variabilität), range (Spannweite)
    - Extrema: min, max (Ausschläge)
    - Verteilung: q25, q75 (Quartile)
    
    Args:
        df: DataFrame mit Zyklen (Zeilen) × Zeitpunkten (Spalten)
        sensor_name: Name des Sensors (z.B. 'ts1', 'ps2')
    
    Returns:
        DataFrame mit 8 Features pro Zyklus
    """
    features = pd.DataFrame()
    
    # Konvertiere zu numerisch (bereinigt automatisch Typos → NaN)
    df_numeric = df.apply(pd.to_numeric, errors='coerce')
    
    # Aggregationen über Zeitachse (axis=1 = über Spalten)
    features[f'{sensor_name}_mean'] = df_numeric.mean(axis=1)
    features[f'{sensor_name}_std'] = df_numeric.std(axis=1)
    features[f'{sensor_name}_min'] = df_numeric.min(axis=1)
    features[f'{sensor_name}_max'] = df_numeric.max(axis=1)
    features[f'{sensor_name}_median'] = df_numeric.median(axis=1)
    features[f'{sensor_name}_q25'] = df_numeric.quantile(0.25, axis=1)
    features[f'{sensor_name}_q75'] = df_numeric.quantile(0.75, axis=1)
    features[f'{sensor_name}_range'] = features[f'{sensor_name}_max'] - features[f'{sensor_name}_min']
    
    return features


def load_and_aggregate_sensors(data_path: str = "data") -> pd.DataFrame:
    """
    Lädt alle Sensor-Dateien und extrahiert aggregierte Features.
    
    Args:
        data_path: Pfad zum Datenordner
        
    Returns:
        DataFrame mit aggregierten Features
    """
    data_dir = Path(data_path)
    all_features = []
    
    print(f"[load_and_aggregate_sensors] Lade und aggregiere Sensordaten aus '{data_path}'...\n")
    
    # Nur echte Sensor-Dateien laden (keine Dokumentation)
    # Sensor-Namen: CE, CP, EPS1, FS1, FS2, PS1-6, SE, TS1-4, VS1
    sensor_names = ['ce', 'cp', 'eps1', 'fs1', 'fs2', 'ps1', 'ps2', 'ps3', 
                    'ps4', 'ps5', 'ps6', 'se', 'ts1', 'ts2', 'ts3', 'ts4', 'vs1']
    
    sensor_files = [data_dir / f"{name.upper()}.txt" for name in sensor_names]
    sensor_files = [f for f in sensor_files if f.exists()]
    sensor_files = sorted(sensor_files)
    
    for file_path in sensor_files:
        sensor_name = file_path.stem.lower()
        
        print(f"  Verarbeite {sensor_name}...", end=' ')
        
        # Lade Zeitreihen-Daten
        df = pd.read_csv(file_path, sep=r'\s+', header=None, engine='python')
        
        # Extrahiere Features
        features = extract_features(df, sensor_name)
        all_features.append(features)
        
        print(f"✓ ({df.shape[0]} Zyklen × {df.shape[1]} Zeitpunkte → {features.shape[1]} Features)")
    
    # Alle Features zusammenführen
    combined = pd.concat(all_features, axis=1)
    
    print(f"\n  → Gesamt: {combined.shape[0]} Zyklen × {combined.shape[1]} aggregierte Features\n")
    
    return combined


def load_targets(profile_path: str = "docs/profile.txt") -> pd.DataFrame:
    """
    Lädt Zielvariablen aus profile.txt.
    
    Args:
        profile_path: Pfad zu profile.txt
        
    Returns:
        DataFrame mit Zielvariablen
    """
    print(f"[load_targets] Lade Zielvariablen aus '{profile_path}'...")
    
    profile = pd.read_csv(profile_path, sep='\t', header=None)
    
    # Laut Dokumentation:
    profile.columns = ['cooler_condition', 'valve_condition', 'pump_leakage', 
                       'accumulator_pressure', 'stable_flag']
    
    print(f"  ✓ {profile.shape[0]} Zyklen × {profile.shape[1]} Zielvariablen")
    print(f"  Zielvariablen: {list(profile.columns)}\n")
    
    return profile


def compute_statistics(df: pd.DataFrame, feature_cols: list) -> pd.DataFrame:
    """
    Berechnet Basis-Statistiken für alle Features.
    
    Gibt uns Überblick über:
    - Verteilungen (mean, std, min, max, Quartile)
    - Datenqualität (Missing Values)
    
    Args:
        df: Kompletter DataFrame
        feature_cols: Liste der Feature-Spalten
        
    Returns:
        DataFrame mit Statistiken
    """
    print("[compute_statistics] Berechne Statistiken...")
    
    stats = df[feature_cols].describe().T
    stats['n_missing'] = df[feature_cols].isna().sum()
    stats['pct_missing'] = 100 * stats['n_missing'] / len(df)
    
    # Reorder columns für bessere Übersicht
    stats = stats[['count', 'n_missing', 'pct_missing', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']]
    
    stats.to_csv("out/feature_stats.csv")
    print(f"  ✓ Statistiken gespeichert: out/feature_stats.csv\n")
    
    return stats


def compute_correlation(df: pd.DataFrame, feature_cols: list) -> pd.DataFrame:
    """
    Berechnet Korrelationsmatrix und erstellt Heatmap.
    
    Warum Korrelation?
    - Zeigt uns redundante Features (hohe Korrelation = ähnliche Info)
    - Hilft beim Feature Selection
    - Erkennt Zusammenhänge zwischen Sensoren
    
    Args:
        df: Kompletter DataFrame
        feature_cols: Liste der Feature-Spalten
        
    Returns:
        Korrelationsmatrix
    """
    print("[compute_correlation] Berechne Korrelationsmatrix...")
    
    corr = df[feature_cols].corr()
    corr.to_csv("out/correlation.csv")
    print(f"  ✓ Korrelation gespeichert: out/correlation.csv")
    
    # Heatmap für visuelle Übersicht
    plt.figure(figsize=(20, 18))
    sns.heatmap(corr, cmap='coolwarm', center=0, square=True, 
                linewidths=0.1, cbar_kws={"shrink": 0.8})
    plt.title('Korrelations-Heatmap (Aggregierte Features)', fontsize=16, pad=20)
    plt.tight_layout()
    plt.savefig("out/correlation_heatmap.png", dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Heatmap gespeichert: out/correlation_heatmap.png\n")
    
    return corr


def compute_mutual_information(df: pd.DataFrame, feature_cols: list, 
                               target_col: str = 'cooler_condition') -> pd.DataFrame:
    """
    Berechnet Mutual Information für Features vs. Zielvariable.
    
    OPTIONAL: Für Einsteiger nicht zwingend notwendig!
    Mutual Information zeigt, welche Features am besten zur Vorhersage geeignet sind.
    
    Einfacher Alternative: Korrelation mit Target verwenden:
    df.corrwith(df['cooler_condition']).abs().sort_values(ascending=False)
    
    Args:
        df: Kompletter DataFrame
        feature_cols: Liste der Feature-Spalten
        target_col: Name der Zielspalte
        
    Returns:
        DataFrame mit MI-Scores
    """
    print(f"[compute_mutual_information] Berechne Mutual Information für '{target_col}'...")
    print("  (Optional: Dieser Schritt kann übersprungen werden)")
    
    X = df[feature_cols].fillna(0)
    y = df[target_col]
    
    # Mutual Information (für kategorische Zielvariable)
    mi_scores = mutual_info_classif(X, y, random_state=42)
    
    mi_df = pd.DataFrame({
        'feature': feature_cols,
        'mi_score': mi_scores
    }).sort_values('mi_score', ascending=False)
    
    mi_df.to_csv("out/mutual_information.csv", index=False)
    print(f"  ✓ MI-Scores gespeichert: out/mutual_information.csv")
    print(f"  → Top 5 Features:")
    for idx, row in mi_df.head(5).iterrows():
        print(f"     {row['feature']}: {row['mi_score']:.4f}")
    print()
    
    return mi_df


def create_visualizations(df: pd.DataFrame, feature_cols: list):
    """
    Erstellt grundlegende Visualisierungen.
    
    Args:
        df: Kompletter DataFrame
        feature_cols: Liste der Feature-Spalten
    """
    print("[create_visualizations] Erstelle Visualisierungen...")
    
    # 1. Mean-Features Verteilungen
    mean_features = [col for col in feature_cols if '_mean' in col][:16]
    
    fig, axes = plt.subplots(4, 4, figsize=(16, 12))
    axes = axes.flatten()
    
    for i, col in enumerate(mean_features):
        axes[i].hist(df[col].dropna(), bins=50, edgecolor='black', alpha=0.7)
        axes[i].set_title(col, fontsize=10)
        axes[i].set_xlabel('Wert')
        axes[i].set_ylabel('Häufigkeit')
        axes[i].grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig("out/feature_distributions.png", dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Verteilungen gespeichert: out/feature_distributions.png")
    
    # 2. Boxplots nach Cooler Condition
    if 'cooler_condition' in df.columns:
        features_to_plot = ['ts1_mean', 'ts2_mean', 'ps1_mean', 'ps2_mean']
        features_to_plot = [f for f in features_to_plot if f in df.columns][:4]
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        axes = axes.flatten()
        
        for i, feat in enumerate(features_to_plot):
            df.boxplot(column=feat, by='cooler_condition', ax=axes[i])
            axes[i].set_title(f'{feat} by Cooler Condition')
            axes[i].set_xlabel('Cooler Condition')
            axes[i].set_ylabel(feat)
        
        plt.suptitle('')
        plt.tight_layout()
        plt.savefig("out/boxplots_by_target.png", dpi=150, bbox_inches='tight')
        plt.close()
        print(f"  ✓ Boxplots gespeichert: out/boxplots_by_target.png")
    
    print()


def main():
    """
    Hauptfunktion: Führt komplette Datenaufbereitung durch.
    
    Ablauf:
    1. Rohdaten laden (17 Sensor-Dateien aus data/)
    2. Feature Engineering: Zeitreichen → 8 Features pro Sensor
    3. Zielvariablen laden (docs/profile.txt)
    4. Statistiken berechnen
    5. Korrelationsanalyse
    6. Mutual Information (optional)
    7. Visualisierungen
    8. Export nach out/
    """
    print("=" * 70)
    print("HYDRAULIC SYSTEMS - DATA PREPARATION")
    print("=" * 70)
    print("\nKonzept: Feature Engineering aus Zeitreihen")
    print("  • Problem: 43.680 Spalten (Rohdaten) sind zu viel!")
    print("  • Lösung: Aggregation → 136 Features (8 pro Sensor)")
    print("  • Vorteil: Kompakt, aussagekräftig, analysierbar\n")
    print("=" * 70 + "\n")
    
    # Erstelle Output-Verzeichnis falls nicht vorhanden
    Path('out').mkdir(exist_ok=True)
    
    # 1. Lade und aggregiere Sensordaten
    features_df = load_and_aggregate_sensors("data")
    
    # 2. Lade Zielvariablen
    targets_df = load_targets("docs/profile.txt")
    
    # 3. Zusammenführen
    print("[main] Führe Features und Targets zusammen...")
    df_complete = pd.concat([features_df.reset_index(drop=True), 
                            targets_df.reset_index(drop=True)], axis=1)
    print(f"  ✓ Kompletter Datensatz: {df_complete.shape}\n")
    
    # Feature-Spalten identifizieren
    feature_cols = [col for col in df_complete.columns if col not in targets_df.columns]
    
    # 4. Statistiken
    stats_df = compute_statistics(df_complete, feature_cols)
    
    # 5. Korrelation
    corr_df = compute_correlation(df_complete, feature_cols)
    
    # 6. Mutual Information
    mi_df = compute_mutual_information(df_complete, feature_cols, 'cooler_condition')
    
    # 7. Visualisierungen
    create_visualizations(df_complete, feature_cols)
    
    # 8. Export als CSV
    print("[main] Exportiere finalen Datensatz...")
    df_complete.to_csv("out/features_complete.csv", index=False)
    print(f"  ✓ Gespeichert: out/features_complete.csv ({df_complete.shape})\n")
    
    # Zusammenfassung
    print("=" * 70)
    print("✓ DATA PREPARATION ABGESCHLOSSEN")
    print("=" * 70)
    print("\nDatensatz:")
    print(f"  • {df_complete.shape[0]:,} Zyklen")
    print(f"  • {len(feature_cols):,} aggregierte Features")
    print(f"  • {len(targets_df.columns)} Zielvariablen")
    print("\nExportierte Dateien:")
    print("  • out/features_complete.csv (Hauptdatei)")
    print("  • out/feature_stats.csv")
    print("  • out/correlation.csv")
    print("  • out/correlation_heatmap.png")
    print("  • out/mutual_information.csv")
    print("  • out/feature_distributions.png")
    print("  • out/boxplots_by_target.png")
    print("\nZielvariablen:")
    for col in targets_df.columns:
        unique_vals = sorted(df_complete[col].unique())
        print(f"  • {col}: {unique_vals}")
    print()


if __name__ == "__main__":
    main()
