"""
Hydraulic Systems - Data Preparation
=====================================
Einlesen, Zusammenführen und Bereinigen der UCI Hydraulic Systems Sensordaten.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, Tuple
from sklearn.feature_selection import mutual_info_classif, mutual_info_regression


def load_txt_folder(path: str = "data") -> Dict[str, pd.DataFrame]:
    """
    Lädt alle .txt-Dateien aus dem angegebenen Ordner.
    
    Args:
        path: Pfad zum Datenordner
        
    Returns:
        Dictionary mit Dateinamen (ohne .txt) als Keys und DataFrames als Values
    """
    data_path = Path(path)
    tables = {}
    total_typos = 0
    
    print(f"[load_txt_folder] Lade Dateien aus '{path}'...")
    
    for file_path in sorted(data_path.glob("*.txt")):
        filename = file_path.stem.lower()  # z.B. "ce", "ps1"
        
        # Einlesen ohne Header
        df = pd.read_csv(file_path, sep=r'\s+', header=None, engine='python')
        
        # Spaltennamen vergeben
        if df.shape[1] == 1:
            df.columns = [filename]
        else:
            df.columns = [f"{filename}_{i}" for i in range(df.shape[1])]
        
        # Nicht-numerische Werte zu NaN konvertieren und zählen
        for col in df.columns:
            original = df[col].copy()
            df[col] = pd.to_numeric(df[col], errors='coerce')
            typos = original.notna().sum() - df[col].notna().sum()
            if typos > 0:
                total_typos += typos
                print(f"  └─ {col}: {typos} nicht-numerische Werte zu NaN konvertiert")
        
        tables[filename] = df
        print(f"  ✓ {filename}: {df.shape[0]} Zeilen × {df.shape[1]} Spalten")
    
    print(f"\n[load_txt_folder] {len(tables)} Dateien geladen, {total_typos} Typos gefunden.\n")
    return tables


def merge_tables(tables: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Führt alle Tabellen spaltenweise zusammen (inner join auf Zeilenindex).
    
    Args:
        tables: Dictionary mit DataFrames
        
    Returns:
        Zusammengeführter DataFrame
    """
    print("[merge_tables] Führe Tabellen zusammen...")
    
    # Finde minimale Zeilenanzahl
    row_counts = {name: df.shape[0] for name, df in tables.items()}
    min_rows = min(row_counts.values())
    max_rows = max(row_counts.values())
    
    if min_rows != max_rows:
        print(f"  ⚠ Warnung: Unterschiedliche Zeilenzahlen gefunden!")
        print(f"    Min: {min_rows}, Max: {max_rows}")
        for name, count in row_counts.items():
            if count != min_rows:
                print(f"    └─ {name}: {count} Zeilen → {count - min_rows} Zeilen werden abgeschnitten")
    
    # Alle auf minimale Länge kürzen
    trimmed_tables = {name: df.iloc[:min_rows].reset_index(drop=True) 
                      for name, df in tables.items()}
    
    # Spaltenweise zusammenführen
    merged = pd.concat(trimmed_tables.values(), axis=1)
    
    print(f"  ✓ Merged: {merged.shape[0]} Zeilen × {merged.shape[1]} Spalten\n")
    return merged


def basic_stats(df: pd.DataFrame) -> pd.DataFrame:
    """
    Erstellt Basis-Statistiken für alle Spalten.
    
    Args:
        df: Input DataFrame
        
    Returns:
        DataFrame mit Statistiken
    """
    print("[basic_stats] Erstelle Statistiken...")
    
    stats_list = []
    
    for col in df.columns:
        series = df[col].dropna()
        n_total = len(df[col])
        n_missing = df[col].isna().sum()
        pct_missing = 100 * n_missing / n_total if n_total > 0 else 0
        
        if len(series) > 0:
            stats_list.append({
                'column': col,
                'count': len(series),
                'n_missing': n_missing,
                'pct_missing': round(pct_missing, 2),
                'min': series.min(),
                'p1': series.quantile(0.01),
                'mean': series.mean(),
                'median': series.median(),
                'p99': series.quantile(0.99),
                'max': series.max(),
                'std': series.std()
            })
        else:
            stats_list.append({
                'column': col,
                'count': 0,
                'n_missing': n_missing,
                'pct_missing': 100.0,
                'min': np.nan,
                'p1': np.nan,
                'mean': np.nan,
                'median': np.nan,
                'p99': np.nan,
                'max': np.nan,
                'std': np.nan
            })
    
    stats_df = pd.DataFrame(stats_list)
    stats_df.to_csv("out/stats.csv", index=False)
    print(f"  ✓ Statistiken gespeichert: out/stats.csv\n")
    
    return stats_df


