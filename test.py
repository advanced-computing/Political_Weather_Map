import pytest
import pandas as pd
from tempo import melt_clean_data, load_data, prepare_articles


def test_load_data():
    pass

def test_prepare_articles():
    pass

def test_melt_clean_data():
    input_data = {
        'Country Code': ['ABC', "DEF"],
        '2000': [2, 8],
        '2001': [3,9]
    }
    df_input = pd.DataFrame(input_data)

    output_data = {
        "Country Code": ['ABC', 'DEF', "ABC", "DEF"],
        "Year": ["2000", "2000", "2001", "2001"],
        "Population": [2,8,3,9]
    }
    df_output = pd.DataFrame(output_data)
    df_output["Year"] = pd.to_datetime(df_output["Year"], format = "%Y")

    assert melt_clean_data(df_input, 'Population').equals(df_output)

