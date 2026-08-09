"""
KPI Engine — domain-aware.
"""
import pandas as pd
from typing import List, Dict
from ..utils.constants import DOMAIN_KPI_CONFIG, Domain
from .calculator import calculate_kpi
from ..validation.schema import KPIResult, ModuleResult

def run_kpi_analysis(
    df: pd.DataFrame,
    detected_domain: str,
    profile_result
) -> ModuleResult:
    """
    Calculate KPIs based on detected domain.
    If domain unknown, try all domains but filter available.
    """
    try:
        kpis_to_calc = []
        domain_enum = detected_domain if detected_domain in DOMAIN_KPI_CONFIG else Domain.UNKNOWN.value

        if domain_enum in DOMAIN_KPI_CONFIG:
            kpis_to_calc = DOMAIN_KPI_CONFIG[domain_enum]
        else:
            # Try all domains, collect unique KPI names
            seen = set()
            for dom, kpis in DOMAIN_KPI_CONFIG.items():
                for kpi in kpis:
                    if kpi["name"] not in seen:
                        kpis_to_calc.append(kpi)
                        seen.add(kpi["name"])

        results: List[KPIResult] = []
        for kpi_cfg in kpis_to_calc:
            res = calculate_kpi(df, kpi_cfg)
            results.append(res)

        # Sort: available first, then by name
        results_sorted = sorted(results, key=lambda x: (not x.available, x.name))

        # Summary
        available_count = sum(1 for r in results if r.available)
        total_count = len(results)

        data = {
            "detected_domain": detected_domain,
            "kpis": results_sorted,
            "available_count": available_count,
            "total_count": total_count,
            "summary": f"{available_count}/{total_count} KPIs calculable from detected columns"
        }

        return ModuleResult(available=True, data=data)

    except Exception as e:
        return ModuleResult(available=False, reason=f"KPI calculation failed: {e}")
