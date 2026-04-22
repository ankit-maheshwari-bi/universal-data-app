import pandas as pd

# ---------------- SAFE UNIQUE ---------------- #
def safe_nunique(series):
    try:
        return series.nunique()
    except:
        try:
            return series.astype(str).nunique()
        except:
            return "Unsupported"

# ---------------- PROFILE ---------------- #
def get_profile(df):
    profile_data = []

    for col in df.columns:
        series = df[col]

        profile_data.append({
            "Column": col,
            "Data Type": str(series.dtype),
            "Missing Values": int(series.isnull().sum()),
            "Missing %": round(series.isnull().mean() * 100, 2),
            "Unique Values": safe_nunique(series),
            "Sample Value": str(series.dropna().iloc[0]) if series.dropna().shape[0] > 0 else "N/A"
        })

    return pd.DataFrame(profile_data)


# ---------------- ISSUE DETECTION ---------------- #
def detect_issues(df):
    issues = []

    # Missing values
    if df.isnull().sum().sum() > 0:
        issues.append("⚠️ Missing values detected")

    # Duplicate rows
    if df.duplicated().sum() > 0:
        issues.append("⚠️ Duplicate rows found")

    # Blank values (only for object columns)
    obj_cols = df.select_dtypes(include=['object']).columns
    if len(obj_cols) > 0:
        blank_count = (df[obj_cols].apply(lambda x: x.astype(str).str.strip() == "")).sum().sum()
        if blank_count > 0:
            issues.append("⚠️ Blank/empty string values detected")

    # High cardinality columns
    for col in df.columns:
        try:
            if df[col].nunique() > 0.9 * len(df):
                issues.append(f"⚠️ High cardinality column: {col}")
        except:
            continue

    # Single value columns
    for col in df.columns:
        try:
            if df[col].nunique() == 1:
                issues.append(f"⚠️ Column '{col}' has only one unique value")
        except:
            continue

    return issues
