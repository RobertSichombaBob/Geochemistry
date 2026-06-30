import numpy as np
import pandas as pd

def multiplicative_replace(series: pd.Series) -> pd.Series:
    """
    Replace zeros with 2/3 of the smallest positive value.
    For compositional data (CoDA) – handles values below detection limit.
    """
    vals = pd.to_numeric(series, errors="coerce").fillna(0).astype(float)
    positive = vals[vals > 0]
    if len(positive) == 0:
        return vals
    delta = positive.min() * (2/3)
    vals[vals == 0] = delta
    return vals

def safe_divide(a, b, default=0.0):
    with np.errstate(divide='ignore', invalid='ignore'):
        res = np.divide(a, b)
        res[~np.isfinite(res)] = default
    return res

def detect_coordinate_columns(df: pd.DataFrame) -> tuple:
    """
    Auto‑detect spatial coordinate columns (East/North or Lon/Lat).
    Returns (x_col, y_col) or (None, None).
    """
    x_patterns = ['east', 'easting', 'x', 'longitude', 'lon', 'coord_x', 'x_coord']
    y_patterns = ['north', 'northing', 'y', 'latitude', 'lat', 'coord_y', 'y_coord']
    x_col, y_col = None, None
    for col in df.columns:
        col_lower = col.lower().strip()
        if any(p in col_lower for p in x_patterns):
            x_col = col
        if any(p in col_lower for p in y_patterns):
            y_col = col
        if x_col and y_col:
            break
    return x_col, y_col

def detect_element_columns(df: pd.DataFrame, coord_cols: list) -> list:
    """
    Identify numeric columns that are likely element concentrations.
    Uses common element symbols and heuristics.
    """
    common_elements = [
        'au', 'ag', 'cu', 'pb', 'zn', 'fe', 'as', 'hg', 'cd', 'cr', 'ni', 'co',
        'mn', 'mo', 'sb', 'se', 'th', 'u', 'v', 'al', 'ca', 'k', 'mg', 'na',
        'ti', 'p', 's', 'si', 'ba', 'be', 'bi', 'w', 'zr', 'rb', 'sn', 'sr',
        'li', 'cs', 'ga', 'ge', 'te', 'tl', 're', 'pt', 'pd', 'rh', 'ru'
    ]
    elements = []
    for col in df.columns:
        if col in coord_cols:
            continue
        if not pd.api.types.is_numeric_dtype(df[col]):
            continue
        col_lower = col.lower()
        # Check if column name contains a known element symbol (as whole word or prefix)
        # Also check if it ends with (ppm) or (%)
        is_element = False
        for elem in common_elements:
            if elem in col_lower or col_lower.endswith(f"({elem})") or f"{elem}_" in col_lower:
                is_element = True
                break
        if is_element:
            elements.append(col)
        else:
            # Heuristic: if column has range and median in typical geochemical range
            non_null = df[col].dropna()
            if len(non_null) > 0:
                median = non_null.median()
                if 0.001 < median < 1_000_000 and non_null.std() > 0:
                    elements.append(col)
    return elements