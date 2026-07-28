# Executive Business Visualizations Documentation

## Overview

This repository contains five production-ready, professional business visualizations designed to convert data into immediate, actionable decision-making insights for stakeholders. Every chart follows core visualization principles: matching chart types to data relationships, complete self-explanatory labeling, a unified color palette, explicit accessibility considerations, and targeted insight annotations.

---

## 1. Consistent Colour Palette & Accessibility System

### Unified Colour Palette (`PALETTE`)

| Role | Colour Hex | Description & Usage Rationale |
|---|---|---|
| **Primary** | `#1f77b4` | Deep Professional Blue — Used for baseline metrics, top category bars, primary line series, histogram density, and scatter plot observation points. |
| **Secondary** | `#ff7f0e` | Energetic Orange — Used for secondary growth series (Cloud SaaS), KDE distribution overlays, regression trendlines, and growth callouts. |
| **Success** | `#2ca02c` | Forest Green — Used for positive performance benchmarks, baseline growth products, and target achievements. |
| **Danger** | `#d62728` | Crimson Red — Used for critical threshold lines, seasonal dips, negative anomalies, and outlier highlights. |
| **Purple** | `#9467bd` | Royal Purple — Used for secondary stacked product categories (Professional Services). |
| **Neutral** | `#7f7f7f` | Slate Gray — Used for grid lines, average benchmarks, and background context elements. |

### Color Blindness & Accessibility Considerations
- **Non-Color Encoding**: Color is never the sole communicator of information.
  - Line charts utilize distinct geometric markers (`'o'`, `'s'`, `'^'`) and line styles (`'-'`, `'--'`, `'-.'`).
  - Bar charts and stacked segments include direct textual data labels (`$6.2M`, `$4.8M`).
  - Reference lines use distinct line patterns (dashed `--`, dotted `:`).
- **High Contrast**: All text annotations and axis labels adhere to high WCAG contrast ratios against light backgrounds (`#ffffff` and `#f8f9fa`).

---

## 2. Comprehensive Chart Breakdown

### Chart 1: Q4 Revenue by Product Line
- **File Name:** `chart1_revenue_by_product.png`
- **Chart Type:** Horizontal Bar Chart
- **Business Question:** Which product line generated the most revenue in Q4?
- **Why Chosen:** A horizontal bar chart allows instant comparison across discrete categories. Horizontal orientation provides ample room for long category names without text truncation or rotation.
- **Complete Labelling:**
  - **Title:** Q4 Revenue by Product Line (Category Comparison)
  - **X-axis:** Revenue ($ Millions) — formatted as `$xM`
  - **Y-axis:** Product Line
  - **Data Labels:** Precise dollar values (`$6.2M`, `$4.8M`, `$3.5M`, `$2.4M`, `$1.9M`) placed at the end of each bar.
- **Key Insight:** `Enterprise Suite` is the top revenue generator, contributing `$6.2M` (32.9% of total Q4 revenue).
- **Annotation:**
  - **Top Performer Callout:** Red arrow pointing to `Enterprise Suite` (`$6.2M, 32.9% of Total`).
  - **Reference Line:** Dashed gray vertical line indicating the average product revenue (`$3.78M`).

---

### Chart 2: 12-Month Revenue Trend
- **File Name:** `chart2_revenue_trend.png`
- **Chart Type:** Multi-Series Line Chart
- **Business Question:** How has monthly revenue trended across top product lines over the last 12 months?
- **Why Chosen:** Line charts are built specifically for continuous temporal data. The connected lines emphasize continuity, rate of change, and seasonal trajectories.
- **Complete Labelling:**
  - **Title:** Monthly Revenue Trend for Top 3 Product Lines (Last 12 Months)
  - **X-axis:** Month (2024)
  - **Y-axis:** Monthly Revenue ($ Millions) — formatted as `$xM`
  - **Legend:** Positioned upper left with white background to prevent data overlap.
- **Key Insight:** `Cloud SaaS` demonstrated steady, compound growth of 108% over the year (expanding from `$1.2M` in Jan to `$2.5M` in Dec), narrowing the gap with `Enterprise Suite`.
- **Annotation:**
  - **Seasonal Anomaly:** Yellow box & red arrow marking the "August Dip" (`$1.7M`), caused by annual European summer slowdown.
  - **Target Line:** Dotted red horizontal reference line marking the `$2.0M` monthly growth target.
  - **Growth Callout:** Orange callout celebrating `Cloud SaaS` 108% growth trajectory.

---

