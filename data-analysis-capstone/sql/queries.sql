-- Table name: sales   (loaded from data/cleaned_data.csv by src/02_analysis.py)
-- Each query starts with "-- name: <id>" so the Python script can run and export them.

-- name: q1_kpi_overview
SELECT COUNT(*)                                   AS transactions,
       ROUND(SUM(units_sold),0)                   AS units_sold,
       ROUND(SUM(gross_sales),0)                  AS gross_sales,
       ROUND(SUM(discounts),0)                    AS discounts,
       ROUND(SUM(sales),0)                        AS net_sales,
       ROUND(SUM(cogs),0)                         AS cogs,
       ROUND(SUM(profit),0)                       AS profit,
       ROUND(100.0*SUM(profit)/SUM(sales),2)      AS profit_margin_pct,
       ROUND(100.0*SUM(discounts)/SUM(gross_sales),2) AS discount_rate_pct
FROM sales;

-- name: q2_by_segment
SELECT segment,
       ROUND(SUM(sales),0)   AS net_sales,
       ROUND(SUM(profit),0)  AS profit,
       ROUND(100.0*SUM(profit)/SUM(sales),1) AS margin_pct,
       ROUND(100.0*SUM(sales)/(SELECT SUM(sales) FROM sales),1)  AS share_of_sales_pct,
       ROUND(100.0*SUM(profit)/(SELECT SUM(profit) FROM sales),1) AS share_of_profit_pct
FROM sales GROUP BY segment ORDER BY profit DESC;

-- name: q3_by_country
SELECT country,
       ROUND(SUM(sales),0)  AS net_sales,
       ROUND(SUM(profit),0) AS profit,
       ROUND(100.0*SUM(profit)/SUM(sales),1)      AS margin_pct,
       ROUND(100.0*SUM(discounts)/SUM(gross_sales),1) AS discount_rate_pct
FROM sales GROUP BY country ORDER BY profit DESC;

-- name: q4_by_product
SELECT product,
       ROUND(SUM(units_sold),0) AS units,
       ROUND(SUM(sales),0)      AS net_sales,
       ROUND(SUM(profit),0)     AS profit,
       ROUND(100.0*SUM(profit)/SUM(sales),1) AS margin_pct
FROM sales GROUP BY product ORDER BY net_sales DESC;

-- name: q5_discount_band_effect
SELECT discount_band,
       COUNT(*)                                   AS deals,
       ROUND(100.0*SUM(discounts)/SUM(gross_sales),1) AS avg_discount_pct,
       ROUND(SUM(sales),0)                        AS net_sales,
       ROUND(SUM(profit),0)                       AS profit,
       ROUND(100.0*SUM(profit)/SUM(sales),1)      AS margin_pct,
       SUM(CASE WHEN profit < 0 THEN 1 ELSE 0 END) AS loss_making_deals
FROM sales
GROUP BY discount_band
ORDER BY CASE discount_band WHEN 'None' THEN 0 WHEN 'Low' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END;

-- name: q6_monthly_trend
SELECT month,
       ROUND(SUM(sales),0)  AS net_sales,
       ROUND(SUM(profit),0) AS profit
FROM sales GROUP BY month ORDER BY month;

-- name: q7_loss_making_deals
SELECT segment, discount_band,
       COUNT(*) AS loss_deals,
       ROUND(SUM(profit),0) AS total_loss
FROM sales WHERE profit < 0
GROUP BY segment, discount_band ORDER BY total_loss;

-- name: q8_enterprise_by_discount
SELECT discount_band,
       COUNT(*) AS deals,
       ROUND(SUM(sales),0)  AS net_sales,
       ROUND(SUM(profit),0) AS profit,
       ROUND(100.0*SUM(profit)/SUM(sales),1) AS margin_pct
FROM sales WHERE segment = 'Enterprise'
GROUP BY discount_band;

-- name: q9_segment_country_profit_matrix
SELECT segment, country, ROUND(SUM(profit),0) AS profit
FROM sales GROUP BY segment, country ORDER BY segment, profit DESC;

-- name: q10_top5_deals
SELECT segment, country, product, date, ROUND(sales,0) AS net_sales, ROUND(profit,0) AS profit
FROM sales ORDER BY profit DESC LIMIT 5;

-- name: q11_like_for_like_sep_dec
SELECT year,
       ROUND(SUM(sales),0)  AS net_sales,
       ROUND(SUM(profit),0) AS profit
FROM sales WHERE month_number BETWEEN 9 AND 12
GROUP BY year ORDER BY year;

-- name: q12_ranked_products_within_segment
SELECT segment, product, ROUND(SUM(profit),0) AS profit,
       RANK() OVER (PARTITION BY segment ORDER BY SUM(profit) DESC) AS rank_in_segment
FROM sales GROUP BY segment, product
ORDER BY segment, rank_in_segment;
