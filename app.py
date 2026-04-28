from modules.insights import generate_insights
from modules.recommender import get_recommendations
from modules.profiler import get_profile, detect_issues
from modules.loader import load_data

# NEW IMPORTS
from modules.classifier import classify_columns
import plotly.express as px

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

        # ---------------- IMPROVED HEALTH SCORE ---------------- #
        missing_weight = 0.4
        duplicate_weight = 0.3
        consistency_weight = 0.3

        missing_score = 1 - (missing_values / (total_rows * total_cols)) if total_rows > 0 else 1
        duplicate_score = 1 - (duplicate_rows / total_rows) if total_rows > 0 else 1
        consistency_score = num_cols / total_cols if total_cols > 0 else 1

        health_score = (
            missing_score * missing_weight +
            duplicate_score * duplicate_weight +
            consistency_score * consistency_weight
        ) * 100

        health_score = round(health_score, 2)

        # ---------------- KPI DISPLAY ---------------- #
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

            col_types = classify_columns(df)

            numeric_cols = [col for col, t in col_types.items() if t == "Numeric"]
            categorical_cols = [col for col, t in col_types.items() if t == "Categorical"]

            st.info(f"Detected {len(numeric_cols)} numeric and {len(categorical_cols)} categorical columns")

            # ---------------- AUTO VISUALS ---------------- #
            st.markdown("### 📊 Auto Visualizations")

            if numeric_cols:
                fig = px.histogram(df, x=numeric_cols[0])
                st.plotly_chart(fig, use_container_width=True)

            if categorical_cols:
                cat_data = df[categorical_cols[0]].value_counts().reset_index()
                cat_data.columns = ['Category', 'Count']
                fig = px.bar(cat_data, x='Category', y='Count')
                st.plotly_chart(fig, use_container_width=True)

            # ---------------- INSIGHTS ---------------- #
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

            # SMART Missing handling
            nulls = df.isnull().sum()
            for col, val in nulls.items():
                if val > 0:
                    if df[col].dtype in ['int64', 'float64']:
                        actions.append(f"Fill missing values in '{col}' using median")
                    else:
                        actions.append(f"Fill missing values in '{col}' using mode")

            # Duplicates
            if df.duplicated().sum() > 0:
                actions.append("Remove duplicate rows")

            # Data type suggestions
            for col in df.columns:
                if df[col].dtype == 'object':
                    actions.append(f"Validate or convert data type for '{col}'")

            if actions:
                for act in actions:
                    st.warning(act)
            else:
                st.success("No major actions required")

            # ---------------- AUTO CLEAN BUTTON ---------------- #
            st.markdown("### 🧹 Auto Fix Data")

            if st.button("Auto Clean Data"):
                original_shape = df.shape

                # Fill numeric
                df.fillna(df.median(numeric_only=True), inplace=True)

                # Fill categorical
                for col in df.select_dtypes(include=['object']).columns:
                    if not df[col].mode().empty:
                        df[col].fillna(df[col].mode()[0], inplace=True)

                # Drop duplicates
                df.drop_duplicates(inplace=True)

                st.success(f"Data cleaned! Rows reduced from {original_shape[0]} to {df.shape[0]}")

            # ---------------- RECOMMENDATIONS ---------------- #
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
