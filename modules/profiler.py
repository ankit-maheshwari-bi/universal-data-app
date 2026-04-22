import pandas as pd

def get_profile(df):
    profile = pd.DataFrame({
        "Column": df.columns,
        "Data Type": df.dtypes.values,
        "Null Count": df.isnull().sum().values,
        "Null %": (df.isnull().sum().values / len(df)) * 100,
        "Unique Values": df.nunique().values
    })

    return profile


def detect_issues(df):
    issues = []

    if df.isnull().sum().sum() > 0:
        issues.append("Missing values detected")

    if df.duplicated().sum() > 0:
        issues.append("Duplicate rows found")

    if (df == "").sum().sum() > 0:
        issues.append("Blank values detected")

    return issues