def validate_and_flag(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Validiert Daten und markiert Ausreißer via IQR-Regel.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Tuple aus (bereinigter DataFrame, Quality-Report DataFrame)
    """
    print("[validate_and_flag] Validiere Daten und markiere Ausreißer...")
    
    # Zahlen erzwingen
    df_clean = df.apply(pd.to_numeric, errors='coerce')
    
    quality_list = []
    
    for col in df_clean.columns:
        series = df_clean[col].dropna()
        n_total = len(df_clean[col])
        n_missing = df_clean[col].isna().sum()
        
        # Ausreißer via IQR
        if len(series) > 0:
            q1 = series.quantile(0.25)
            q3 = series.quantile(0.75)
            iqr = q3 - q1
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            
            n_outliers = ((series < lower) | (series > upper)).sum()
            pct_outliers = 100 * n_outliers / n_total if n_total > 0 else 0
        else:
            n_outliers = 0
            pct_outliers = 0
        
        # Typos (bereits zu NaN konvertiert beim Einlesen)
        n_typos = n_missing
        
        quality_list.append({
            'column': col,
            'n_outliers': n_outliers,
            'pct_outliers': round(pct_outliers, 2),
            'n_typos': n_typos,
            'pct_typos': round(100 * n_typos / n_total, 2) if n_total > 0 else 0
        })
    
    quality_df = pd.DataFrame(quality_list)
    quality_df.to_csv("out/quality.csv", index=False)
    print(f"  ✓ Quality-Report gespeichert: out/quality.csv\n")
    
    return df_clean, quality_df


def apply_missing_policies(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Wendet Missing-Value-Policies an:
    - Spalten mit >40% Missing: droppen
    - Spalten mit 0-40% Missing: Median-Imputation
    
    Args:
        df: Input DataFrame
        
    Returns:
        Tuple aus (bereinigter DataFrame, Policies DataFrame)
    """
    print("[apply_missing_policies] Wende Missing-Policies an...")
    
    policies_list = []
    df_clean = df.copy()
    
    for col in df.columns:
        n_total = len(df[col])
        n_missing = df[col].isna().sum()
        pct_missing = 100 * n_missing / n_total if n_total > 0 else 0
        
        if pct_missing > 40:
            action = "DROP (>40% missing)"
            df_clean = df_clean.drop(columns=[col])
        elif pct_missing > 0:
            action = f"IMPUTE with median ({df[col].median():.4f})"
            df_clean[col] = df_clean[col].fillna(df[col].median())
        else:
            action = "NO ACTION (no missing)"
        
        policies_list.append({
            'column': col,
            'pct_missing': round(pct_missing, 2),
            'action': action
        })
    
    policies_df = pd.DataFrame(policies_list)
    policies_df.to_csv("out/policies.csv", index=False)
    print(f"  ✓ Policies gespeichert: out/policies.csv")
    print(f"  ✓ Spalten nach Bereinigung: {df_clean.shape[1]} (von {df.shape[1]})\n")
    
    return df_clean, policies_df


def winsorize_outliers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Winsorisiert Ausreißer auf [p1, p99] pro Spalte.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Winsorisierter DataFrame
    """
    print("[winsorize_outliers] Winsorisiere auf [p1, p99]...")
    
    df_winsor = df.copy()
    
    for col in df_winsor.columns:
        if df_winsor[col].notna().sum() > 0:
            p1 = df_winsor[col].quantile(0.01)
            p99 = df_winsor[col].quantile(0.99)
            df_winsor[col] = df_winsor[col].clip(lower=p1, upper=p99)
    
    print(f"  ✓ Winsorisierung abgeschlossen\n")
    return df_winsor


def compute_correlation(df: pd.DataFrame) -> pd.DataFrame:
    """
    Berechnet Pearson-Korrelation und erstellt Heatmap.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Korrelationsmatrix
    """
    print("[compute_correlation] Berechne Korrelationsmatrix...")
    
    corr = df.corr(numeric_only=True)
    corr.to_csv("out/corr.csv")
    print(f"  ✓ Korrelation gespeichert: out/corr.csv")
    
    # Heatmap erstellen
    plt.figure(figsize=(20, 16))
    sns.heatmap(corr, cmap='coolwarm', center=0, square=True, 
                linewidths=0.5, cbar_kws={"shrink": 0.8}, 
                xticklabels=True, yticklabels=True)
    plt.title('Korrelations-Heatmap', fontsize=16, pad=20)
    plt.tight_layout()
    plt.savefig("out/corr_heatmap.png", dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Heatmap gespeichert: out/corr_heatmap.png\n")
    
    return corr


def compute_mutual_info(df: pd.DataFrame) -> None:
    """
    Berechnet Mutual Information falls Zielspalte vorhanden.
    Sucht nach typischen Zielspalten aus profile.txt.
    
    Args:
        df: Input DataFrame
    """
    print("[compute_mutual_info] Prüfe auf Zielspalten...")
    
    # Suche nach typischen Zielspalten (aus profile.txt)
    # Diese sollten kategorisch sein (Cooler, Valve, Pump, Accumulator, Stable Flag)
    target_candidates = [col for col in df.columns if col.startswith('profile_')]
    
    if not target_candidates:
        print("  ℹ Keine Zielspalte gefunden (profile_* fehlt). Mutual Info wird übersprungen.\n")
        return
    
    # Nutze erste Zielspalte
    target_col = target_candidates[0]
    print(f"  ✓ Zielspalte gefunden: {target_col}")
    
    # Features (alle außer Zielspalten)
    feature_cols = [col for col in df.columns if not col.startswith('profile_')]
    X = df[feature_cols].fillna(0)  # MI benötigt keine NaNs
    y = df[target_col].fillna(0)
    
    # Prüfe ob kategorisch oder numerisch
    n_unique = y.nunique()
    
    if n_unique < 10:  # Kategorisch
        print(f"  → Zielspalte ist kategorisch ({n_unique} Klassen), nutze mutual_info_classif")
        mi_scores = mutual_info_classif(X, y, random_state=42)
    else:  # Numerisch
        print(f"  → Zielspalte ist numerisch, nutze mutual_info_regression")
        mi_scores = mutual_info_regression(X, y, random_state=42)
    
    # Ergebnis speichern
    mi_df = pd.DataFrame({
        'feature': feature_cols,
        'mi_score': mi_scores
    }).sort_values('mi_score', ascending=False)
    
    mi_df.to_csv("out/mi.csv", index=False)
    print(f"  ✓ Mutual Information gespeichert: out/mi.csv\n")


def main():
    """
    Hauptfunktion: Führt komplette Datenaufbereitung durch.
    """
    print("=" * 70)
    print("HYDRAULIC SYSTEMS - DATA PREPARATION")
    print("=" * 70 + "\n")
    
    # 1. Laden
    tables = load_txt_folder("data")
    
    # 2. Merge
    df_merged = merge_tables(tables)
    
    print(f"[main] Speichere raw_merged ({df_merged.shape})...")
    df_merged.to_parquet("out/raw_merged.parquet", index=False)
    print(f"  ✓ Raw merged gespeichert: out/raw_merged.parquet")
    
    # Preview: erste 100 Spalten als CSV
    df_merged.iloc[:, :100].to_csv("out/raw_merged_preview.csv", index=False)
    print(f"  ✓ Preview (erste 100 Spalten) gespeichert: out/raw_merged_preview.csv\n")
    
    # 3. Basic Stats
    stats_df = basic_stats(df_merged)
    
    # 4. Validate & Flag
    df_validated, quality_df = validate_and_flag(df_merged)
    
    # 5. Apply Missing Policies
    df_clean, policies_df = apply_missing_policies(df_validated)
    
    # 6. Exports (mit und ohne Winsorize)
    # Bei vielen Spalten: Parquet nutzen (schneller & kompakter)
    df_clean_nowinsor = df_clean.copy()
    
    print(f"[main] Speichere clean_nowinsor ({df_clean_nowinsor.shape})...")
    df_clean_nowinsor.to_parquet("out/clean_nowinsor.parquet", index=False)
    print(f"  ✓ Clean (ohne Winsorize) gespeichert: out/clean_nowinsor.parquet")
    
    # Nur erste 100 Spalten als CSV (für Quick View)
    df_clean_nowinsor.iloc[:, :100].to_csv("out/clean_nowinsor_preview.csv", index=False)
    print(f"  ✓ Preview (erste 100 Spalten) gespeichert: out/clean_nowinsor_preview.csv\n")
    
    df_clean_winsor = winsorize_outliers(df_clean)
    
    print(f"[main] Speichere clean ({df_clean_winsor.shape})...")
    df_clean_winsor.to_parquet("out/clean.parquet", index=False)
    print(f"  ✓ Clean (mit Winsorize) gespeichert: out/clean.parquet")
    
    # Nur erste 100 Spalten als CSV (für Quick View)
    df_clean_winsor.iloc[:, :100].to_csv("out/clean_preview.csv", index=False)
    print(f"  ✓ Preview (erste 100 Spalten) gespeichert: out/clean_preview.csv\n")
    
    # 7. Korrelation
    corr_matrix = compute_correlation(df_clean_winsor)
    
    # 8. Mutual Information (optional)
    compute_mutual_info(df_clean_winsor)
    
    print("=" * 70)
    print("✓ DATA PREPARATION ABGESCHLOSSEN")
    print("=" * 70)
    print("\nExportierte Dateien:")
    print("  • out/raw_merged.parquet (Hauptdatei)")
    print("  • out/raw_merged_preview.csv (erste 100 Spalten)")
    print("  • out/stats.csv")
    print("  • out/quality.csv")
    print("  • out/policies.csv")
    print("  • out/clean_nowinsor.parquet (Hauptdatei)")
    print("  • out/clean_nowinsor_preview.csv (erste 100 Spalten)")
    print("  • out/clean.parquet (Hauptdatei)")
    print("  • out/clean_preview.csv (erste 100 Spalten)")
    print("  • out/corr.csv")
    print("  • out/corr_heatmap.png")
    print("  • out/mi.csv (falls Zielspalte vorhanden)")
    print()


if __name__ == "__main__":
    main()
