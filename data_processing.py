import pandas as pd
import streamlit as st

def melt_clean_data(df, value_name):
    """Melt and clean data for visualization."""
    df_melted = df.melt(
        id_vars=['Country Code'], 
        var_name='Year', 
        value_name=value_name
    )
    df_melted['Year'] = pd.to_datetime(df_melted['Year'], format='%Y')
    return df_melted

@st.cache_data(ttl=24 * 60 * 60)
def fetch_bigquery_data(_client, query):
    job = _client.query(query) 
    df = job.result().to_dataframe() 
    return df

def article_groupby_query(PROJECT_ID, DATASET_ID, TABLE_ID, date_input):
    TABLE_FULL_ID = f'{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}'   
    query = f'''
    SELECT CountryCode, COUNT(*) AS Count, AVG(DocTone) AS Tone
    FROM `{TABLE_FULL_ID}` 
    WHERE DATE(DateTime) = '{date_input.strftime('%Y-%m-%d')}'
    GROUP BY CountryCode
    '''
    return query

def stats_trend_query(PROJECT_ID, DATASET_ID, TABLE_ID, start_year, end_year):
    TABLE_FULL_ID = f'{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}'
    query = f"""
    SELECT 
        CountryCode,
        EXTRACT(YEAR FROM DateTime) AS Year,
        AVG(DocTone) AS Tone
    FROM `{TABLE_FULL_ID}`
    WHERE EXTRACT(YEAR FROM DateTime) BETWEEN {max(2018, start_year)} AND {end_year}
    GROUP BY CountryCode, Year
    ORDER BY Year, CountryCode
    """
    return query

def stats_year_query(PROJECT_ID, DATASET_ID, TABLE_ID, date_input):
    TABLE_FULL_ID = f'{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}'   
    query = f'''
    SELECT CountryCode, AVG(DocTone) AS Tone 
    FROM `{TABLE_FULL_ID}`  
    WHERE EXTRACT(YEAR FROM DateTime) = {date_input.year}  
    GROUP BY CountryCode
    '''
    return query

def stats_month_query(PROJECT_ID, DATASET_ID, TABLE_ID, date_input):
    TABLE_FULL_ID = f'{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}'   
    query = f'''
    SELECT CountryCode, AVG(DocTone) AS Tone 
    FROM `{TABLE_FULL_ID}`  
    WHERE EXTRACT(YEAR FROM DateTime) = {date_input.year}  
    AND EXTRACT(MONTH FROM DateTime) = {date_input.month}
    GROUP BY CountryCode
    '''
    return query

def stats_date_query(PROJECT_ID, DATASET_ID, TABLE_ID, date_input):
    TABLE_FULL_ID = f'{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}'   
    query = f'''
    SELECT CountryCode, AVG(DocTone) AS Tone 
    FROM `{TABLE_FULL_ID}`  
    WHERE DATE(DateTime) = '{date_input.strftime('%Y-%m-%d')}'
    GROUP BY CountryCode
    '''
    return query

def article_country_query(PROJECT_ID, DATASET_ID, TABLE_ID,
                          date_input, selected_countries):
    TABLE_FULL_ID = f'{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}'   
    selected_countries_str = ', '.join(
        [f"'{country}'" for country in selected_countries]) 
    query = f'''
    SELECT CountryCode, ContextualText
    FROM `{TABLE_FULL_ID}` 
    WHERE DATE(DateTime) = '{date_input.strftime('%Y-%m-%d')}'
          AND CountryCode IN ({selected_countries_str}) 
    '''
    return query

def data_query(PROJECT_ID, DATASET_ID, TABLE_ID):
    TABLE_FULL_ID = f'{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}'   
    query = f'''
    SELECT * EXCEPT(`Country Name`,
    `Indicator Name`, `Indicator Code`, `Unnamed: 69`)
    FROM `{TABLE_FULL_ID}` 
    '''
    return query

