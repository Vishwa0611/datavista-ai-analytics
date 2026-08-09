# Testing

## Unit Tests

Located in `tests/` — pytest style, also runnable via `python tests/test_*.py`

- test_ingestion: valid CSV, invalid extension, empty file, Excel sheets, JSON
- test_quality: missing detection, duplicate detection, perfect score
- test_kpi: total revenue sum, AOV ratio, missing columns handling
- test_statistics: correlation strong (a vs 2a), t-test significant groups
- test_cleaning: remove duplicates, fill missing median, trim whitespace
- test_sql: register table and query SUM, showcase generation

## Edge Cases Covered

- Empty dataset → quality score 0, EDA unavailable reason
- One-column dataset → only categorical analysis, correlation unavailable
- Missing values 7.2% → detected, suggested median/mode, log
- Duplicate records 12 → detected, suggested removal, log
- Invalid dates (N/A, blank) → date parsing fails, validity issue, cleaning parse_dates
- Mixed data types (numeric col with strings) → safe_numeric_conversion tries, validity warning
- Very small dataset (<10 rows) → correlation requires >=5 rows, hypothesis tests require >=10 per group, graceful unavailable
- Large dataset sampling: EDA chart_point limit 50k sample with disclaimer, but KPIs via DuckDB full
- No numerical columns → numerical EDA unavailable, correlation unavailable, but categorical works
- No categorical columns → categorical EDA unavailable

## How to Run

```
pip install -r requirements.txt
pytest tests/ -v
# Or
python -m pytest tests/ --tb=short
```

## Manual Testing Checklist

- Upload CSV, XLSX, JSON, Parquet
- Try demo datasets e-commerce, marketing, saas
- Check profiling detects domain correctly
- Quality score changes after cleaning
- Transformation log shows before/after
- EDA charts render for numeric/categorical/date
- KPIs calculable count matches expectation
- Statistics tests show H0/H1 and p-value
- Segmentation shows RFM if customer+date+monetary else unavailable reason
- Time series shows MoM/YoY if date+numeric else reason
- AI insights traceable, no invented numbers
- Ask Data generates SQL, shows table + chart
- SQL Lab showcase queries run
- Report HTML generation and download
- Export cleaned CSV

## Performance

- 12K rows ecommerce: pipeline ~5 sec
- 100K rows: ~15 sec with sampling for charts
- 200MB limit enforced, warning >100MB
