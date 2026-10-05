"""
Step 5 - Compile the final PDF report (charts + findings + recommendations).
Run:  python src/05_build_report.py
"""
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak, KeepTogether
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]; CH = ROOT / "outputs" / "charts"; T = ROOT / "outputs" / "tables"
ss = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=ss["Heading1"], fontName="Helvetica-Bold", fontSize=17, textColor=colors.HexColor("#1f2d3d"), spaceAfter=8)
H2 = ParagraphStyle("H2", parent=ss["Heading2"], fontName="Helvetica-Bold", fontSize=12.5, textColor=colors.HexColor("#0f7b6c"), spaceBefore=10, spaceAfter=4)
B = ParagraphStyle("B", parent=ss["BodyText"], fontName="Helvetica", fontSize=10, leading=14.5)
BL = ParagraphStyle("BL", parent=B, leftIndent=14, bulletIndent=2, spaceAfter=2)
SM = ParagraphStyle("SM", parent=B, fontSize=8.5, textColor=colors.HexColor("#666666"))
def bullets(items): return [Paragraph(t, BL, bulletText="\u2022") for t in items]
def img(name, w=15.5): 
    from PIL import Image as PI
    iw, ih = PI.open(CH / name).size; return Image(str(CH / name), width=w*cm, height=w*cm*ih/iw)
def table(df, widths=None):
    data = [list(df.columns)] + df.astype(str).values.tolist()
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#1f2d3d")),("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),8.5),("GRID",(0,0),(-1,-1),.3,colors.HexColor("#d5dbe1")),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white, colors.HexColor("#f4f6f8")]),("ALIGN",(1,0),(-1,-1),"RIGHT")])); return t
def money(v): return f"-${abs(v)/1e6:,.2f}M" if v < 0 else f"${v/1e6:,.2f}M"

seg = pd.read_csv(T/"q2_by_segment.csv"); seg_t = pd.DataFrame({"Segment": seg.segment, "Net sales": seg.net_sales.map(money),
    "Profit": seg.profit.map(money), "Margin %": seg.margin_pct.map("{:.1f}".format), "Share of profit %": seg.share_of_profit_pct.map("{:.1f}".format)})
bd = pd.read_csv(T/"q5_discount_band_effect.csv", keep_default_na=False); bd_t = pd.DataFrame({"Discount band": bd.discount_band, "Deals": bd.deals,
    "Avg discount %": bd.avg_discount_pct, "Net sales": bd.net_sales.map(money), "Margin %": bd.margin_pct, "Loss deals": bd.loss_making_deals})

doc = SimpleDocTemplate(str(ROOT/"report"/"Final_Report.pdf"), pagesize=A4, leftMargin=2*cm, rightMargin=2*cm, topMargin=1.8*cm, bottomMargin=1.8*cm,
                        title="Sales & Profitability - End-to-End Analysis", author="Capstone Project")
S = []
S += [Paragraph("Sales &amp; Profitability: End-to-End Analysis", H1),
      Paragraph("Capstone Project - Data Visualization &amp; Analysis (Python, SQL, Pandas, Excel, Power BI/Tableau)", SM), Spacer(1, 8)]

S += [Paragraph("1. Executive summary", H2),
      Paragraph("The business earned <b>$118.7M</b> in net sales and <b>$16.9M</b> in profit (<b>14.2%</b> margin) across 700 transactions between "
                "Sep 2013 and Dec 2014. Profit is concentrated: <b>Government</b> delivers 44% of sales and 67% of profit. The biggest leak is the "
                "<b>Enterprise</b> segment, which sells $19.6M but loses $0.61M, and <b>discounting</b>, which cuts margin from 21.9% (no discount) to 9.1% (High band).", B)]

S += [Paragraph("2. Data &amp; cleaning (Python)", H2)]
S += bullets(["Dataset: 700 rows x 16 columns - segment, country, product, discount band, units, prices, gross sales, discounts, sales, COGS, profit, date.",
    "Column names standardised (the <i>Sales</i> column had a leading space); country 'United States of America' shortened to 'USA'.",
    "<b>53 blank Discount Band values</b> - all have Discounts = 0, so they mean 'no discount' and were labelled <b>None</b> (not guessed).",
    "No duplicate rows. Integrity checks passed: Gross - Discounts = Sales, Sales - COGS = Profit, Units x Price = Gross Sales, Date = Month/Year.",
    "Added features: profit margin %, discount %, month (YYYY-MM), loss flag. Large-deal profit outliers were kept - they are real deals, not errors.",
    "<b>Caveat:</b> 2013 only has Sep-Dec while 2014 has 12 months, so raw year totals are not comparable. Like-for-like (Sep-Dec) is used instead."])

S += [Paragraph("3. Method", H2),
      Paragraph("Each question was answered twice - once in <b>SQL</b> (12 queries in <i>sql/queries.sql</i>, run on SQLite) and once in <b>pandas</b> - and the results were "
                "cross-checked in code. Summaries were then rebuilt in <b>Excel</b> with live SUMIFS formulas and charts, and visualised in a <b>BI dashboard</b>.", B)]

