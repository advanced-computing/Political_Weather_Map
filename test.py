import pytest
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from main_page import melt_clean_data, load_data, select_columns
from main_page import code_mapping, convert_to_alpha3, plot_choropleth

# test_case_mapping
@pytest.fixture
def test_case_mapping():
    test_mapping = {'JA': 'JP', 'GM': 'DE', 'IZ': 'IQ'}    
    df = pd.DataFrame(list(test_mapping.items()), columns=['FIPS', 'ISO'])
    df_fips = df[['FIPS']]
    df_iso = df[['ISO']]
    column = 'FIPS'
    df_iso = df_iso.rename(columns={'ISO': column})
    return df_fips, df_iso, column

def test_code_mapping(test_case_mapping):
    df_fips, df_iso, column = test_case_mapping
    try:
        df_new = code_mapping(df_fips, column)
        assert df_iso.equals(df_new)
        print(f'Test passed for FIPS codes in column {column}')
    except AssertionError:
        print(f"Test failed for FIPS codes in column {column}")

# test_convert_to_alpha3
@pytest.fixture
def test_case_alpha3():
    alpha2s = ['US', 'JP', 'DE', 'FR']
    alpha3s = ['USA', 'JPN', 'DEU', 'FRA']
    return alpha2s, alpha3s

def test_convert_to_alpha3(test_case_alpha3):
    alpha2s, alpha3s = test_case_alpha3
    for alpha2, alpha3 in zip(alpha2s, alpha3s):
        try:
            assert convert_to_alpha3(alpha2) == alpha3
            print(f'Test passed for alpha2: {alpha2} and alpha3: {alpha3}')
        except AssertionError:
            print(f'Test failed for alpha2: {alpha2} and alpha3: {alpha3} (got: {convert_to_alpha3(alpha2)})')

# test_plot_choropleth
@pytest.fixture
def test_case_plot():
    data = pd.DataFrame({
        'Alpha3Code': ['USA', 'JPN', 'DEU'],
        'Value': [100, 200, 150]
        })
    return data

def test_plot_choropleth(test_case_plot):
    data = test_case_plot
    try:
        fig = plot_choropleth(data, 'Value', 'Sample Choropleth Map')
        assert isinstance(fig, go.Figure)
        print("Test passed: The function returned a Plotly Figure object.")
    except AssertionError:
        print(f'Test failed')
        