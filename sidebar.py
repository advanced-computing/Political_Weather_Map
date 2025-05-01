import streamlit as st
import pandas as pd
from country import get_country_list
from datetime import datetime, timedelta

# ------------------Input Date------------------
def sidebar_input_data():
    date_input = st.sidebar.date_input(
        'Select a Date from 2018/01/01', value=pd.to_datetime('2025-02-01'),
    min_value=pd.to_datetime('2018-01-01'),
    max_value= pd.to_datetime(datetime.today() - timedelta(days=1)))
    return date_input

# ------------------International Level------------------
def sidebar_international(df_country):
    st.sidebar.markdown('### International Level')
    
    region_options = ['World'] + df_country['region'].dropna().unique().tolist()
    selected_region = st.sidebar.selectbox('Select Region', region_options)

    if selected_region == 'World':
        sub_region_options=['All'] + df_country['sub-region'].unique().tolist()
    else:
        sub_region_options = (
            ['All'] + df_country[df_country['region'] == selected_region
                ]['sub-region'].unique().tolist())
            
    selected_sub_region = st.sidebar.selectbox('Select Sub-region', sub_region_options)
    region_df = df_country.copy()
    if selected_region != 'World':
        region_df = region_df[region_df['region'] == selected_region]
    if selected_sub_region != 'All':
        region_df = region_df[region_df['sub-region'] == selected_sub_region]

    return region_df['alpha-3'].tolist()

# ------------------Country Level------------------
# Select Countries
def sidebar_country(imgs_pops):
    st.sidebar.markdown('### Country Level')

    country_list = get_country_list(imgs_pops)
    selected_countries_iso = st.sidebar.multiselect(
        'Select Countries', country_list, default=['SWE','POL','DEU'])

    min_year = imgs_pops['Year'].dt.year.min() 
    max_year = imgs_pops['Year'].dt.year.max()
    
    default_start_year = max(min_year, 1990)
    start_year, end_year = st.sidebar.slider(
        'Select Year Range', min_year, max_year, (default_start_year, max_year))

    return selected_countries_iso, start_year, end_year

# Event
def sidebar_event(imgs_pops):
    event_name = st.sidebar.text_input(' Write any intervention event',
                                   'Syrian War')
    
    min_year = imgs_pops['Year'].dt.year.min() 
    max_year = imgs_pops['Year'].dt.year.max()

    highlight_start, highlight_end = st.sidebar.slider(
        'Highlight Period', min_year, max_year, (2011, 2023))
    
    return event_name, highlight_start, highlight_end