### Chart 3: Customer Order Value Distribution
- **File Name:** `chart3_order_value_distribution.png`
- **Chart Type:** Histogram with Kernel Density Estimate (KDE) Overlay
- **Business Question:** What is the typical customer order value and how are orders distributed across price tiers?
- **Why Chosen:** A histogram exposes the shape of distribution (skewness, modality, outliers) that single summary metrics (like simple averages) obscure.
- **Complete Labelling:**
  - **Title:** Customer Order Value Distribution (Bimodal Pattern Analysis)
  - **X-axis:** Order Value ($ USD) — formatted with dollar signs (`$x`)
  - **Y-axis:** Number of Orders (Frequency)
  - **Legend:** Distinguishes frequency bins, KDE curve, and median threshold line.
- **Key Insight:** Order values follow a strong **bimodal distribution**: a major peak of SMB/self-serve purchases around `$150` and a secondary peak of Enterprise bundles around `$650`.
- **Annotation:**
  - **Peak Callout 1:** Arrow marking SMB Peak (`~ $150 Mode`).
  - **Peak Callout 2:** Arrow marking Enterprise Peak (`~ $650 Mode`).
  - **Median Line:** Dashed red reference line marking the median order value (`$345`).

---

### Chart 4: Quarterly Revenue Composition
- **File Name:** `chart4_revenue_composition.png`
- **Chart Type:** Stacked Bar Chart
- **Business Question:** How does quarterly revenue break down by product line, and how is product mix shifting over time?
- **Why Chosen:** Stacked bars communicate part-to-whole relationships over discrete time blocks (quarters), allowing viewers to evaluate both total revenue growth and internal composition simultaneously.
- **Complete Labelling:**
  - **Title:** Quarterly Revenue Composition by Product Line (2024)
  - **X-axis:** Fiscal Quarter (Q1 2024 to Q4 2024)
  - **Y-axis:** Total Revenue ($ Millions) — formatted as `$xM`
  - **Segment Labels:** Precise segment values (`$M`) directly printed on stack segments $\ge \$2.0M$.
  - **Total Labels:** Overall quarterly totals (`$15.5M`, `$16.6M`, `$17.5M`, `$18.8M`) printed atop each bar.
- **Key Insight:** Total quarterly revenue increased by 21.3% from Q1 (`$15.5M`) to Q4 (`$18.8M`). `Cloud SaaS` expanded its contribution from 20.0% of total revenue in Q1 to 25.5% in Q4.
- **Annotation:**
  - **Composition Shift:** Orange arrow and annotation box noting `Cloud SaaS` expansion from 20% to 25.5% share.

---

### Chart 5: Marketing Spend vs. Revenue Generated
- **File Name:** `chart5_marketing_vs_revenue.png`
- **Chart Type:** Scatter Plot with Linear Trendline
- **Business Question:** Does marketing campaign spend correlate with revenue generated, and are there inefficient campaigns?
- **Why Chosen:** Scatter plots visually test relationship hypothesis between two continuous numerical variables, making clusters, trend directions, and individual outliers instantly noticeable.
- **Complete Labelling:**
  - **Title:** Marketing Spend vs. Revenue Generated (Correlation Analysis)
  - **X-axis:** Marketing Campaign Spend ($ Thousands) — formatted as `$xK`
  - **Y-axis:** Revenue Generated ($ Millions) — formatted as `$xM`
  - **Correlation Box:** Top-left summary callout displaying Pearson $r = 0.78$.
  - **Legend:** Distinguishes campaign data points and linear regression trendline.
- **Key Insight:** Marketing spend has a strong positive linear correlation with revenue ($r = 0.78$). Every `$10K` increase in marketing spend yields approximately `$0.55M` in revenue.
- **Annotation:**
  - **Outlier Highlight:** Red target ring and arrow pointing to Campaign #15 (`High Spend: $85K, Low Return: $2.1M`), identifying an underperforming promotion that requires audit.

---

## 3. Summary of Deliverables

- `assignment-35-visualizations.py`: Executable Python script generating all 5 charts.
- `output/chart1_revenue_by_product.png`: 300 DPI horizontal bar chart.
- `output/chart2_revenue_trend.png`: 300 DPI multi-line trend chart.
- `output/chart3_order_value_distribution.png`: 300 DPI histogram with KDE.
- `output/chart4_revenue_composition.png`: 300 DPI stacked bar composition chart.
- `output/chart5_marketing_vs_revenue.png`: 300 DPI scatter correlation chart.
- `output/CHARTS_README.md`: This comprehensive documentation artifact.
