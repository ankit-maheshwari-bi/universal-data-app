import pandas as pd
import json

# ---------------- NEW ADVANCED FUNCTIONS ---------------- #

def standardize_column_names(df):
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace(r"[^\w]", "", regex=True)
    )
    return df


def clean_text_columns(df):
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype(str).str.strip()
    return df


def auto_parse_dates(df):
    for col in df.columns:
        try:
            df[col] = pd.to_datetime(df[col])
        except:
            continue
    return df


def drop_useless_columns(df):
    df = df.dropna(axis=1, how='all')
    df = df.loc[:, df.nunique() > 1]
    return df


def optimize_dtypes(df):
    for col in df.select_dtypes(include=['int64']).columns:
        df[col] = pd.to_numeric(df[col], downcast='integer')

    for col in df.select_dtypes(include=['float64']).columns:
        df[col] = pd.to_numeric(df[col], downcast='float')

    return df


# ---------------- MAIN LOADER ---------------- #

def load_data(file):
    filename = file.name.lower()

    try:
        # ---------------- CSV ---------------- #
        if filename.endswith('.csv'):
            try:
                df = pd.read_csv(file)
            except Exception:
                file.seek(0)
                df = pd.read_csv(file, sep=None, engine='python', on_bad_lines='skip')

        # ---------------- JSON ---------------- #
        elif filename.endswith('.json'):
            file.seek(0)
            try:
                df = pd.read_json(file)
            except Exception:
                file.seek(0)
                data = json.load(file)

                if isinstance(data, dict):
                    df = pd.json_normalize(data)
                elif isinstance(data, list):
                    df = pd.json_normalize(data)
                else:
                    return None, "Unsupported JSON structure"

        # ---------------- PARQUET ---------------- #
        elif filename.endswith('.parquet'):
            df = pd.read_parquet(file)

        # ---------------- TXT ---------------- #
        elif filename.endswith('.txt'):
            file.seek(0)
            content = file.read().decode('utf-8', errors='ignore')

            try:
                file.seek(0)
                df = pd.read_csv(file, sep=None, engine='python', on_bad_lines='skip')
            except Exception:
                lines = content.splitlines()
                split_data = [line.split() for line in lines if line.strip()]

                if len(split_data) > 0 and len(split_data[0]) > 3:
                    df = pd.DataFrame(split_data)
                else:
                    df = pd.DataFrame(lines, columns=["raw_text"])

        # ---------------- EXCEL ---------------- #
        elif filename.endswith('.xlsx'):
            file.seek(0)
            df = pd.read_excel(file, engine="openpyxl")

        elif filename.endswith('.xls'):
            file.seek(0)
            try:
                df = pd.read_excel(file, engine="xlrd")
            except Exception:
                return None, "Install xlrd to read .xls files"

        # ---------------- FALLBACK ---------------- #
        else:
            file.seek(0)
            try:
                df = pd.read_csv(file, sep=None, engine='python', on_bad_lines='skip')
            except Exception:
                return None, "Unsupported file format or unable to parse"

        # ---------------- FINAL VALIDATION ---------------- #
        if df is None or df.empty:
            return None, "No data found in file"

        df = df.copy()

        # ---------------- APPLY ADVANCED PROCESSING ---------------- #
        df = standardize_column_names(df)
        df = clean_text_columns(df)
        df = auto_parse_dates(df)
        df = drop_useless_columns(df)
        df = optimize_dtypes(df)

        # Final cleanup
        df.dropna(how='all', inplace=True)
        df.reset_index(drop=True, inplace=True)

        return df, None

    except Exception as e:
        return None, f"Data loading failed: {str(e)}"
