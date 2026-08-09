"""
PII detection utilities — regex based, conservative.
Only checks object/text columns to avoid flagging numeric metrics.
"""
import re
from typing import Dict, List

# Stricter patterns with anchors/word boundaries
PII_PATTERNS_STRICT = {
    "email": r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$",
    "phone_in_strict": r"^(\+91[\-\s]?)?[6-9]\d{9}$",  # Indian 10-digit starting 6-9, optional +91
    "phone_us_strict": r"^(\+1[\-\s]?)?\(?\d{3}\)?[\-\s]?\d{3}[\-\s]?\d{4}$",
}

# For floating numbers, we should NOT flag as phone
# So we check if value after stripping non-digits is 10 digits and matches phone pattern

def detect_pii_columns(df_columns: List[str], sample_values: Dict[str, List[str]], dtypes: Dict[str, str] = None) -> Dict[str, List[str]]:
    """
    Detect potential PII columns based on name and sample values.
    Only checks columns that are object/text — skips numeric.
    Returns dict: column -> list of detected PII types
    """
    pii_results = {}
    dtypes = dtypes or {}

    # Compile strict patterns
    compiled_strict = {
        "email": re.compile(PII_PATTERNS_STRICT["email"], re.IGNORECASE),
        "phone_in": re.compile(PII_PATTERNS_STRICT["phone_in_strict"]),
        "phone_us": re.compile(PII_PATTERNS_STRICT["phone_us_strict"]),
    }

    # Loose email pattern for contains (email can be in text)
    email_loose = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")

    for col in df_columns:
        # Skip numeric dtypes entirely for PII — revenue, spend etc should not be flagged
        dtype_str = str(dtypes.get(col, "")).lower()
        if any(x in dtype_str for x in ['int', 'float', 'numeric']):
            # Also check if col name suggests PII? Even if numeric, skip phone detection
            # But if column name is explicitly email/phone, we still check
            col_lower = col.lower()
            is_explicit_pii_name = any(hint in col_lower for hint in ['email', 'phone', 'mobile', 'contact', 'aadhaar', 'ssn', 'social'])
            if not is_explicit_pii_name:
                continue

        col_lower = col.lower()
        found_types = []

        samples = sample_values.get(col, [])[:20]

        for val in samples:
            s = str(val).strip()
            if not s:
                continue

            # Skip values that look like floats with many decimals (e.g., 4635.854089) — not phone
            if '.' in s:
                # If it's a float representation, skip phone/aadhaar checks
                try:
                    float(s)
                    # If it has more than 1 decimal point or many decimals, likely numeric metric
                    # We still check email though
                    if email_loose.search(s):
                        if 'email' not in found_types:
                            found_types.append('email')
                    continue
                except:
                    pass

            # Clean value for phone check: remove spaces, dashes, parentheses
            cleaned = re.sub(r'[\s\-\(\)]', '', s)

            # Email check (loose for object columns)
            if email_loose.search(s):
                if 'email' not in found_types:
                    found_types.append('email')

            # Phone India: 10 digits starting 6-9, optionally +91
            # Remove +91 prefix for check
            temp = cleaned
            if temp.startswith('+91'):
                temp = temp[3:]
            if temp.startswith('91') and len(temp) >10:
                temp = temp[2:]
            if temp.startswith('0'):
                temp = temp[1:]

            # Now check 10-digit
            if re.fullmatch(r'[6-9]\d{9}', temp):
                if 'phone_in' not in found_types:
                    found_types.append('phone_in')

            # US phone: 10 digits
            if re.fullmatch(r'\d{10}', temp) or re.fullmatch(r'\d{3}\d{3}\d{4}', temp):
                # Only flag as US phone if col name hints phone
                if any(h in col_lower for h in ['phone', 'mobile', 'contact']) and 'phone_us' not in found_types:
                    found_types.append('phone_us')

        if found_types:
            pii_results[col] = found_types

    return pii_results

def mask_pii_value(value: str) -> str:
    """Mask for display — not security, just UI safety."""
    s = str(value)
    if "@" in s and "." in s:
        parts = s.split("@")
        if len(parts) == 2:
            return parts[0][:2] + "***@" + parts[1]
    if len(s) > 4:
        return s[:2] + "***" + s[-2:]
    return "***"
