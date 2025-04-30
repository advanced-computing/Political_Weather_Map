import streamlit as st
import pandas as pd
import json
from google.cloud import bigquery
from google.oauth2 import service_account
from proposal import display_proposal
from data_processing import melt_clean_data, fetch_bigquery_data, article_groupby_query, data_query
from data_processing import stats_year_query, stats_month_query, stats_date_query 
from country import enrich_country_codes, get_country_list
from visualization import plot_choropleth, make_rank_df
from tab import render_scatter_plot, render_data_map, render_trend_tone, render_trend_img, render_wordcloud
import time

start = time.perf_counter()

st.set_page_config(layout='wide')
st.title('Political Weather Map')
st.write('Unveil the link between immigration rate and tones toward immigrants.')

# Sideber Filter Option 1: Select Date
date_input = st.sidebar.date_input(
    'Select a Date from 2018/01/01', value=pd.to_datetime('2025-02-01'),
    min_value=pd.to_datetime('2018-01-01'), max_value=pd.to_datetime('today'))

# Access to BigQuery
credentials_info = json.loads(st.secrets['bigquery']['credentials_json'])
credentials = service_account.Credentials.from_service_account_info(
    credentials_info)
client = bigquery.Client(
    credentials=credentials, project=credentials.project_id)
    
# Load Data
list_article = ['political-weather-map', 'articles', 'immigration', date_input]
list_img = ['political-weather-map', 'WorldBankData', 'Immigration']
list_pop = ['political-weather-map', 'WorldBankData', 'Population']
df_article = fetch_bigquery_data(client, article_groupby_query(*list_article))
df_stats_year = fetch_bigquery_data(client, stats_year_query(*list_article))
df_stats_month = fetch_bigquery_data(client, stats_month_query(*list_article))
df_stats_date = fetch_bigquery_data(client, stats_date_query(*list_article))
df_img = fetch_bigquery_data(client, data_query(*list_img))
df_pop = fetch_bigquery_data(client, data_query(*list_pop))
df_country = pd.read_csv('country.csv')
    
# Transform Data
url = 'https://www.geodatasource.com/resources/tutorials/international-country-code-fips-versus-iso-3166/?form=MG0AV3'
articles = enrich_country_codes(df_article, url)
stats_year = enrich_country_codes(df_stats_year, url)
stats_month = enrich_country_codes(df_stats_month, url)
stats_date = enrich_country_codes(df_stats_date, url)
imgs = melt_clean_data(df_img, 'Immigrants')
pops = melt_clean_data(df_pop, 'Populations')
imgs_pops = pd.merge(imgs, pops, on=['Country Code', 'Year'])
imgs_pops['Rate(%)'] = imgs_pops['Immigrants']/imgs_pops['Populations']*100
imgs_pops['Alpha3Code'] = imgs_pops['Country Code']
target_year = 2023 if date_input.year >= 2024 else date_input.year
imgs_year = imgs_pops[imgs_pops['Year'].dt.year == target_year]

# Sidebar Filter Option 2: Select Region
st.sidebar.markdown('### International Level')
region_options = ['World'] + df_country['region'].unique().tolist()
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
selected_countries = region_df['alpha-3'].tolist()

# Sidebar Filter Option 3: Select Countries
st.sidebar.markdown('### Country Level')
country_list = get_country_list(imgs_pops)
selected_countries_iso = st.sidebar.multiselect(
    'Select Countries', country_list, default=['SWE','DEU'])
min_year = imgs_pops['Year'].dt.year.min()
max_year = imgs_pops['Year'].dt.year.max()
default_start_year = max(min_year, 1990)
start_year, end_year = st.sidebar.slider(
    'Select Year Range', min_year, max_year, (default_start_year, max_year))

# Sidebar Filter Option 4: Select Event
event_name = st.sidebar.text_input(' Write any intervention event',
                                   'Syrian War')
highlight_start, highlight_end = st.sidebar.slider(
    'Highlight Period', min_year, max_year, (2011, 2023))

# Rank Data
selected_articles = articles[articles['Alpha3Code'].isin(selected_countries)]
articles_tone_rank = make_rank_df(selected_articles, 'Tone')
selected_imgs_date = imgs_year[imgs_year['Alpha3Code'].isin(selected_countries)]
imgs_pops_rank = make_rank_df(selected_imgs_date, 'Rate(%)')

# Scatter Plot Data
scts_year = pd.merge(stats_year[['Tone', 'Alpha3Code']],
                     imgs_year, on='Alpha3Code')
scts_month = pd.merge(stats_month[['Tone', 'Alpha3Code']],
                      imgs_year, on='Alpha3Code')
scts_date = pd.merge(stats_date[['Tone', 'Alpha3Code']],
                     imgs_year, on='Alpha3Code')

# Plot Choropleth
fig_articles = plot_choropleth(selected_articles, 'Count', 
                               'Number of Articles of Immigrants by Country')
fig_tones = plot_choropleth(selected_articles, 'Tone', 
                            'Mean Tone toward Immigrants by Country')
fig_imgs = plot_choropleth(selected_imgs_date, 'Rate(%)', 
                           'New Immigration Rate per Capita (%) by Country')

# Tabs
tab1, tab2, tab3 = st.tabs(
    ['Proposal','International Level Analysis','Country Level Analysis'])

with tab1:
    display_proposal() 

with tab2:
    col1, col2 = st.columns([1,1])
    with col1:
        st.write('#### Immigration & Article Sentiment')
        render_scatter_plot(scts_year, scts_month, 
                            scts_date, selected_countries)

    with col2:
        st.write('#### Data Map')
        render_data_map(fig_articles, fig_tones, fig_imgs)

    col3, col4 = st.columns(2)
    with col3:
        st.write('#### Rank of Attitude toward Immigration')
        st.dataframe(articles_tone_rank)
        
    with col4:
        st.write('#### Rank of Annual New Immigration per Capita')
        st.dataframe(imgs_pops_rank)

with tab3:
    col5, col6 = st.columns([1,1])
    with col5:
        st.write('#### Article Tone Trends')             
        render_trend_tone(client, url, 
                          selected_countries_iso, start_year, end_year)

    with col6:
        st.write('#### Immigration Rate Trends')             
        render_trend_img(imgs_pops, selected_countries_iso, start_year, 
                         end_year, highlight_start, highlight_end, event_name)

    st.write('#### Word Cloud by Country')
    render_wordcloud(client, url, selected_countries_iso, date_input)

end = time.perf_counter()
print(f'Time taken: {end - start:.2f} seconds')