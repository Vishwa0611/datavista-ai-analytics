"""
File validators — security first.
"""
import os
from typing import Tuple
from ..utils.constants import SUPPORTED_EXTENSIONS, MAX_FILE_SIZE_MB
from ..utils.logger import logger

def validate_file_extension(filename: str) -> Tuple[bool, str]:
    ext = os.path.splitext(filename)[1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        return False, f"Unsupported format {ext}. Supported: {', '.join(SUPPORTED_EXTENSIONS)}"
    return True, "OK"

def validate_file_size(file_size_bytes: int) -> Tuple[bool, str]:
    size_mb = file_size_bytes / (1024*1024)
    if size_mb > MAX_FILE_SIZE_MB:
        return False, f"File size {size_mb:.1f}MB exceeds limit {MAX_FILE_SIZE_MB}MB. Try sampling or splitting."
    return True, "OK"

def validate_file_content(file_bytes: bytes, filename: str) -> Tuple[bool, str]:
    """Basic magic check — CSV should have commas/newlines, XLSX starts with PK"""
    if len(file_bytes) == 0:
        return False, "Empty file"
    ext = os.path.splitext(filename)[1].lower()
    if ext == '.xlsx' or ext == '.xls':
        # XLSX is ZIP archive starting with PK
        if ext == '.xlsx' and not file_bytes.startswith(b'PK'):
            return False, "Invalid XLSX file — does not start with ZIP header"
    if ext == '.csv':
        # Should contain at least one comma or newline
        try:
            text = file_bytes[:2000].decode('utf-8', errors='ignore')
            if ',' not in text and '\n' not in text:
                return False, "CSV appears invalid — no commas or newlines detected"
        except:
            pass
    return True, "OK"
