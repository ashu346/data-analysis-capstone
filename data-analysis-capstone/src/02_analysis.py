"""
Step 2 - Analyse with SQL (sqlite3) AND pandas, cross-check both, export tables.
Run:  python src/02_analysis.py
"""
import re, sqlite3
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "tables"
df = pd.read_csv(ROOT / "data" / "cleaned_data.csv", parse_dates=["date"], keep_default_na=False, na_values=[""])  # keep "None" band as text

# ---------- SQL ----------
con = sqlite3.connect(":memory:")
df.assign(date=df.date.dt.strftime("%Y-%m-%d")).to_sql("sales", con, index=False)
text = (ROOT / "sql" / "queries.sql").read_text()
queries = dict(re.findall(r"-- name: (\w+)\n(.*?;)", text, flags=re.S))
sql = {}
for name, q in queries.items():
    sql[name] = pd.read_sql_query(q, con)
    sql[name].to_csv(OUT / f"{name}.csv", index=False)
    print(f"\n### {name}\n{sql[name].to_string(index=False)}")

# ---------- pandas (same questions) + cross-check ----------
seg = (df.groupby("segment").agg(net_sales=("sales","sum"), profit=("profit","sum"))
         .sort_values("profit", ascending=False))
seg["margin_pct"] = seg.profit / seg.net_sales * 100
assert (seg.index == sql["q2_by_segment"].segment).all()
assert abs(seg.profit.sum() - sql["q1_kpi_overview"].profit[0]) < 1
ctry = df.groupby("country").profit.sum().sort_values(ascending=False)
assert list(ctry.index) == list(sql["q3_by_country"].country)
band = df.groupby("discount_band").agg(sales=("sales","sum"), profit=("profit","sum"))
band["margin"] = band.profit / band.sales * 100
assert abs(band.loc["High","margin"] - sql["q5_discount_band_effect"].set_index("discount_band").loc["High","margin_pct"]) < 0.1
print("\nCross-check passed: pandas results match SQL results.")

# ---------- extra pandas-only analysis ----------
# correlation of discount % with margin
corr = df[df.discount_pct > 0][["discount_pct", "profit_margin_pct"]].corr().iloc[0, 1]
print(f"Correlation discount_pct vs profit_margin_pct (discounted deals): {corr:.2f}")

# Enterprise: price vs unit cost
ent = df[df.segment == "Enterprise"]
unit_cost = (ent.cogs / ent.units_sold).round(2).unique()
print("Enterprise sale price:", ent.sale_price.unique(), "| unit COGS values:", unit_cost[:5])
print("Enterprise discount % range on loss deals:",
      ent[ent.is_loss].discount_pct.min().round(1), "-", ent[ent.is_loss].discount_pct.max().round(1))
print("Enterprise profit margin before discount (gross - cogs)/gross:",
      round(((ent.gross_sales - ent.cogs).sum()) / ent.gross_sales.sum() * 100, 1), "%")

# What if Enterprise had no loss-making deals?
print("Total loss from loss-making deals:", round(df.loc[df.is_loss, 'profit'].sum()))
print("Profit lost to discounts on all deals:", round(df.discounts.sum()))

# Group-level margin by segment x discount band
print(df.pivot_table(index="segment", columns="discount_band", values="profit_margin_pct", aggfunc="mean").round(1))
seg.round(1).to_csv(OUT / "pandas_segment_summary.csv")
