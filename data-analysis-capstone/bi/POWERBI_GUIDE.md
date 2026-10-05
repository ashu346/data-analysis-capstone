# Build the dashboard in Power BI (or Tableau)

`dashboard_preview.png` shows the target layout. Power BI Desktop files (.pbix) can only be created inside Power BI Desktop, so follow these steps (about 30-40 minutes). Use `data/cleaned_data.csv` or `excel/Sales_Analysis.xlsx` (sheet **Data**) as the source.

## 1. Load data
Home -> Get data -> Text/CSV -> `data/cleaned_data.csv` -> **Transform data**.
Check types: `date` = Date, money columns = Fixed decimal number, `units_sold` = Whole/Decimal number. Close & Apply.
(Make sure `discount_band` shows the text **None**, not null.)

## 2. DAX measures (Modeling -> New measure)
```DAX
Net Sales      = SUM(cleaned_data[sales])
Gross Sales    = SUM(cleaned_data[gross_sales])
Profit         = SUM(cleaned_data[profit])
Units Sold     = SUM(cleaned_data[units_sold])
Discounts      = SUM(cleaned_data[discounts])
Profit Margin  = DIVIDE([Profit], [Net Sales])
Discount Rate  = DIVIDE([Discounts], [Gross Sales])
Loss Deals     = CALCULATE(COUNTROWS(cleaned_data), cleaned_data[profit] < 0)
Sales Share    = DIVIDE([Net Sales], CALCULATE([Net Sales], ALL(cleaned_data[segment])))
Profit Share   = DIVIDE([Profit], CALCULATE([Profit], ALL(cleaned_data[segment])))
```
Calculated column for sorting discount bands (Table view -> New column):
```DAX
Band Order = SWITCH(cleaned_data[discount_band], "None",0, "Low",1, "Medium",2, "High",3)
```
Select `discount_band` column -> Column tools -> **Sort by column** -> `Band Order`.

## 3. Page layout (matches dashboard_preview.png)
| Visual | Type | Fields |
|---|---|---|
| 6 KPI cards | Card | Net Sales, Profit, Profit Margin, Units Sold, Discount Rate, Loss Deals |
| Monthly trend | Line and clustered column | X: `month`; column: Net Sales; line: Profit |
| Segment | Clustered column | X: `segment`; Y: Net Sales, Profit |
| Country | Clustered column | X: `country`; Y: Profit (tooltip: Profit Margin) |
| Product | Bar | Y: `product`; X: Net Sales |
| Discount band | Column | X: `discount_band`; Y: Profit Margin |
| Enterprise view | Column | X: `discount_band`; Y: Profit Margin; **visual-level filter** segment = Enterprise |
| Heatmap (optional) | Matrix | Rows: segment; Columns: country; Values: Profit; Conditional formatting -> background colour scale |

## 4. Filters / slicers
Add slicers: **year**, **segment**, **country**, **product**, **discount_band**. (Tip: View -> Sync slicers if you add more pages.)
Optional: add a drill-through page for Segment.

## 5. Formatting tips
Theme colours: navy `#1F2D3D`, gold `#C9A24D`, teal `#0F7B6C`, red `#C0392B` (use red for losses). Title: "Sales & Profitability Dashboard". Turn off gridlines, keep fonts consistent, format Profit Margin as 0.0%.

## 6. Export for submission
- Save the `.pbix` into this `bi/` folder (GitHub accepts files up to 100 MB).
- File -> Export -> PDF, or take screenshots into `bi/`.
- Record a 1-3 minute screen recording (Win+G or OBS) while clicking the slicers and explaining insights (see `report/Stakeholder_Summary.md`). Upload it to the repo or link it in the README.

## Tableau equivalent
Connect to the CSV -> create calculated fields: `Profit Margin = SUM([profit])/SUM([sales])`, `Discount Rate = SUM([discounts])/SUM([gross_sales])`, `Loss Deals = SUM(IF [profit]<0 THEN 1 ELSE 0 END)`. Build the same sheets, combine in a Dashboard, add filters from the Year/Segment/Country/Product/Discount Band fields.
