import pandas as pd

def generate_insights(df):
    insights = []

    # Identify numeric & categorical columns
    num_cols = df.select_dtypes(include=['number']).columns
    cat_cols = df.select_dtypes(include=['object']).columns

    # Basic business-style signals
    if "Sales" in df.columns:
        total_sales = df["Sales"].sum()
        insights.append(f"Total sales is {round(total_sales,2)}")

    if "Profit" in df.columns:
        total_profit = df["Profit"].sum()
        if total_profit < 0:
            insights.append("Overall business is running in loss")
        else:
            insights.append("Business is profitable")

    if "Region" in df.columns and "Sales" in df.columns:
        region_sales = df.groupby("Region")["Sales"].sum()
        lowest_region = region_sales.idxmin()
        highest_region = region_sales.idxmax()

        insights.append(f"Lowest performing region: {lowest_region}")
        insights.append(f"Top performing region: {highest_region}")

    # Generic insight (works for any dataset)
    if len(num_cols) > 0:
        col = num_cols[0]
        insights.append(f"Column '{col}' shows numeric trends, useful for forecasting")

    return insights