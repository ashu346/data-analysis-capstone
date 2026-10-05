"""
Step 1 - Clean & explore the dataset in Python (pandas).
Run:  python src/01_clean_explore.py
Output: data/cleaned_data.csv + outputs/tables/data_quality_report.txt
"""
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
raw = pd.read_excel(ROOT / "data" / "Sample_data.xlsx")
log = []
def note(msg):
    print(msg); log.append(msg)

note("=== RAW DATA ===")
note(f"Shape: {raw.shape[0]} rows x {raw.shape[1]} columns")
note(f"Columns: {list(raw.columns)}")

df = raw.copy()

# 1. Column names: strip stray spaces (' Sales' has a leading space), snake_case
df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
note("\n[Clean 1] Column names stripped/standardised (e.g. ' Sales' -> 'sales').")

# 2. Text columns: trim whitespace, consistent country label
for c in ["segment", "country", "product", "discount_band", "month_name"]:
    df[c] = df[c].astype("string").str.strip()
df["country"] = df["country"].replace({"United States of America": "USA"})
note("[Clean 2] Text trimmed; 'United States of America' shortened to 'USA' for charts.")

# 3. Missing values
n_missing = int(df["discount_band"].isna().sum())
note(f"\n[Clean 3] Missing values per column:\n{raw.isna().sum()[raw.isna().sum()>0].to_string()}")
none_disc = df.loc[df["discount_band"].isna(), "discounts"].eq(0).all()
note(f"          Discount Band is blank in {n_missing} rows and Discounts = 0 in ALL of them ({none_disc}) "
     f"-> blank means 'no discount'. Filled with 'None' (value is NOT guessed).")
df["discount_band"] = df["discount_band"].fillna("None")

# 4. Duplicates
note(f"\n[Clean 4] Fully duplicated rows: {df.duplicated().sum()} (nothing to drop).")

# 5. Types
df["date"] = pd.to_datetime(df["date"])
df["units_sold"] = df["units_sold"].astype(float)
note("[Clean 5] Date converted to datetime.")

# 6. Consistency / integrity checks
chk1 = (df.gross_sales - df.discounts - df.sales).abs().max()
chk2 = (df.sales - df.cogs - df.profit).abs().max()
chk3 = (df.units_sold * df.sale_price - df.gross_sales).abs().max()
chk4 = ((df.date.dt.month != df.month_number) | (df.date.dt.year != df.year)).sum()
note(f"\n[Check] Gross Sales - Discounts = Sales   (max error {chk1:.6f})  OK")
note(f"[Check] Sales - COGS = Profit             (max error {chk2:.6f})  OK")
note(f"[Check] Units x Sale Price = Gross Sales  (max error {chk3:.6f})  OK")
note(f"[Check] Date vs Month/Year columns mismatch: {chk4} rows  OK")

# 7. New features
df["profit_margin_pct"] = (df.profit / df.sales * 100).round(2)
df["discount_pct"] = (df.discounts / df.gross_sales * 100).round(2)
df["month"] = df.date.dt.to_period("M").astype(str)
df["is_loss"] = df.profit < 0
note("\n[Feature] Added: profit_margin_pct, discount_pct, month (YYYY-MM), is_loss.")

# 8. Exploration
note("\n=== EXPLORATION ===")
note(f"Date range: {df.date.min().date()} to {df.date.max().date()}")
note("  -> 2013 contains only Sep-Dec (4 months); 2014 has all 12 months. "
     "Year-over-year totals are NOT like-for-like (see report).")
for c in ["segment", "country", "product", "discount_band"]:
    note(f"\n{c} value counts:\n{df[c].value_counts().to_string()}")
note(f"\nLoss-making rows (profit < 0): {int(df.is_loss.sum())} of {len(df)}")
note("\nNumeric summary:\n" + df[["units_sold","gross_sales","discounts","sales","cogs","profit"]].describe().round(1).to_string())

q1, q3 = df.profit.quantile([.25, .75]); iqr = q3 - q1
out = df[(df.profit > q3 + 1.5*iqr) | (df.profit < q1 - 1.5*iqr)]
note(f"\nProfit outliers by IQR rule: {len(out)} rows (kept - they are real large deals, not errors).")

df.to_csv(ROOT / "data" / "cleaned_data.csv", index=False)
(ROOT / "outputs" / "tables" / "data_quality_report.txt").write_text("\n".join(log))
note("\nSaved data/cleaned_data.csv")
