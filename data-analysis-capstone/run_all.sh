#!/usr/bin/env bash
# Re-creates every output from the raw data file.
set -e
python src/01_clean_explore.py
python src/02_analysis.py
python src/03_visuals.py
python src/04_excel_report.py
python src/05_build_report.py
python src/06_build_dashboard.py
