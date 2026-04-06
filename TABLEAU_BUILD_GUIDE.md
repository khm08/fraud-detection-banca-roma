# Banca Roma Digitale - Tableau Dashboard Build Guide
## Author: Kareem Makki

---

## QUICK START
1. Open `Banca_Roma_Fraud_Detection.twbx` in Tableau Desktop or Tableau Public
2. The data is pre-loaded with 50,000 transactions and 42 columns
3. Follow the steps below to build each visualization
4. Combine all sheets into the "Fraud Intelligence Dashboard"

---

## PRE-BUILT CALCULATED FIELDS (already in the workbook)
- **Fraud Rate**: `AVG([is_fraud])` → format as percentage
- **Fraud Count**: `SUM([is_fraud])`
- **Total Fraud Amount**: `SUM(IF [is_fraud] = 1 THEN [amount_eur] ELSE 0 END)`
- **Number of Records**: `1`

## ADDITIONAL CALCULATED FIELDS TO CREATE
In Tableau, right-click on the data pane → Create Calculated Field:

1. **Fraud Rate %**: `AVG([is_fraud]) * 100`
2. **Avg Fraud Amount**: `SUM(IF [is_fraud]=1 THEN [amount_eur] ELSE 0 END) / SUM([is_fraud])`
3. **Foreign Flag**: `IF [transaction_country] != 'IT' THEN 'Foreign' ELSE 'Domestic' END`
4. **Risk Score**: `IF [is_fraud]=1 THEN 'Fraud' ELSE 'Legitimate' END`

---

## SHEET 1: Monthly Fraud Trend (Combo Chart)
**Type**: Dual-axis bar + line

