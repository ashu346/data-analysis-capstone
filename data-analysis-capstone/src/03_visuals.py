"""
Step 3 - Charts (matplotlib) + a one-page dashboard preview image.
Run:  python src/03_visuals.py
"""
import pandas as pd, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CH = ROOT / "outputs" / "charts"
df = pd.read_csv(ROOT / "data" / "cleaned_data.csv", parse_dates=["date"],
                 keep_default_na=False, na_values=[""])

NAVY, GOLD, TEAL, RED, GREY = "#1f2d3d", "#c9a24d", "#0f7b6c", "#c0392b", "#8c97a3"
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False,
                     "axes.spines.right": False, "axes.titleweight": "bold", "axes.titlesize": 12})
M = FuncFormatter(lambda v, _: f"${v/1e6:,.1f}M")

def save(fig, name):
    fig.tight_layout(); fig.savefig(CH / name, dpi=160, bbox_inches="tight"); plt.close(fig)

# ---- aggregates
seg = df.groupby("segment").agg(sales=("sales","sum"), profit=("profit","sum")).sort_values("sales", ascending=False)
seg["margin"] = seg.profit / seg.sales * 100
ctry = df.groupby("country").agg(sales=("sales","sum"), profit=("profit","sum"), disc=("discounts","sum"), gross=("gross_sales","sum"))
ctry["margin"] = ctry.profit / ctry.sales * 100; ctry = ctry.sort_values("profit", ascending=False)
prod = df.groupby("product").agg(sales=("sales","sum"), profit=("profit","sum")).sort_values("sales", ascending=False)
prod["margin"] = prod.profit / prod.sales * 100
order = ["None", "Low", "Medium", "High"]
band = df.groupby("discount_band").agg(sales=("sales","sum"), profit=("profit","sum"), disc=("discounts","sum"), gross=("gross_sales","sum")).loc[order]
band["margin"] = band.profit / band.sales * 100; band["disc_pct"] = band.disc / band.gross * 100
ent = df[df.segment == "Enterprise"].groupby("discount_band").agg(sales=("sales","sum"), profit=("profit","sum")).loc[order]
ent["margin"] = ent.profit / ent.sales * 100
mon = df.groupby("month").agg(sales=("sales","sum"), profit=("profit","sum"))
heat = df.pivot_table(index="segment", columns="country", values="profit", aggfunc="sum").loc[seg.index]

# ---- individual charts
def monthly(ax):
    x = np.arange(len(mon)); ax.bar(x, mon.sales, color=NAVY, label="Net sales")
    ax2 = ax.twinx(); ax2.plot(x, mon.profit, color=GOLD, marker="o", lw=2, label="Profit")
    ax.set_xticks(x); ax.set_xticklabels([m[2:] for m in mon.index], rotation=60, fontsize=8)
    ax.yaxis.set_major_formatter(M); ax2.yaxis.set_major_formatter(M); ax2.spines["right"].set_visible(True)
    ax.set_title("Monthly net sales & profit")
    h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1+h2, l1+l2, loc="upper left", frameon=False, fontsize=8)

def segment(ax):
    x = np.arange(len(seg)); w = .38
    ax.bar(x-w/2, seg.sales, w, color=NAVY, label="Net sales"); ax.bar(x+w/2, seg.profit, w, color=[TEAL if p>0 else RED for p in seg.profit], label="Profit")
    ax.set_xticks(x); ax.set_xticklabels([n.replace(" ","\n") for n in seg.index], fontsize=8); ax.yaxis.set_major_formatter(M)
    ax.set_title("Net sales vs profit by segment"); ax.axhline(0, color="k", lw=.6)
    for i, m in enumerate(seg.margin): ax.text(i+w/2, max(seg.profit.iloc[i],0)+1e6, f"{m:.0f}%", ha="center", fontsize=8, color=GREY)
    ax.legend(frameon=False, fontsize=8)

def country(ax):
    ax.bar(ctry.index, ctry.profit, color=TEAL); ax.yaxis.set_major_formatter(M); ax.set_title("Profit by country (+ margin %)")
    for i, (p, m) in enumerate(zip(ctry.profit, ctry.margin)): ax.text(i, p+5e4, f"{m:.1f}%", ha="center", fontsize=9)
    ax.tick_params(axis="x", labelsize=9)

def product(ax):
    ax.barh(prod.index[::-1], prod.sales[::-1], color=NAVY); ax.xaxis.set_major_formatter(M)
    ax.set_title("Net sales by product")
    for i, (s, m) in enumerate(zip(prod.sales[::-1], prod.margin[::-1])): ax.text(s+3e5, i, f"{m:.1f}% margin", va="center", fontsize=8, color=GREY)
    ax.set_xlim(0, prod.sales.max()*1.3)

