"""
DuckDB engine — in-process analytical DB.
Fixed: Converts datetime columns to DATE type so DATE_TRUNC works (fixes VARCHAR binder error)
"""
import duckdb
import pandas as pd
from typing import Dict, Any, Optional
from ..utils.logger import logger

def _convert_datetime_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Try to convert object columns that look like dates to datetime64"""
    df_copy = df.copy()
    for col in df_copy.columns:
        # Skip if already datetime
        if pd.api.types.is_datetime64_any_dtype(df_copy[col]):
            continue
        # Only try for object columns
        if df_copy[col].dtype == 'object':
            try:
                # Sample first 20 non-null
                sample = df_copy[col].dropna().head(20)
                if len(sample) == 0:
                    continue
                # Try parsing with dayfirst=True (handles DD-MM-YYYY)
                parsed_sample = pd.to_datetime(sample, errors='coerce', dayfirst=True)
                success_ratio = parsed_sample.notna().sum() / len(sample)
                if success_ratio > 0.8:
                    # Convert full column
                    df_copy[col] = pd.to_datetime(df_copy[col], errors='coerce', dayfirst=True)
                    logger.info(f"Converted column {col} to datetime for DuckDB")
            except:
                continue
    return df_copy

class DuckDBEngine:
    def __init__(self):
        self.con = duckdb.connect(database=':memory:')
        self.tables = {}

    def register_table(self, table_name: str, df: pd.DataFrame):
        """Register dataframe as DuckDB table — with datetime conversion"""
        try:
            # Convert datetime-like columns first
            df_converted = _convert_datetime_columns(df)
            
            # Clean table name
            safe_name = ''.join(c if c.isalnum() or c=='_' else '_' for c in table_name).lower()
            # Register
            self.con.register('df_temp', df_converted)
            self.con.execute(f"CREATE OR REPLACE TABLE {safe_name} AS SELECT * FROM df_temp")
            self.con.unregister('df_temp')
            
            self.tables[safe_name] = {"rows": len(df_converted), "cols": len(df_converted.columns)}
            logger.info(f"Registered table {safe_name} with {len(df_converted)} rows, cols: {list(df_converted.columns)[:5]}...")
            return safe_name
        except Exception as e:
            logger.warning(f"First registration method failed for {table_name}: {e}, trying fallback")
            try:
                # Fallback without datetime conversion
                self.con.register(table_name, df)
                self.con.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM {table_name}")
                self.tables[table_name] = {"rows": len(df), "cols": len(df.columns)}
                return table_name
            except Exception as e2:
                logger.error(f"Failed to register {table_name}: {e2}")
                raise e2

    def execute(self, sql: str, limit: int = 10000) -> Dict[str, Any]:
        """Safe execute with timeout logic."""
        try:
            result_df = self.con.execute(sql).fetchdf()
            if len(result_df) > limit:
                result_df = result_df.head(limit)
            return {"success": True, "df": result_df, "rows": len(result_df)}
        except Exception as e:
            logger.warning(f"SQL execution failed: {sql[:200]}... Error: {e}")
            return {"success": False, "error": str(e), "df": None}

    def get_schema(self, table_name: str):
        try:
            schema = self.con.execute(f"DESCRIBE {table_name}").fetchdf()
            return schema
        except Exception as e:
            return None

    def list_tables(self):
        try:
            tables = self.con.execute("SHOW TABLES").fetchdf()
            return tables
        except:
            return pd.DataFrame()

    def close(self):
        try:
            self.con.close()
        except:
            pass

def get_engine():
    return DuckDBEngine()