1. Drag `Month` to Columns
2. Drag `Fraud Count` (SUM of is_fraud) to Rows
3. Drag `Fraud Rate` to Rows (right side → Dual Axis)
4. Right-click second axis → Synchronize Axis → uncheck
5. Change `Fraud Count` mark type to **Bar** (color: #06B6D4 cyan)
6. Change `Fraud Rate` mark type to **Line** (color: #F43F5E rose)
7. Format: Dark background (#0F172A), white grid lines

---

## SHEET 2: Fraud by Type (Horizontal Bar)
**Type**: Horizontal bar chart

1. Drag `Fraud Type (Clean)` to Rows
2. Drag `Fraud Count` to Columns
3. Sort descending by Fraud Count
4. Color by `Fraud Type (Clean)` with custom palette:
   - Account Takeover: #EF4444 (red)
   - Phishing ATO: #8B5CF6 (purple)
   - Card Not Present: #F97316 (orange)
   - Card Present: #3B82F6 (blue)
   - First Party: #F59E0B (amber)
   - Money Mule: #06B6D4 (cyan)
   - Synthetic Identity: #10B981 (green)
5. Add `Fraud Count` label to bars

---

## SHEET 3: Financial Exposure (Bar Chart)
**Type**: Horizontal bar chart

1. Filter: `is_fraud = 1`
2. Drag `Fraud Type (Clean)` to Rows
3. Drag `SUM(amount_eur)` to Columns
4. Sort descending
5. Format amounts as EUR currency
6. Same color palette as Sheet 2
7. Add labels: `SUM(amount_eur)` formatted as €#,##0

---

## SHEET 4: Channel Fraud Rate (Bar Chart)
**Type**: Horizontal bar chart

1. Drag `Channel` to Rows
2. Drag `Fraud Rate %` to Columns
3. Sort descending
4. Color gradient: low (#10B981 green) to high (#EF4444 red)
5. Add labels showing the percentage

---

## SHEET 5: Hourly Fraud Pattern (Area Chart)
**Type**: Area chart

1. Drag `Hour` to Columns (as Dimension, not continuous)
2. Drag `Fraud Rate %` to Rows
3. Mark type: Area
4. Color: #8B5CF6 purple with 20% opacity fill
5. Add trend line (polynomial, degree 4)

---

## SHEET 6: Card Present vs Not Present (Pie/Donut)
**Type**: Pie chart

1. Filter: `is_fraud = 1`
2. Drag `Card Presence` to Color
3. Drag `Fraud Count` to Angle
4. Colors: Card Not Present (#EF4444), Card Present (#3B82F6)
5. Add labels: percentage and count

---

## SHEET 7: Country Breakdown (Map or Bar)
**Type**: Bar chart or filled map

### Bar version:
1. Filter: `is_fraud = 1`
2. Drag `Transaction Country` to Rows
3. Drag `Fraud Count` to Columns
4. Sort descending
5. Color: Italy = #10B981 (green), all others = #EF4444 (red)

### Map version:
1. Drag `Transaction Country` to the canvas (auto-generates map)
2. Drag `Fraud Count` to Color
3. Color gradient: white to red

---

## SHEET 8: Amount Distribution (Histogram)
**Type**: Stacked bar chart

1. Drag `Amount Bucket` to Columns
2. Drag `Number of Records` to Rows
3. Drag `Fraud Label` to Color
4. Colors: Legitimate (#3B82F6), Fraud (#EF4444)
5. Stack marks

---

## SHEET 9: KPI Text Sheets (create 6 separate sheets)
For each KPI, create a new sheet:

### KPI: Total Transactions
1. Drag `Number of Records` to Text
2. Format: 28pt bold, #3B82F6 blue
3. Add subtitle: "24-month period"

### KPI: Fraud Detected
1. Drag `Fraud Count` to Text
2. Format: 28pt bold, #EF4444 red

### KPI: Total Exposure
1. Drag `Total Fraud Amount` to Text
2. Format: €#,##0, 28pt bold, #F59E0B amber

### KPI: Fraud Rate
1. Drag `Fraud Rate` to Text
2. Format: 0.00%, 28pt bold, #F43F5E rose

### KPI: Avg Fraud Amount
1. Drag `Avg Fraud Amount` to Text
2. Format: €#,##0, 28pt bold

### KPI: Detection Rate
1. Create calculated field: `0.943` (static, from model results)
2. Format: 94.3%, 28pt bold, #10B981 green

---

## DASHBOARD ASSEMBLY

1. Create new Dashboard → Size: Fixed 1400 x 900
2. Set background to dark: #0F172A

### Layout (top to bottom):
**Row 1 - Header** (height ~60px):
- Text object: "BANCA ROMA DIGITALE" (gold #D4A853, 18pt bold)
- Text object: "Fraud Intelligence Dashboard | Kareem Makki | 2024-2025"

**Row 2 - KPIs** (height ~80px):
- 6 KPI sheets side by side in a horizontal container
- Each with colored top border using container padding

**Row 3 - Main Charts** (height ~300px):
- Left 65%: Monthly Fraud Trend
- Right 35%: Fraud by Type (pie/donut)

**Row 4 - Exposure** (height ~120px):
- Full width: Financial Exposure horizontal bars

**Row 5 - Detail Charts** (height ~250px):
- 3 columns: Channel Analysis | Hourly Pattern | CP vs CNP

**Row 6 - Footer** (height ~30px):
- Text: "CONFIDENTIAL | Banca Roma Digitale | Fraud Intelligence Division | 2025"

### Dashboard Formatting:
- Background: #0F172A (dark navy)
- All sheet backgrounds: transparent or #111827
- Title font: Tableau Bold, white
- Axis labels: #94A3B8 (light gray)
- Grid lines: #1E293B (subtle dark)
- Border on containers: #1E293B, 1px

### Color Palette (add as custom Tableau palette):
Edit Preferences.tps in My Tableau Repository:
```xml
<color-palette name="Banca Roma Digitale" type="regular">
  <color>#EF4444</color>
  <color>#3B82F6</color>
  <color>#8B5CF6</color>
  <color>#F97316</color>
  <color>#F59E0B</color>
  <color>#06B6D4</color>
  <color>#10B981</color>
  <color>#F43F5E</color>
  <color>#D4A853</color>
</color-palette>
```

---

## FILTERS TO ADD TO DASHBOARD
- Year (single select dropdown)
- Channel (multi-select)
- Fraud Type (multi-select)
- Card Presence (single select)

Apply all filters to "All Using This Data Source"

---

## INTERACTIVITY
- Enable "Use as Filter" on the Fraud by Type chart
- Enable "Use as Filter" on the Country Breakdown
- Add highlight actions between all sheets
- Tooltip: show Transaction ID, Amount, Fraud Type, Channel

---

## PUBLISH
- Save as .twbx (packaged with data)
- Or publish to Tableau Public: public.tableau.com
- Title: "Banca Roma Digitale - Fraud Intelligence Dashboard"
- Tags: fraud detection, banking, machine learning, financial analytics
