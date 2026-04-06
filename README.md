# Banca Roma Digitale — Fraud Detection & Prevention System

**Author:** Kareem Makki | **Date:** 2025 | **Status:** Complete

---

## Executive Summary

End-to-end fraud detection system built for **Banca Roma Digitale**, a digital bank based in Rome, Italy. The project covers synthetic data generation, exploratory analysis, machine learning model development, rule-based strategies, graph-based fraud detection, model monitoring, and an interactive analytics dashboard.

**Key Results:**
- **Best Model AUC-ROC:** 0.9991 (Gradient Boosting)
- **Detection Rate:** 94.3% recall
- **Precision:** 97.9% (minimizing false positives)
- **Total Fraud Exposure Analyzed:** EUR 10.8M across 50,000 transactions

---

## Project Structure

```
fraud-detection-project/
|
|-- data/
|   |-- banca_roma_digitale_data.xlsx    # Raw synthetic dataset (5 sheets)
|   |-- tableau_fraud_data.csv           # Tableau-ready flat file (42 columns)
|   |-- banca_roma_fraud.db             # SQLite database with all tables
|
|-- notebooks/
|   |-- Banca_Roma_Fraud_Detection.ipynb  # Full ML pipeline (Jupyter)
|
|-- scripts/
|   |-- generate_data.py                 # Synthetic data generator
|   |-- fraud_detection_pipeline.py      # Python ML pipeline (standalone)
|   |-- fraud_analysis.sql              # SQL analysis queries (10 sections)
|
|-- dashboards/
|   |-- Banca_Roma_Fraud_Dashboard.html  # Interactive web dashboard
|   |-- Banca_Roma_Fraud_Dashboard_v2.xlsx  # Excel dashboard
|   |-- Banca_Roma_Fraud_Detection_v2.twbx  # Tableau workbook
|   |-- TABLEAU_BUILD_GUIDE.md           # Step-by-step Tableau build guide
|
|-- reports/
|   |-- fraud_detection_report.xlsx      # Model comparison & monitoring report
|   |-- Fraud_Detection_Presentation.pptx  # Executive presentation
|
|-- charts/
|   |-- 01_fraud_overview.png
|   |-- 02_cp_cnp_analysis.png
|   |-- 03_temporal_patterns.png
|   |-- 04_network_graph.png
|   |-- 05_model_comparison.png
|   |-- 06_feature_importance.png
|   |-- 07_model_monitoring.png
|
|-- README.md                            # This file
```

---

## Dataset Overview

| Table | Records | Description |
|-------|---------|-------------|
| Customers | 2,000 | Italian bank customers with KYC, income, credit scores |
| Transactions | 50,000 | 24 months of banking transactions (Jan 2024 - Dec 2025) |
| Devices | 3,983 | Device fingerprints, IPs, OS versions |
| Alerts | 2,635 | Fraud alerts with dispositions |
| Network Edges | 188 | Customer-to-customer connections for graph analysis |

### Fraud Types Covered

| Fraud Type | Count | Exposure (EUR) | Description |
|------------|-------|----------------|-------------|
| Account Takeover (ATO) | 1,013 | 5,399,153 | Unauthorized access via stolen credentials |
| Card Present Fraud | 864 | 885,386 | Counterfeit/stolen card used at POS/ATM |
| Phishing ATO | 856 | 2,130,041 | Social engineering leading to account compromise |
| Card Not Present (CNP) | 615 | 1,555,029 | Online/phone fraud without physical card |
| First Party Fraud | 408 | 701,632 | Customer-initiated false claims |
| Money Mule | 8 | 85,784 | Accounts used to launder illicit funds |
| Synthetic Identity | 3 | 16,337 | Fabricated identities for credit fraud |

---

## Technical Stack

| Category | Technologies |
|----------|-------------|
| Languages | Python 3.10+, SQL |
| ML Frameworks | Scikit-learn, NumPy, Pandas |
| Visualization | Matplotlib, Seaborn, Chart.js, Tableau |
| Database | SQLite |
| Graph Analysis | NetworkX |
| Dashboard | HTML/CSS/JS (Chart.js), Excel (openpyxl), Tableau |
| Notebook | Jupyter (ipynb) |

---

## Models & Results

### Supervised Models

