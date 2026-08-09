"""
Export helpers — CSV, XLSX, PNG.
"""
import pandas as pd
from typing import Any
import io

def export_cleaned_csv(df: pd.DataFrame) -> bytes:
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    return csv_buffer.getvalue().encode('utf-8')

def export_cleaned_excel(df: pd.DataFrame) -> bytes:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='cleaned_data')
    return output.getvalue()

def export_kpi_excel(kpi_results) -> bytes:
    output = io.BytesIO()
    rows = []
    for kpi in kpi_results:
        rows.append({
            "KPI": kpi.name,
            "Formula": kpi.formula,
            "Value": kpi.value,
            "Unit": kpi.unit,
            "Interpretation": kpi.interpretation,
            "Evidence Columns": ", ".join(kpi.evidence_columns),
            "Available": kpi.available
        })
    df = pd.DataFrame(rows)
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='kpis')
    return output.getvalue()
