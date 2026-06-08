"""
CCIRC Post-Processing - Perimeters List Column (Simple Version v2)
===================================================================

Approach:
    1. Tạo 4 scope columns (scope_us, scope_fortis, scope_bcef, scope_japan)
    2. Tạo perimeters_list từ 4 columns đó
    3. Xóa 4 scope columns

Output: Chỉ còn perimeters_list
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple


# ==============================================================================
# Constants
# ==============================================================================

PERIMETERS_LIST_COLUMN = "perimeters_list"

NUMERIC_SCOPE_COLUMNS = ["accounting_site_code_post_acc"]

CCIRC_SCOPE_LABELS = [
    ("us", "US"),
    ("fortis", "Fortis"),
    ("bcef", "BCEF"),
    ("japan", "Japan"),
]

ICAAP_SCOPE_LABELS = [
    ("bnl", "BNL"),
    ("fortis", "Fortis"),
    ("pf", "PF"),
    ("bgl", "BGL"),
    ("pfspain", "PF Spain"),
    ("pfitaly", "PF Italy"),
    ("bcef", "BCEF"),
    ("japan", "Japan"),
]


# ==============================================================================
# Step 1: Tạo scope columns
# ==============================================================================

def _compute_scope_column(
    df: pd.DataFrame,
    scope_id: str,
    filters: Dict[str, Any]
) -> pd.DataFrame:
    """
    Tạo 1 scope column (boolean).
    """
    if not filters:
        df[f"scope_{scope_id}"] = True
        return df
    
    mask = pd.Series([True] * len(df), index=df.index)
    
    for col_name, config in filters.items():
        if col_name.startswith("_") or col_name not in df.columns:
            continue
        
        operator = config.get("operator", "IN").upper()
        values = config.get("values", [])
        value = config.get("value")
        allow_null = config.get("allow_null", False)
        
        if not values and value is not None:
            values = [value]
        
        # Normalize column
        if col_name in NUMERIC_SCOPE_COLUMNS:
            col_series = df[col_name].apply(
                lambda x: str(int(float(x))) if pd.notna(x) and x != "" else None
            )
            values = [str(int(float(v))) for v in values]
        else:
            col_series = df[col_name].astype(str).replace({"nan": None, "": None})
            values = [str(v) for v in values]
        
        # Build condition
        if operator == "IN":
            cond = col_series.isin(values)
        elif operator == "EQUALS":
            cond = col_series == values[0]
        elif operator == "NOT_IN":
            cond = ~col_series.isin(values)
            if allow_null:
                cond = cond | col_series.isna()
        elif operator == "NOT_EQUALS":
            cond = col_series != values[0]
            if allow_null:
                cond = cond | col_series.isna()
        else:
            continue
        
        mask = mask & cond
    
    df[f"scope_{scope_id}"] = mask
    return df


# ==============================================================================
# Step 2: Tạo perimeters_list từ scope columns
# ==============================================================================

def _create_perimeters_from_scope_columns(
    df: pd.DataFrame,
    scope_labels: List[Tuple[str, str]]
) -> pd.DataFrame:
    """
    Tạo perimeters_list từ các scope_* columns.
    """
    def build_perimeters(row):
        labels = []
        for scope_id, label in scope_labels:
            col_name = f"scope_{scope_id}"
            if col_name in row.index and row[col_name] == True:
                labels.append(label)
        
        if labels:
            return ",".join(labels)
        else:
            return np.nan
    
    df[PERIMETERS_LIST_COLUMN] = df.apply(build_perimeters, axis=1)
    return df


# ==============================================================================
# Step 3: Xóa scope columns
# ==============================================================================

def _drop_scope_columns(
    df: pd.DataFrame,
    scope_labels: List[Tuple[str, str]]
) -> pd.DataFrame:
    """
    Xóa các scope_* columns.
    """
    cols_to_drop = [f"scope_{scope_id}" for scope_id, _ in scope_labels]
    cols_to_drop = [c for c in cols_to_drop if c in df.columns]
    
    df = df.drop(columns=cols_to_drop)
    return df


# ==============================================================================
# Main Function
# ==============================================================================

def add_perimeters_list(
    df: pd.DataFrame,
    scope_definitions: Dict[str, Any] = None,
    flow_type: str = "ccirc"
) -> pd.DataFrame:
    """
    Tạo column perimeters_list.
    
    Args:
        df: DataFrame với source columns
        scope_definitions: Dict từ params["scopes"]
        flow_type: "ccirc", "icaap", "ifrs9"
    
    Returns:
        DataFrame với column perimeters_list (không có scope_* columns)
    
    Output values:
        - "US", "Fortis", "BCEF", "Japan" (single scope)
        - "US,Fortis" (multiple scopes)
        - NULL (np.nan) nếu không thuộc scope nào
    """
    flow_type_lower = flow_type.lower() if flow_type else ""
    
    # Không có scope definitions → NULL (bao gồm IFRS9)
    if not scope_definitions:
        df[PERIMETERS_LIST_COLUMN] = np.nan
        return df
    
    # Lấy scope labels
    if flow_type_lower == "icaap":
        scope_labels = ICAAP_SCOPE_LABELS
    else:
        scope_labels = CCIRC_SCOPE_LABELS
    
    # Step 1: Tạo scope columns
    for scope_id, label in scope_labels:
        if scope_id in scope_definitions:
            filters = scope_definitions[scope_id].get("filters", {})
            df = _compute_scope_column(df, scope_id, filters)
    
    # Step 2: Tạo perimeters_list
    df = _create_perimeters_from_scope_columns(df, scope_labels)
    
    # Step 3: Xóa scope columns
    df = _drop_scope_columns(df, scope_labels)
    
    return df


# ==============================================================================
# Usage
# ==============================================================================

"""
df_out = add_perimeters_list(df_out, scope_definitions, flow_type="ccirc")

# Output: chỉ có perimeters_list, không có scope_us, scope_fortis...
"""
