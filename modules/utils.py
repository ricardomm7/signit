import pandas as pd

def read_csv_data(csv_path):
    """
    Lê o arquivo CSV e retorna um DataFrame.
    O CSV deve conter uma coluna chamada 'text' com os textos a inserir.
    """
    df = pd.read_csv(csv_path)
    if 'text' not in df.columns:
        raise ValueError("CSV file must contain a 'text' column.")
    return df
