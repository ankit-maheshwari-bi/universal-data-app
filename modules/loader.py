import pandas as pd
import json

def load_data(file):
    filename = file.name.lower()

    try:
        # ---------------- CSV ---------------- #
        if filename.endswith('.csv'):
            try:
                df = pd.read_csv(file)
            except:
                file.seek(0)
                df = pd.read_csv(file, sep=None, engine='python', on_bad_lines='skip')

        # ---------------- JSON ---------------- #
        elif filename.endswith('.json'):
            file.seek(0)
            try:
                df = pd.read_json(file)
            except:
                file.seek(0)
                data = json.load(file)

                # Handle nested JSON
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
            except:
                lines = content.splitlines()

                # Try splitting structured logs
                split_data = [line.split() for line in lines if line.strip()]

                if len(split_data) > 0 and len(split_data[0]) > 3:
                    df = pd.DataFrame(split_data)
                else:
                    df = pd.DataFrame(lines, columns=["Raw_Text"])

        # ---------------- EXCEL ---------------- #
        elif filename.endswith('.xlsx') or filename.endswith('.xls'):
            df = pd.read_excel(file)

        # ---------------- UNSUPPORTED ---------------- #
        else:
            return None, "Unsupported file format"

        # ---------------- FINAL CLEANUP ---------------- #
        if df is None or df.empty:
            return None, "No data found in file"

        df = df.copy()
        df.dropna(how='all', inplace=True)
        df.reset_index(drop=True, inplace=True)

        return df, None

    except Exception as e:
        return None, f"Data loading failed: {str(e)}"
