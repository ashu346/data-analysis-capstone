# Power BI step by step (using bi/Business_Metrics_Dashboard_PowerBI_Ready.xlsx)

Beginner guide, about 30 minutes. Power BI Desktop is free but runs only on **Windows** (Microsoft Store -> search "Power BI Desktop").
No Windows? Use **Tableau Public** (free, Windows + Mac) with the same Excel file; see the Tableau notes at the bottom.

## Step 1 - Load the data
1. Open Power BI Desktop -> **Home -> Get data -> Excel workbook** -> choose `Business_Metrics_Dashboard_PowerBI_Ready.xlsx`.
2. In the Navigator tick only **Data** (not Dashboard, not Power BI Measures) -> click **Transform Data**.

## Step 2 - Quick cleaning (Power Query window)
1. Click the **Discount Band** column header -> right-click -> **Replace Values**
   - Value to find: `null`  |  Replace with: `None`  -> OK.
   (53 rows have no discount band; this makes them show as "None" instead of "(Blank)".)
2. Check the little icon on each column header: **Date** = Date, **Sales / Profit / COGS / Gross Sales / Discounts** = Fixed decimal number, **Units Sold** = Decimal number. Change via the icon if different.
3. **Home -> Close & Apply**.

## Step 3 - Month order fix
Right-side **Data** pane -> click `Month Name` -> top menu **Column tools -> Sort by column -> Month Number**.

## Step 4 - Measures
Right-click the `Data` table in the Data pane -> **New measure** -> paste one at a time (press Enter after each):
```DAX
Total Sales   = SUM('Data'[Sales])
Total Profit  = SUM('Data'[Profit])
Total Units   = SUM('Data'[Units Sold])
Total COGS    = SUM('Data'[COGS])
Profit Margin = DIVIDE([Total Profit], [Total Sales])
Discount Rate = DIVIDE(SUM('Data'[Discounts]), SUM('Data'[Gross Sales]))
Loss Deals    = CALCULATE(COUNTROWS('Data'), 'Data'[Profit] < 0)
```
(The first five are the same as the sheet **Power BI Measures** in the file. The last two are extra.)
Select `Profit Margin` and `Discount Rate` -> Measure tools -> format as **Percentage**, 1 decimal.

## Step 5 - Build the visuals
Click an empty area of the canvas, choose the visual type in the **Visualizations** pane, then drag fields into the boxes.

| # | Visual | Drag these fields |
|---|---|---|
| 1-6 | **Card** (make 6) | Total Sales, Total Profit, Profit Margin, Total Units, Discount Rate, Loss Deals |
| 7 | **Line and clustered column chart** | X-axis: `Date` (choose "Date", not the hierarchy); Column y: Total Sales; Line y: Total Profit |
| 8 | **Clustered column chart** | X-axis: Segment; Y-axis: Total Sales, Total Profit |
| 9 | **Clustered column chart** | X-axis: Country; Y-axis: Total Profit |
| 10 | **Clustered bar chart** | Y-axis: Product; X-axis: Total Sales |
| 11 | **Clustered column chart** | X-axis: Discount Band; Y-axis: Profit Margin |
| 12 | **Table or Matrix** | Rows: Segment; Values: Total Sales, Total Profit, Profit Margin, Loss Deals |

## Step 6 - Slicers (filters)
Click empty canvas -> **Slicer** visual -> drag one field into it. Make 5 slicers: **Year, Segment, Country, Product, Discount Band**.
(Tip: Slicer settings -> Format -> Slicer settings -> Style -> **Dropdown** to save space.)

## Step 7 - Title, insights and look
- **Insert -> Text box**: title "Sales & Profitability Dashboard".
- Add a second text box with 3-4 insights from `report/Stakeholder_Summary.md`:
  Enterprise loses money (-3.1% margin) | Government = 67% of profit | High discounts cut margin to 9.1%.
- **View -> Themes** to pick colours. Use red for the loss/negative values.
- Look at `bi/dashboard_preview.png` for the layout idea.

## Step 8 - Save and export
1. **File -> Save as** -> `Sales_Dashboard.pbix` -> put it in this `bi/` folder.
2. **File -> Export -> Export to PDF** -> save as `Sales_Dashboard.pdf` in `bi/`.
3. Optional: screen-record yourself clicking the slicers for 1-3 minutes (Windows: Win + G).
4. Upload `Sales_Dashboard.pbix`, the PDF and the recording (or link) to GitHub.

## Tableau (Public) quick notes
Connect to Microsoft Excel -> choose the **Data** sheet. Create calculated fields:
`Profit Margin = SUM([Profit]) / SUM([Sales])`, `Discount Rate = SUM([Discounts]) / SUM([Gross Sales])`.
Build the same sheets, combine them in a Dashboard, and add filters for Year, Segment, Country, Product, Discount Band.

## Note about the Excel file
Its **Dashboard** sheet holds typed-in numbers (not formulas) and 3 basic charts. It is good as a Power BI source, but the real dashboard is what you build in the steps above. The richer Excel summary with live formulas is `excel/Sales_Analysis.xlsx`.