| Model | AUC-ROC | Precision | Recall | F1 Score |
|-------|---------|-----------|--------|----------|
| **Gradient Boosting** | **0.9991** | **0.979** | **0.943** | **0.961** |
| Random Forest | 0.9985 | 0.973 | 0.921 | 0.947 |
| Decision Tree | 0.9788 | 0.765 | 0.954 | 0.849 |
| Logistic Regression | 0.9661 | 0.534 | 0.878 | 0.664 |

### Unsupervised Models

| Model | Precision | Recall | F1 Score |
|-------|-----------|--------|----------|
| Isolation Forest | 0.464 | 0.462 | 0.463 |

### Hybrid Model (ML + Rules)

| Approach | AUC-ROC | Precision | Recall | F1 Score |
|----------|---------|-----------|--------|----------|
| Hybrid (60% ML + 40% Rules) | 0.9969 | 0.960 | 0.910 | 0.940 |

---

## Feature Engineering (29 features)

**Transaction Features:** amount, card presence, velocity (1h/24h), response time, channel, merchant category, authentication method

**Customer Features:** age, monthly income, credit score, account age, account type, KYC status

**Risk Indicators:** foreign transaction flag, unknown device flag, no authentication flag, amount-to-income ratio, high amount flag, night transaction flag, transfer flag, crypto flag

**Graph Features:** degree centrality, neighbor count, suspicious connections, fraud cluster membership

---

## Rule-Based Strategy (10 Expert Rules)

1. High velocity (5+ transactions in 1 hour)
2. Unknown device + high amount (>EUR 500)
3. Foreign transaction + no authentication
4. Amount exceeds 3x monthly income
5. New account (<30 days) + large transfer (>EUR 1,000)
6. Night transaction + foreign origin
7. Crypto exchange + high amount (>EUR 2,000)
8. Synthetic identity flag
9. Mule account flag
10. Low response time + high amount (automated attack)

---

## Graph-Based Fraud Detection

- Built customer network graph using NetworkX
- 179 nodes, 188 edges across 72 connected components
- Identified suspicious clusters via shared devices, IPs, and phone patterns
- Fraud ring detection through community analysis
- Node-level features (degree centrality, suspicious connection count) fed into ML models

---

## Key Findings & Recommendations

1. **Account takeover is the top threat** — EUR 5.4M exposure, deploy device fingerprint validation as primary defense
2. **Card-not-present fraud dominates online channel** — 9.05% fraud rate vs 6.63% mobile
3. **Deploy Gradient Boosting for real-time scoring** — 99.91% AUC with 97.9% precision
4. **Implement graph-based monitoring** — identified 72 suspicious network clusters
5. **Tighten night-hour rules** — elevated fraud rates between 22:00-06:00
6. **Flag new accounts with large transfers** — accounts <30 days old with transfers >EUR 1,000
7. **Monitor model drift monthly** — automated dashboard tracks precision, recall, and AUC over time

---

## How to Run

### Prerequisites
```bash
pip install pandas numpy scikit-learn openpyxl networkx matplotlib seaborn
```

### Step 1: Generate Data
```bash
python generate_data.py
```

### Step 2: Run ML Pipeline
```bash
python fraud_detection_pipeline.py
# Or open Banca_Roma_Fraud_Detection.ipynb in Jupyter
```

### Step 3: Run SQL Analysis
```bash
sqlite3 banca_roma_fraud.db < fraud_analysis.sql
```

### Step 4: View Dashboard
Open `Banca_Roma_Fraud_Dashboard.html` in any web browser.

---

## Live Dashboard

[Click here to view the interactive fraud dashboard](https://khm08.github.io/fraud-detection-banca-roma/)

*(To deploy: upload the HTML file to GitHub Pages via your khm08 repository)*

---

## Contact

**Kareem Makki**
- Email: kareemmakki@gmail.com
- LinkedIn: [linkedin.com/in/kareemmakki](https://linkedin.com/in/kareemmakki)
- GitHub: [github.com/khm08](https://github.com/khm08)
- Portfolio: [datascienceportfol.io/kareemmakki](https://datascienceportfol.io/kareemmakki)
- Coursera: [Financial Reporting with Tableau](https://www.coursera.org/projects/financial-reporting-with-tableau-parameters--filters)
