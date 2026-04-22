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
               data = json.load(file)
               df = pd.json_normalize(data)

        # ---------------- PARQUET ---------------- #
        elif filename.endswith('.parquet'):
            df = pd.read_parquet(file)

        # ---------------- TXT (SMART HANDLING) ---------------- #
        elif filename.endswith('.txt'):
            file.seek(0)
            content = file.read().decode('utf-8')

            # Try structured read first
            try:
                file.seek(0)
                df = pd.read_csv(file, sep=None, engine='python', on_bad_lines='skip')
            except:
                # Detect log-like file
                lines = content.splitlines()

                # Try splitting by common patterns
                split_data = [line.split() for line in lines]

                if len(split_data) > 0 and len(split_data[0]) > 3:
                    df = pd.DataFrame(split_data)
                else:
                    df = pd.DataFrame(lines, columns=["Raw_Text"])

        # ---------------- EXCEL ---------------- #
        elif filename.endswith('.xlsx'):
            df = pd.read_excel(file)

        else:
            return None, "Unsupported file format"

        # ---------------- FINAL CLEANUP ---------------- #
        df = df.copy()

        # Remove fully empty rows
        df.dropna(how='all', inplace=True)

        # Reset index
        df.reset_index(drop=True, inplace=True)

        return df, None

    except Exception as e:
        return None, f"Data loading failed: {str(e)}"
