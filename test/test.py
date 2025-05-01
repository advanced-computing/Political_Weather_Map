import pytest
import pandas as pd
import plotly.graph_objs as go
from main_page import melt_clean_data, load_data, select_columns
from main_page import code_mapping, convert_to_alpha3, plot_choropleth

# test_lad_data
def test_load_data():
    test_file = 'test_data.csv'
    test_data = (
        'name,age,city\n'
        'Alice,30,New York\n'
        'Bob,25,San Francisco\n'
        'Charlie,35,Los Angeles'
    )

        # Write the test CSV file
    with open(test_file, 'w') as f:
        f.write(test_data)

    test_output = pd.DataFrame({
        'name': ['Alice', 'Bob', 'Charlie'],
        'age': [30, 25, 35],
        'city': ['New York', 'San Francisco', 'Los Angeles']
    })
    assert load_data(test_file).equals(test_output)

# test_select_columns
def test_select_columns():
    df_input = pd.DataFrame({
        'DateTime': ['2023-02-04', '2023-02-05'],
        'CountryCode': ['USA', 'JPN'],
        'Title': ['Dan', 'Amy'],
        'ContextualText': ['Dan got promoted', 'Amy got fired'],
        'DocTone': [4.3, -3.3],
        'URL': ['www.articles', 'www.posts'],
        'Source': ['WSJ', 'NYT']
    })
    df_output = pd.DataFrame({
        'DateTime': pd.to_datetime(['2023-02-04', '2023-02-05']),
        'CountryCode': ['USA', 'JPN'],
        'Title': ['Dan', 'Amy'],
        'ContextualText': ['Dan got promoted', 'Amy got fired'],
        'DocTone': [4.3, -3.3],
        'URL': ['www.articles', 'www.posts']
    })

    assert df_output.equals(select_columns(df_input))

# test_melt_clean_data
def test_melt_clean_data():
    input_data = {
        'Country Code': ['ABC', 'DEF'],
        '2000': [2, 8],
        '2001': [3,9]
    }
    df_input = pd.DataFrame(input_data)

    output_data = {
        'Country Code': ['ABC', 'DEF', 'ABC', 'DEF'],
        'Year': ['2000', '2000', '2001', '2001'],
        'Population': [2,8,3,9]
    }
    df_output = pd.DataFrame(output_data)
    df_output['Year'] = pd.to_datetime(df_output['Year'], format = '%Y')

    assert melt_clean_data(df_input, 'Population').equals(df_output)

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
            print(f'Test failed for alpha2: {alpha2} and alpha3:'
                  '{alpha3} (got: {convert_to_alpha3(alpha2)})')

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
        print('Test passed: The function returned a Plotly Figure object.')
    except AssertionError:
        print('Test failed')

