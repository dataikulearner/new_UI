def _compute_scope_column(df: DataFrame, scope_id: str, filters: dict) -> DataFrame:
    """
    Compute single scope boolean column.
    """
    if not filters:
        return df.withColumn(f"scope_{scope_id}", F.lit(True))
    
    condition = F.lit(True)
    
    for col_name, config in filters.items():
        if col_name.startswith("_"):
            continue
        if col_name not in df.columns:
            logger.warning(f"  Column '{col_name}' not found for scope '{scope_id}', skipping")
            continue
        
        operator = config.get("operator", "IN").upper()
        values = config.get("values", [])
        value = config.get("value")
        allow_null = config.get("allow_null", False)
        
        if not values and value is not None:
            values = [value]
        
        # =====================================================================
        # FIX: Convert string values to double for numeric columns
        # =====================================================================
        if col_name in NUMERIC_SCOPE_COLUMNS:
            # Convert ["12309", "40043"] → [12309.0, 40043.0]
            values = [float(v) for v in values]
        
        if operator == "IN":
            cond = F.col(col_name).isin(values)
        elif operator == "EQUALS":
            cond = F.col(col_name) == values[0]
        elif operator == "NOT_IN":
            cond = ~F.col(col_name).isin(values)
            if allow_null:
                cond = cond | F.col(col_name).isNull()
            else:
                cond = cond & F.col(col_name).isNotNull()
        elif operator == "NOT_EQUALS":
            cond = F.col(col_name) != values[0]
            if allow_null:
                cond = cond | F.col(col_name).isNull()
            else:
                cond = cond & F.col(col_name).isNotNull()
        else:
            continue
        
        condition = condition & cond
    
    return df.withColumn(f"scope_{scope_id}", condition)
