import pandas as pd
import streamlit as st

@st.cache_data
def select_columns(df_article):
    """Select relevant columns and convert DateTime to datetime type."""
    columns = ['DateTime', 'CountryCode', 'Title', 'ContextualText', 'DocTone']
    df_article['DateTime'] = pd.to_datetime(df_article['DateTime'])
    return df_article[columns]

@st.cache_data
def melt_clean_data(df, value_name):
    """Melt and clean data for visualization."""
    df_melted = df.melt(
        id_vars=['Country Code'], 
        var_name='Year', 
        value_name=value_name
    )
    df_melted['Year'] = pd.to_datetime(df_melted['Year'], format='%Y')
    return df_melted

@st.cache_resource
def article_groupby_query(PROJECT_ID, DATASET_ID, TABLE_ID, date_input):
    TABLE_FULL_ID = f'{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}'   
    query = f'''
    SELECT CountryCode, COUNT(*) AS Count, AVG(DocTone) AS Tone
    FROM `{TABLE_FULL_ID}` 
    WHERE DATE(DateTime) = '{date_input.strftime('%Y-%m-%d')}'
    GROUP BY CountryCode
    '''
    return query

@st.cache_resource
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

@st.cache_resource
def data_query(PROJECT_ID, DATASET_ID, TABLE_ID):
    TABLE_FULL_ID = f'{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}'   
    query = f'''
    SELECT * EXCEPT(`Country Name`,
    `Indicator Name`, `Indicator Code`, `Unnamed: 68`)
    FROM `{TABLE_FULL_ID}` 
    '''
    return query
