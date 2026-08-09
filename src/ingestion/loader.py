"""
Unified file loader — handles CSV, XLSX, JSON, Parquet with encoding fallback.
"""
import io
import os
from typing import List, Optional, Tuple, Any
import pandas as pd
from ..utils.helpers import compute_file_hash, human_readable_size
from ..validation.schema import IngestionResult
from .validators import validate_file_extension, validate_file_size, validate_file_content
from ..utils.logger import logger

def list_excel_sheets(file_bytes: bytes) -> List[str]:
    """Return sheet names for XLSX/XLS"""
    try:
        xls = pd.ExcelFile(io.BytesIO(file_bytes))
        return xls.sheet_names
    except Exception as e:
        logger.warning(f"Could not list sheets: {e}")
        return []

def read_file(
    file_bytes: bytes,
    filename: str,
    sheet_name: Optional[str] = None,
    nrows_preview: int = 100
) -> IngestionResult:
    """
    Main entry — reads bytes into DataFrame.
    Returns IngestionResult with df, preview, metadata
    """
    # Validate
    ok, msg = validate_file_extension(filename)
    if not ok:
        raise ValueError(msg)
    ok, msg = validate_file_size(len(file_bytes))
    if not ok:
        raise ValueError(msg)
    ok, msg = validate_file_content(file_bytes, filename)
    if not ok:
        raise ValueError(msg)

    ext = os.path.splitext(filename)[1].lower()
    df = None
    encoding_used = "utf-8"

    try:
        if ext == '.csv':
            # Try encodings
            for enc in ['utf-8', 'latin1', 'ISO-8859-1', 'cp1252']:
                try:
                    df = pd.read_csv(io.BytesIO(file_bytes), encoding=enc)
                    encoding_used = enc
                    break
                except UnicodeDecodeError:
                    continue
                except Exception as e:
                    # Try with error handling
                    if enc == 'utf-8':
                        continue
                    raise e
            if df is None:
                # Last resort: read with errors='replace'
                df = pd.read_csv(io.BytesIO(file_bytes), encoding='utf-8', encoding_errors='replace')

        elif ext in ['.xlsx', '.xls']:
            if sheet_name:
                df = pd.read_excel(io.BytesIO(file_bytes), sheet_name=sheet_name)
            else:
                # If multiple sheets, default to first but we allow caller to list
                df = pd.read_excel(io.BytesIO(file_bytes), sheet_name=0)

        elif ext == '.json':
            # Try to detect if JSON lines or array
            try:
                df = pd.read_json(io.BytesIO(file_bytes))
            except:
                # Try json normalize if nested
                import json
                data = json.loads(file_bytes.decode('utf-8', errors='ignore'))
                if isinstance(data, list):
                    df = pd.json_normalize(data)
                elif isinstance(data, dict):
                    # If dict of lists
                    df = pd.json_normalize(data)
                else:
                    raise ValueError("Unsupported JSON structure")

        elif ext == '.parquet':
            try:
                df = pd.read_parquet(io.BytesIO(file_bytes))
            except Exception as e:
                raise ValueError(f"Parquet reading failed (need pyarrow): {e}")

        else:
            raise ValueError(f"Unsupported extension {ext}")

    except Exception as e:
        logger.error(f"File read error: {e}")
        raise ValueError(f"Failed to read file: {str(e)}")

    if df is None or df.empty:
        raise ValueError("File read resulted in empty dataset — check file content")

    # Clean up column names slightly for display but keep original
    # We keep original names, just strip whitespace
    df.columns = [str(c).strip() for c in df.columns]

    # Metadata
    mem_usage = df.memory_usage(deep=True).sum()
    metadata = {
        "file_name": filename,
        "file_type": ext.replace('.', '').upper(),
        "file_size_bytes": len(file_bytes),
        "file_size_human": human_readable_size(len(file_bytes)),
        "rows": len(df),
        "columns": len(df.columns),
        "memory_usage_bytes": int(mem_usage),
        "memory_usage_human": human_readable_size(int(mem_usage)),
        "encoding": encoding_used,
        "sheet_name": sheet_name,
        "file_hash": compute_file_hash(file_bytes),
        "excel_sheets": list_excel_sheets(file_bytes) if ext in ['.xlsx', '.xls'] else []
    }

    preview = df.head(nrows_preview)

    return IngestionResult(df=df, preview=preview, metadata=metadata)

def load_sample_dataset(name: str, sample_dir: str = "sample_data") -> IngestionResult:
    """Load built-in sample datasets for demo mode."""
    import pathlib
    base = pathlib.Path(__file__).parent.parent.parent / sample_dir
    # Try csv
    path = base / f"{name}.csv"
    if not path.exists():
        # Try without .csv
        path = base / name
        if not path.exists():
            raise FileNotFoundError(f"Sample dataset {name} not found in {base}")

    with open(path, 'rb') as f:
        file_bytes = f.read()
    return read_file(file_bytes, f"{name}.csv")
