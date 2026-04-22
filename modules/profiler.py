import pandas as pd

def get_profile(df):
    profile_data = []

    for col in df.columns:
        try:
            unique_vals = df[col].nunique()
        except:
            unique_vals = "Unsupported (complex data)"

        profile_data.append({
            "Column": col,
            "Data Type": str(df[col].dtype),
            "Missing Values": df[col].isnull().sum(),
            "Unique Values": unique_vals
        })

    return pd.DataFrame(profile_data)


def detect_issues(df):
    issues = []

    if df.isnull().sum().sum() > 0:
        issues.append("Missing values detected")

    if df.duplicated().sum() > 0:
        issues.append("Duplicate rows found")

    if (df == "").sum().sum() > 0:
        issues.append("Blank values detected")

    return issues
