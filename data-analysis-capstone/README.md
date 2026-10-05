# Sales & Profitability - End-to-End Analysis (Capstone)

Week 4 capstone: clean and explore a sales dataset in **Python**, analyse with **SQL and pandas**, visualise in **Excel and a BI tool (Power BI/Tableau)**, and compile a final report with charts, findings and recommendations.

## Headline results
- Net sales **$118.7M**, profit **$16.9M** (**14.2%** margin), 700 transactions, Sep 2013 - Dec 2014.
- **Government** = 44% of sales, 67% of profit.
- **Enterprise loses money** (-3.1% margin; all 58 loss-making deals). Price 125 vs cost 120 -> only 4% gross margin, so any discount above 4% causes a loss.
- **Discounts cut margin** from 21.9% (none) to 9.1% (High band).
- Like-for-like Sep-Dec sales grew **+37%** (2014 vs 2013).

## Repo structure
```
data/        Sample_data.xlsx (raw), cleaned_data.csv (output of step 1)
src/         01_clean_explore.py  -> clean + explore (pandas)
             02_analysis.py       -> run SQL queries + pandas analysis, cross-check
             03_visuals.py        -> charts + dashboard preview
             04_excel_report.py   -> Excel workbook with formulas and charts
             05_build_report.py   -> final PDF report
             06_build_dashboard.py -> interactive HTML dashboard
sql/         queries.sql (12 queries)
excel/       Sales_Analysis.xlsx (Data, Summary with SUMIFS formulas + charts, Key Insights)
bi/          dashboard.html (interactive dashboard with filters), dashboard_preview.png, POWERBI_STEP_BY_STEP.md + Business_Metrics_Dashboard_PowerBI_Ready.xlsx (Power BI source file), POWERBI_GUIDE.md
outputs/     charts/ (PNG), tables/ (query results, data quality report)
report/      Final_Report.pdf, Stakeholder_Summary.md
```

## How to run
```bash
pip install -r requirements.txt
./run_all.sh          # or run the src/ scripts in order
```

## Deliverables
- [x] Complete code - this repo (`src/`, `sql/`, `run_all.sh`)
- [x] PDF explanation report - `report/Final_Report.pdf`
- [x] Stakeholder insight summary - `report/Stakeholder_Summary.md`
- [x] Excel analysis - `excel/Sales_Analysis.xlsx`
- [x] Interactive dashboard with filters (Year, Segment, Country, Product, Discount band) - `bi/dashboard.html` (open in a browser; layout image in `bi/dashboard_preview.png`)
- Power BI: the dashboard above is built as an HTML/Chart.js dashboard, not a `.pbix`. A Power BI-ready data file (`bi/Business_Metrics_Dashboard_PowerBI_Ready.xlsx`) and build steps (`bi/POWERBI_STEP_BY_STEP.md`, `bi/POWERBI_GUIDE.md`) are included.

## Tools
Python (pandas, matplotlib, openpyxl, reportlab), SQL (SQLite), Excel, interactive HTML dashboard (Chart.js).
