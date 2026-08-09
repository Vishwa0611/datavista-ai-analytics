"""
Helper utilities — pure functions.
"""
import hashlib
import re
from typing import List, Optional
import pandas as pd

def compute_file_hash(content: bytes) -> str:
    """SHA256 hash for reproducibility manifest."""
    return hashlib.sha256(content).hexdigest()[:16]

def human_readable_size(num_bytes: int) -> str:
    """Convert bytes to human readable."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if num_bytes < 1024:
            return f"{num_bytes:.1f}{unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f}TB"

def normalize_column_name(col: str) -> str:
    """Lowercase, trim, replace spaces with underscore."""
    col = str(col).strip()
    col = re.sub(r'\s+', '_', col)
    col = re.sub(r'[^\w_]', '', col)
    return col.lower()

def fuzzy_column_match(target_aliases: List[List[str]], columns: List[str]) -> Optional[dict]:
    """
    Improved fuzzy matching that avoids false positives like 'sales' matching 'salesperson' when 'Total Sales' exists.
    Scoring: exact > normalized exact > whole word > substring with penalty
    """
    import re
    cols_lower = {c.lower(): c for c in columns}
    cols_norm = {c.lower().replace('_', ' ').replace('-', ' '): c for c in columns}
    
    def normalize(s):
        return s.lower().replace('_', ' ').replace('-', ' ').strip()
    
    result = {}
    for idx, alias_group in enumerate(target_aliases):
        best_match = None
        best_score = -1
        
        for alias in alias_group:
            alias_norm = alias.lower()
            alias_norm_space = normalize(alias)
            
            for col_low, orig in cols_lower.items():
                col_norm_space = normalize(col_low)
                score = -1
                
                # Exact match (case-insensitive)
                if alias_norm == col_low:
                    score = 100
                # Normalized exact (total_sales == total sales)
                elif alias_norm_space == col_norm_space:
                    score = 90
                # Alias is whole word in column (e.g., sales in "total sales")
                elif re.search(r'' + re.escape(alias_norm) + r'', col_low):
                    score = 80
                elif re.search(r'' + re.escape(alias_norm_space) + r'', col_norm_space):
                    score = 75
                # Alias is substring but check if it's part of larger unrelated word
                # Penalize if column is much longer than alias and alias is prefix of a different word
                elif alias_norm in col_low:
                    # Check if alias is at start and next char is letter (sales in salesperson)
                    # This should have lower score
                    pos = col_low.find(alias_norm)
                    next_char_is_letter = False
                    if pos + len(alias_norm) < len(col_low):
                        next_char = col_low[pos + len(alias_norm)]
                        if next_char.isalpha():
                            next_char_is_letter = True
                    
                    if next_char_is_letter:
                        # Like sales in salesperson - penalize heavily
                        score = 20
                    else:
                        # Calculate penalty based on length difference
                        # Prefer columns where lengths are closer
                        length_diff = len(col_low) - len(alias_norm)
                        score = max(10, 50 - length_diff)
                elif alias_norm_space in col_norm_space:
                    # Similar for normalized
                    pos = col_norm_space.find(alias_norm_space)
                    length_diff = len(col_norm_space) - len(alias_norm_space)
                    score = max(10, 50 - length_diff)
                
                # Keep best scoring match
                if score > best_score:
                    best_score = score
                    best_match = orig
        
        if not best_match or best_score < 10:
            return None
        
        result[idx] = best_match
    
    return result


def is_potential_id(series: pd.Series) -> bool:
    """Heuristic: ID only if name contains id/code/key/uuid AND high unique ratio.
    Fixes small dataset bug where Date/Product with 10/10 unique were misclassified as ID.
    Also excludes datetime-like columns from being ID.
    """
    try:
        unique_ratio = series.nunique() / len(series) if len(series) > 0 else 0
        name = str(series.name).lower()
        has_id_hint = any(k in name for k in ['id', 'code', '_key', 'uuid', 'customer_id', 'order_id', 'product_id'])
        
        # Never treat date-like columns as ID
        if 'date' in name:
            return False
        
        # Never treat product names as ID unless explicit ID hint like product_id
        if name in ['product', 'product name', 'customer name', 'city', 'region', 'state']:
            return False
        
        # Require ID hint AND high unique ratio — fixes small dataset (10 rows) bug
        # For small datasets (n<20), even product names can be 100% unique, but not IDs
        return unique_ratio > 0.90 and has_id_hint
    except:
        return False

def safe_numeric_conversion(series: pd.Series) -> pd.Series:
    """Try to convert to numeric, return original if fails heavily."""
    try:
        converted = pd.to_numeric(series, errors='coerce')
        # If >80% converted, keep
        if converted.notna().sum() / len(series) > 0.8:
            return converted
        return series
    except:
        return series
