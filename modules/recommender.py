def get_recommendations(df):
    recs = []

    # Missing values
    nulls = df.isnull().sum()
    for col, val in nulls.items():
        if val > 0:
            recs.append(f"Column '{col}' has missing values → consider filling or removing")

    # Data types
    for col in df.columns:
        if df[col].dtype == 'object':
            recs.append(f"Column '{col}' may need datatype validation (text/date/number)")

    # Duplicates
    if df.duplicated().sum() > 0:
        recs.append("Duplicate rows detected → consider removing duplicates")

    return recs