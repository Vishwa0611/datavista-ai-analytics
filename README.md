# DataVista — AI Analytics Workbench

Upload any business CSV and get a complete analysis — quality check, cleaning, KPIs, charts, statistics and a downloadable report.

Built as a portfolio project for Data Analyst roles. Works with sales, marketing, HR, SaaS and sports data.

**Live Demo:** https://datavista-ai-analytics.streamlit.app/

---

## 🚀 Quick Demo

No upload needed — try sample data in 5 seconds:

| Dataset | Rows | Best For |
|---------|------|----------|
| 🛒 E-commerce Sales | 12.5k | Revenue, profit, AOV, margin, RFM |
| 📣 Marketing Campaigns | 3.4k | CTR, ROAS, CPA, funnel |
| 💳 SaaS Customers | 5.8k | Churn, MRR, retention |

> Also tested with external files like Superstore (9.9k rows) and FIFA 2026 (54k rows) — works with any business CSV up to 200MB.

Click **Load** on home page → see full dashboard.

---

## ✨ What you get

| Feature | What it does |
|---------|--------------|
| 🔍 Quality Check | Missing, duplicates, outliers (IQR), inconsistent labels — score 0-100 |
| 🧹 Cleaning | Remove dupes, fill missing, trim spaces — with log, original never changed |
| 📊 EDA | Smart charts only — histogram, box plot, bar, line, heatmap, Pareto |
| 🎯 KPIs | Auto detects domain and shows right metrics: Sales/Revenue, Profit, AOV, Margin, Discount, CTR, ROAS, Churn, Goals etc |
| 📈 Statistics | Correlation (Pearson/Spearman), t-test, ANOVA, chi-square, p < 0.001 formatting |
| 🧩 Segmentation | RFM (Champions, Loyal, At Risk, Lost), Pareto 80/20 |
| ⏱️ Time Series | Monthly trend, MoM/YoY growth, peak months, forecast marked as estimate |
| 💡 Insights | Finding → Evidence → Meaning → Action — traceable to numbers |
| 💬 Ask Data | Type "Show monthly sales" → generates SQL + table + chart |
| 🗄️ SQL Lab | 10+ queries with CTEs, window functions RANK/LAG, GROUP BY, HAVING |
| 📄 Report | 10-section HTML report + cleaned CSV download |

---

## 🛠️ Tech Stack

| Tool | Why used |
|------|----------|
| Python, pandas | Clean messy data, handle encoding |
| DuckDB | Run SQL fast in memory, shows CTEs and window functions |
| Plotly | Interactive charts |
| Streamlit | Web app framework |
| SciPy | Statistical tests |
| Jinja2 | HTML report |

---

## 📁 Project Structure

```
DataVista/
├── streamlit_app.py      # Run this file
├── pages/                # 14 pages (Upload, Profiling, Quality...)
├── app/
│   ├── main.py           # Home page
│   ├── components/       # Sidebar with navigation + back button
│   └── ui/               # Theme and styling
├── src/                  # Core logic (ingestion, profiling, quality, etc.)
├── sample_data/          # 3 sample CSVs
├── tests/                # Basic tests
├── requirements.txt
└── Dockerfile
```

---

## ▶️ How to run in VS Code

```bash
# 1. Extract ZIP and open folder in VS Code

# 2. Create virtual env
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 3. Install
pip install -r requirements.txt

# 4. Run
streamlit run streamlit_app.py
# Open http://localhost:8501
```

---

## 📤 What data works best?

| Need | Example | For |
|------|---------|-----|
| 🔢 Number column | sales, profit, quantity, market_value | Charts, KPIs, stats |
| 🔤 Category | product, region, department, team | Bar charts, Pareto, segmentation |
| 📅 Date | order_date, match_date | Monthly trend, MoM/YoY, forecast |
| 🆔 ID | order_id, customer_id | Counts, RFM |

Works best with: E-commerce, Superstore, Marketing, HR attrition, SaaS, Sports stats, Finance

If only 1 column, some pages show "unavailable reason" instead of fake charts.

**Supported:** CSV, XLSX (pick sheet), XLS, JSON, Parquet — up to 200MB

---

## 🌐 How to deploy

**GitHub:**
```bash
git init
git add .
git commit -m "Initial commit - DataVista"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/datavista-analytics.git
git push -u origin main
```

---

## ⚠️ Limitations

- 200MB max — for 10M+ rows use BigQuery/Polars
- No login — data stays in memory, not saved after close
- PII detection is basic (email/phone), not names — handle Customer Name carefully
- Domain detection is keyword based
- Forecasts are simple estimates, marked as estimate
- Correlation ≠ causation — app always warns
- Outliers are statistical anomalies, not automatically errors

---

## 🙏 AI Assistance Disclosure

Few things in this project were built with the help of AI:

- Initial code structure and some boilerplate for data profiling and quality checks
- Some chart templates and SQL query examples
- In few analysis, AI helps to generate the report summary and insights wording — but all numbers come from your actual file, no hallucinated metrics. Every insight shows evidence from calculated results.

That's why it's called **AI Analytics Workbench** — AI assists in analysis and reporting, but the core calculations are deterministic and traceable.

---

## 👤 Author

**Project made by Ayush Vishwakarma**

- GitHub: https://github.com/Vishwa0611
- LinkedIn: https://www.linkedin.com/in/ayush-vishwakarma06/


