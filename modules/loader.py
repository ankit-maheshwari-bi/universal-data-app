import pandas as pd

def load_data(file):
    filename = file.name.lower()

    try:
        if filename.endswith('.csv'):
            df = pd.read_csv(file)

        elif filename.endswith('.json'):
            df = pd.read_json(file)

        elif filename.endswith('.parquet'):
            df = pd.read_parquet(file)

        elif filename.endswith('.txt'):
            df = pd.read_csv(file)

        elif filename.endswith('.xlsx'):
            df = pd.read_excel(file)

        else:
            return None, "Unsupported file format"

        return df, None

    except Exception as e:
        return None, str(e)