import pandas as pd

def classify_columns(df):
    col_types = {}

    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            col_types[col] = "Date"
        elif pd.api.types.is_numeric_dtype(df[col]):
            col_types[col] = "Numeric"
        elif df[col].nunique() < 20:
            col_types[col] = "Categorical"
        else:
            col_types[col] = "Text"

    return col_types