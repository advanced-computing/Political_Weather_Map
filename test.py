import pytest
import pandas as pd
from tempo import melt_clean_data, load_data, select_columns


def test_load_data():
    test_file = "test_data.csv"
    test_data = "name,age,city\nAlice,30,New York\nBob,25,San Francisco\nCharlie,35,Los Angeles"
        
        # Write the test CSV file
    with open(test_file, "w") as f:
        f.write(test_data)

    test_output = pd.DataFrame({
        "name": ["Alice", "Bob", "Charlie"],
        "age": [30, 25, 35],
        "city": ["New York", "San Francisco", "Los Angeles"]
    })
    assert load_data(test_file).equals(test_output)


def test_select_columns():
    df_input = pd.DataFrame({
        'DateTime': ['2023-02-04', '2023-02-05'],
        'CountryCode': ["USA", "JPN"],
        'Title': ['Dan', 'Amy'],
        'ContextualText': ['Dan got promoted', 'Amy got fired'],
        'DocTone': [4.3, -3.3],
        'URL': ['www.articles', 'www.posts'],
        'Source': ['WSJ', 'NYT']
    })
    df_output = pd.DataFrame({
        'DateTime': pd.to_datetime(['2023-02-04', '2023-02-05']),
        'CountryCode': ["USA", "JPN"],
        'Title': ['Dan', 'Amy'],
        'ContextualText': ['Dan got promoted', 'Amy got fired'],
        'DocTone': [4.3, -3.3],
        'URL': ['www.articles', 'www.posts']
    })

    assert df_output.equals(select_columns(df_input))

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

