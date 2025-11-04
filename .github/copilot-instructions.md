## Quick context for AI coding agents

This repository contains **beginner-level** data-preparation code for the UCI Hydraulic Systems dataset. The goal is simple data cleaning and feature extraction — **no machine learning models**, kept intentionally simple for educational purposes.

The authoritative script is `prep_corrected.py`. `archive_prep.py` is legacy code kept for reference only.

### Key concepts

**Data model:**
- Raw files in `data/*.txt` are time-series: rows = cycles (2,205), columns = timepoints (per-sensor, up to 6,000)
- Pipeline aggregates each sensor's time-series into **8 features**: `_mean`, `_std`, `_min`, `_max`, `_median`, `_q25`, `_q75`, `_range`
- Result: 43,680 columns → 136 features (17 sensors × 8 features)

**Targets:**
- Live in `docs/profile.txt` with columns: `cooler_condition`, `valve_condition`, `pump_leakage`, `accumulator_pressure`, `stable_flag`

**Outputs** (written to `out/`):
- `features_complete.csv` — main dataset (2,205 rows × 141 columns)
- `feature_stats.csv`, `correlation.csv`, `mutual_information.csv`
- Visualizations: heatmaps, distributions, boxplots (PNGs)

### Developer workflows (PowerShell)

Install dependencies:
```powershell
pip install -r requirements.txt
```

Run the pipeline:
```powershell
python prep_corrected.py
```

Explore interactively:
```powershell
code notebooks/01_data_exploration.ipynb
```

### Important conventions

- **Keep it simple:** This is beginner-level code for a university module. Avoid overkill features like advanced imputation, Parquet exports, or complex ML pipelines.
- **One main script:** `prep_corrected.py` is THE script. Don't edit `archive_prep.py` unless updating for reference.
- **CSV only:** Export format is CSV (not Parquet). Easy to open, beginner-friendly.
- **Auto-create `out/`:** Script creates the directory automatically (`Path('out').mkdir(exist_ok=True)`).
- **Feature naming:** Deterministic pattern `{sensor}_{statistic}`, e.g., `ps1_mean`, `ce_max`, `ts3_q75`.
- **No missing values:** Dataset has no missing values according to docs. The `pd.to_numeric(errors='coerce')` handles typos only.
- **Mutual Information optional:** It's a nice-to-have for advanced students. Simple correlation is sufficient for beginners.

### Common edits

- **Add a feature (e.g., skewness):** Modify `extract_features()` in `prep_corrected.py`, ensure it's exported in `features_complete.csv`.
- **Change visualizations:** Update `create_visualizations()` — keep plots simple and labeled in German.
- **Simplify code:** Remove complexity if it's over-engineered for beginner level (check with maintainer first).

### Key files

- `prep_corrected.py` — main pipeline (feature extraction, stats, correlation, export)
- `archive_prep.py` — legacy variant with more validation logic (winsorization, detailed missing-value policies)
- `README.md` — beginner-friendly explanation, dataset description, insights
- `notebooks/01_data_exploration.ipynb` — interactive exploration with plots

### Testing/verification

No unit tests. Verify changes by:
1. Run `python prep_corrected.py` without errors
2. Check `out/features_complete.csv` exists with shape (2205, 141)
3. Verify plots are generated and look reasonable

### If unclear

- Ask maintainer if changes should be beginner-appropriate or if you're adding too much complexity
- Confirm German vs. English for comments/output (currently mixed: code comments in German, README in German, docstrings in German)
- This is a **university assignment** — prioritize clarity and educational value over production-grade code