S += [PageBreak(), Paragraph("4. Key findings", H2)]
S += [Paragraph("4.1 Segment performance", H2), table(seg_t, [4*cm, 3*cm, 3*cm, 2.3*cm, 3.5*cm]), Spacer(1, 6), img("02_segment_sales_profit.png", 13.5)]
S += bullets(["Government: 44% of sales, 67% of profit, 21.7% margin - the core of the business.",
    "Channel Partners: 73% margin but only $1.8M sales - high quality, low volume.",
    "Small Business: $42.4M sales but only 9.8% margin - volume without much profit.",
    "<b>Enterprise: negative margin (-3.1%); all 58 loss-making deals are Enterprise.</b>"])
S += [PageBreak(), Paragraph("4.2 Why Enterprise loses money", H2), img("06_enterprise_margin_by_discount.png", 12.5)]
S += bullets(["Enterprise sale price is 125 per unit against a unit cost of 120 - a gross margin of only <b>4%</b> before any discount.",
    "Discounts range 5-15% on the loss-making deals, so even a Low/Medium discount can wipe out the margin. High-band Enterprise deals run at -9.5%.",
    "Total losses on these 58 deals: <b>$0.78M</b>. Fixing Enterprise pricing is the single clearest profit lever."])
S += [Paragraph("4.3 Discounts erode margin", H2), table(bd_t, [3.2*cm, 2*cm, 3*cm, 3*cm, 2.5*cm, 2.5*cm]), Spacer(1, 6), img("05_discount_band_margin.png", 12.5)]
S += bullets(["Margin falls steadily as discounts deepen: 21.9% -> 17.9% -> 14.4% -> 9.1%.",
    "High-band deals are 35% of all deals and account for $5.3M of the $9.2M total discounts.",
    "All 58 loss-making deals sit in the Medium (25) and High (33) bands."])
S += [PageBreak(), Paragraph("4.4 Country and product", H2), img("03_country_profit.png", 12), img("04_product_sales.png", 12)]
S += bullets(["USA: highest sales ($25.0M) but lowest margin (12.0%) and the highest discount rate (8.2%).",
    "France and Germany: best margins (15.5-15.7%) with the lowest discount rates (5.7-6.6%).",
    "Paseo is the top product (28% of sales, $4.8M profit). Product margins are close (12.6-15.9%), so segment and discounting matter more than product mix."])
S += [PageBreak(), Paragraph("4.5 Trend and seasonality", H2), img("01_monthly_trend.png", 14)]
S += bullets(["October and December 2014 were the strongest months ($12.4M and $12.0M); November 2014 was weak ($5.4M).",
    "Like-for-like Sep-Dec: <b>$36.2M in 2014 vs $26.4M in 2013 (+37%)</b>; profit $5.4M vs $3.9M."])
S += [Paragraph("4.6 Segment x country profit", H2), img("07_segment_country_heatmap.png", 12.5)]

S += [PageBreak(), Paragraph("5. Dashboard", H2), Image(str(ROOT/"bi"/"dashboard_preview.png"), width=17*cm, height=17*cm*10/16.4),
      Paragraph("Dashboard layout: 6 KPI cards, trend, segment, country, product, discount and Enterprise views, with slicers for Year, Segment, Country, Product and Discount Band. "
                "The interactive version is <i>bi/dashboard.html</i>; Power BI steps and DAX measures are in <i>bi/POWERBI_GUIDE.md</i>.", SM)]

S += [Paragraph("6. Recommendations", H2)]
S += bullets(["<b>Fix Enterprise pricing:</b> raise the 125 list price or cap Enterprise discounts at about 4% (the break-even point). Require approval for anything above.",
    "<b>Introduce a discount policy:</b> margin drops by half in the High band. Cap discounts for Small Business and Enterprise first; review whether High-band discounts actually lift volume enough.",
    "<b>Protect and grow Government</b> - it generates two-thirds of profit; concentration is also a risk, so diversify.",
    "<b>Grow Channel Partners and Midmarket</b> - 73% and 28% margins but under 4% of sales combined.",
    "<b>USA:</b> investigate why discounts are highest and margin lowest; align with France/Germany practices.",
    "<b>Plan for seasonality:</b> stock and staff for October and December peaks; look at why November dips."])

S += [Paragraph("7. Limitations", H2)]
S += bullets(["Only 16 months of data and only 4 months in 2013 - trends and YoY growth should be treated with caution.",
    "The dataset has no customer, region-within-country or cost-breakdown fields, so causes (e.g. why Enterprise is priced at 125) cannot be confirmed from data alone.",
    "'Manufacturing Price' is a per-product constant that does not reconcile with COGS, so COGS was used for all profit analysis."])
doc.build(S); print("saved report/Final_Report.pdf")
