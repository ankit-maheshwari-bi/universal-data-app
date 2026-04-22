from modules.insights import generate_insights
from modules.recommender import get_recommendations
from modules.profiler import get_profile, detect_issues
from modules.loader import load_data

import streamlit as st
import pandas as pd

# ---------------- PAGE CONFIG ---------------- #
st.set_page_config(page_title="Universal Data App", layout="wide")

# ---------------- TITLE ---------------- #
st.title("📊 Universal Data Health & Insight Platform")

# ---------------- SIDEBAR ---------------- #
st.sidebar.title("📊 Navigation")

menu = st.sidebar.radio(
    "Go to",
    ["Upload Data", "Overview", "Data Profile", "Issues", "Insights", "Recommendations"]
)

# ---------------- FILE UPLOAD ---------------- #
file = st.file_uploader(
    "📂 Upload your dataset",
    type=["csv", "json", "parquet", "txt", "xlsx"]
)

# ---------------- MAIN LOGIC ---------------- #
if file:
    df, error = load_data(file)

    if error:
        st.error(f"❌ Error loading file: {error}")
    else:
        st.success("✅ File loaded successfully!")

        # ---------------- KPI SECTION ---------------- #
        st.markdown("## 📊 Dataset KPIs")

        total_rows = df.shape[0]
        total_cols = df.shape[1]
        missing_values = df.isnull().sum().sum()
        duplicate_rows = df.duplicated().sum()

        missing_pct = (missing_values / (total_rows * total_cols)) * 100 if total_rows > 0 else 0
        duplicate_pct = (duplicate_rows / total_rows) * 100 if total_rows > 0 else 0

        num_cols = len(df.select_dtypes(include=['number']).columns)
        cat_cols = len(df.select_dtypes(include=['object']).columns)

        # Health Score
        health_score = 100
        if total_rows > 0:
            health_score -= (missing_values / (total_rows * total_cols)) * 50
            health_score -= (duplicate_rows / total_rows) * 50

        health_score = max(0, round(health_score, 2))

        k1, k2, k3, k4, k5, k6 = st.columns(6)

        k1.metric("Rows", total_rows)
        k2.metric("Columns", total_cols)
        k3.metric("Missing %", f"{round(missing_pct,2)}%")
        k4.metric("Duplicate %", f"{round(duplicate_pct,2)}%")
        k5.metric("Numeric Cols", num_cols)
        k6.metric("Categorical Cols", cat_cols)

        if health_score > 80:
            st.success(f"🟢 Data Health Score: {health_score}% (Good)")
        elif health_score > 50:
            st.warning(f"🟡 Data Health Score: {health_score}% (Needs Cleaning)")
        else:
            st.error(f"🔴 Data Health Score: {health_score}% (Poor Quality)")

        # ---------------- OVERVIEW ---------------- #
        if menu == "Overview":
            st.markdown("## 🔍 Data Preview")
            st.dataframe(df.head(), use_container_width=True)

        # ---------------- DATA PROFILE ---------------- #
        elif menu == "Data Profile":
            st.markdown("## 🧠 Data Profile")
            profile_df = get_profile(df)
            st.dataframe(profile_df, use_container_width=True)

        # ---------------- ISSUES ---------------- #
        elif menu == "Issues":
            st.markdown("## ⚠️ Data Issues")
            issues = detect_issues(df)

            if issues:
                for issue in issues:
                    st.warning(issue)
            else:
                st.success("No major issues detected!")

        # ---------------- INSIGHTS ---------------- #
        elif menu == "Insights":
            st.markdown("## 🧠 Data Understanding & Insights")

            num_cols = df.select_dtypes(include=['number']).columns
            cat_cols = df.select_dtypes(include=['object']).columns

            st.info(f"Dataset contains {len(num_cols)} numeric columns and {len(cat_cols)} categorical columns")

            use_cases = []

            if "Sales" in df.columns:
                use_cases.append("Sales Analysis can be performed")

            if "Profit" in df.columns:
                use_cases.append("Profitability analysis can be done")

            if len(num_cols) > 0:
                use_cases.append("Trend and forecasting analysis possible")

            if len(cat_cols) > 0:
                use_cases.append("Segmentation and grouping analysis possible")

            for uc in use_cases:
                st.success(uc)

            st.markdown("### 💡 Decision Insights")

            insights = generate_insights(df)

            if insights:
                for ins in insights:
                    st.info(ins)
            else:
                st.write("No insights generated")

        # ---------------- RECOMMENDATIONS ---------------- #
        elif menu == "Recommendations":
            st.markdown("## 🛠️ Action Plan & Recommendations")

            actions = []

            # Missing values
            nulls = df.isnull().sum()
            for col, val in nulls.items():
                if val > 0:
                    actions.append(f"Fill missing values in '{col}' ({val} records)")

            # Duplicates
            if df.duplicated().sum() > 0:
                actions.append("Remove duplicate rows")

            # Data type suggestions
            for col in df.columns:
                if df[col].dtype == 'object':
                    actions.append(f"Validate data type for '{col}'")

            if actions:
                for act in actions:
                    st.warning(act)
            else:
                st.success("No major actions required")

            st.markdown("### 💡 Transformation Suggestions")

            recs = get_recommendations(df)

            if recs:
                for rec in recs:
                    st.warning(rec)

            # ---------------- DOWNLOAD REPORT ---------------- #
            st.markdown("### 📥 Download Report")

            insights = generate_insights(df)
            max_len = max(len(insights), len(recs))

            insights_extended = insights + [""] * (max_len - len(insights))
            recs_extended = recs + [""] * (max_len - len(recs))

            report_df = pd.DataFrame({
                "Insights": insights_extended,
                "Recommendations": recs_extended
            })

            csv = report_df.to_csv(index=False).encode("utf-8")

            st.download_button(
                label="📄 Download Summary Report",
                data=csv,
                file_name="data_summary_report.csv",
                mime="text/csv"
            )