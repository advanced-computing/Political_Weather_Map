import pandas as pd
import os

# Irrelevant now : with Big Queery
def load_data(file_name):
    """Load CSV data from a file."""
    path = os.path.join(os.path.dirname(__file__), file_name)
    return pd.read_csv(path)

def select_columns(df_article):
    """Select relevant columns and convert DateTime to datetime type."""
    columns = ['DateTime', 'CountryCode', 'Title', 'ContextualText', 'DocTone']
    df_article['DateTime'] = pd.to_datetime(df_article['DateTime'])
    return df_article[columns]

def melt_clean_data(df, value_name):
    """Melt and clean data for visualization."""
    df_melted = df.melt(
        id_vars=['Country Code'], 
        var_name='Year', 
        value_name=value_name
    )
    df_melted['Year'] = pd.to_datetime(df_melted['Year'], format='%Y')
    return df_melted