def disc(ax):
    cols = [TEAL, TEAL, GOLD, RED]
    ax.bar(band.index, band.margin, color=cols); ax.set_title("Profit margin by discount band")
    ax.set_ylabel("Profit margin %")
    for i, (m, d) in enumerate(zip(band.margin, band.disc_pct)): ax.text(i, m+.4, f"{m:.1f}%\n(avg disc {d:.1f}%)", ha="center", fontsize=8)
    ax.set_ylim(0, band.margin.max()*1.25)

def enterprise(ax):
    ax.bar(ent.index, ent.margin, color=[TEAL if m>0 else RED for m in ent.margin])
    ax.set_ylim(ent.margin.min()*1.3, ent.margin.max()*1.35); ax.axhline(0, color="k", lw=.7); ax.set_title("Enterprise margin by discount"); ax.set_ylabel("Profit margin %")
    for i, m in enumerate(ent.margin): ax.text(i, m + (.5 if m>0 else -1.2), f"{m:.1f}%", ha="center", fontsize=9)

def heatmap(ax):
    im = ax.imshow(heat.values/1e6, cmap="RdYlGn", aspect="auto", vmin=-3, vmax=3)
    ax.set_xticks(range(len(heat.columns))); ax.set_xticklabels(heat.columns, fontsize=8)
    ax.set_yticks(range(len(heat.index))); ax.set_yticklabels(heat.index, fontsize=8)
    for i in range(heat.shape[0]):
        for j in range(heat.shape[1]): ax.text(j, i, f"{heat.values[i,j]/1e6:.2f}", ha="center", va="center", fontsize=8)
    ax.set_title("Profit ($M): segment x country")
    for s in ax.spines.values(): s.set_visible(False)

charts = {"01_monthly_trend.png": monthly, "02_segment_sales_profit.png": segment, "03_country_profit.png": country,
          "04_product_sales.png": product, "05_discount_band_margin.png": disc,
          "06_enterprise_margin_by_discount.png": enterprise, "07_segment_country_heatmap.png": heatmap}
for name, fn in charts.items():
    fig, ax = plt.subplots(figsize=(7.5, 4)); fn(ax); save(fig, name)

# ---- dashboard preview (what the Power BI / Tableau page should look like)
fig = plt.figure(figsize=(16, 10), facecolor="#eef1f4")
fig.text(.03, .955, "Sales & Profitability Dashboard", fontsize=22, weight="bold", color=NAVY)
fig.text(.03, .925, "Sep 2013 - Dec 2014  |  5 segments  |  5 countries  |  6 products  |  700 transactions", fontsize=10, color=GREY)
kpis = [("Net Sales", f"${df.sales.sum()/1e6:,.1f}M"), ("Profit", f"${df.profit.sum()/1e6:,.1f}M"),
        ("Profit Margin", f"{df.profit.sum()/df.sales.sum()*100:.1f}%"), ("Units Sold", f"{df.units_sold.sum()/1e6:,.2f}M"),
        ("Discount Rate", f"{df.discounts.sum()/df.gross_sales.sum()*100:.1f}%"), ("Loss-making Deals", f"{int(df.is_loss.sum())}")]
for i, (t, v) in enumerate(kpis):
    ax = fig.add_axes([.03 + i*.1625, .80, .150, .105]); ax.set_facecolor("white"); ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values(): s.set_color("#d5dbe1")
    ax.text(.5, .66, v, ha="center", fontsize=20, weight="bold", color=RED if t.startswith("Loss") else NAVY)
    ax.text(.5, .22, t, ha="center", fontsize=10, color=GREY)
pos = {monthly: [.03, .42, .40, .33], segment: [.54, .42, .20, .33], country: [.82, .42, .15, .33],
       product: [.03, .05, .30, .30], disc: [.40, .05, .27, .30], enterprise: [.74, .05, .23, .30]}
for fn, p in pos.items():
    ax = fig.add_axes(p); ax.set_facecolor("white"); fn(ax)
fig.text(.97, .01, "Preview rendered in Python - rebuild interactively in Power BI/Tableau using bi/POWERBI_GUIDE.md", ha="right", fontsize=8, color=GREY)
fig.savefig(ROOT / "bi" / "dashboard_preview.png", dpi=130, bbox_inches="tight"); plt.close(fig)
print("charts saved:", sorted(p.name for p in CH.glob('*.png')))
