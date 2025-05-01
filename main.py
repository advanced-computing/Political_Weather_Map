import streamlit as st
import pandas as pd
import json
from google.cloud import bigquery
from google.oauth2 import service_account
from proposal import display_proposal
from data_processing import melt_clean_data, fetch_bigquery_data, article_groupby_query, data_query
from data_processing import stats_year_query, stats_month_query, stats_date_query 
from country import enrich_country_codes
from sidebar import sidebar_input_data, sidebar_international, sidebar_country, sidebar_event
from visualization import plot_choropleth, make_rank_df
from tab import render_scatter_plot, render_data_map, render_trend_tone, render_trend_img, render_wordcloud
import time

start = time.perf_counter()

# ------------------Write Title------------------
st.set_page_config(layout='wide')
st.title('Political Weather Map')
st.write('Unveil the link between immigration rate and tones toward immigrants.')

# ------------------Sidebar Select a Date------------------
date_input = sidebar_input_data()

# ------------------Load and Clean Data------------------
# Access to BigQuery
credentials_info = json.loads(st.secrets['bigquery']['credentials_json'])
credentials = service_account.Credentials.from_service_account_info(
    credentials_info)
client = bigquery.Client(
    credentials=credentials, project=credentials.project_id)
    
# Load Data
project = 'political-weather-map'
dataset_article = 'articles'
dataset_wb = 'WorldBankData'
table_img_article = 'immigration'
table_img_wb = 'Immigration'
table_pop_wb = 'Population'
query_date = date_input

list_article = [project, dataset_article, table_img_article, query_date]
list_img = [project, dataset_wb, table_img_wb]
list_pop = [project, dataset_wb, table_pop_wb]

df_article = fetch_bigquery_data(client, article_groupby_query(*list_article))
df_stats_year = fetch_bigquery_data(client, stats_year_query(*list_article))
df_stats_month = fetch_bigquery_data(client, stats_month_query(*list_article))
df_stats_date = fetch_bigquery_data(client, stats_date_query(*list_article))
df_img = fetch_bigquery_data(client, data_query(*list_img))
df_pop = fetch_bigquery_data(client, data_query(*list_pop))
df_country = pd.read_csv('country.csv')
    
# Clean Data
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

# ------------------Sidebar Filter Options------------------
# Select Region and Sub-region for International Level Analysis
selected_countries = sidebar_international(df_country)

# Select Countries for Country Level Analysis
selected_countries_iso, start_year, end_year = sidebar_country(imgs_pops)
event_name, highlight_start, highlight_end = sidebar_event(imgs_pops)

# ------------------Create Filtered Data------------------
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

# ------------------Main Page's Tabs------------------
tab1, tab2, tab3 = st.tabs(
    ['Proposal','International Level Analysis','Country Level Analysis'])

with tab1: # Proposal
    display_proposal() 

with tab2: #International Level Analysis
    col1, col2 = st.columns([1,1])
    with col1: # Immigration & Article Sentiment
        render_scatter_plot(scts_year, scts_month, 
                            scts_date, selected_countries)

    with col2: # Data Map
        render_data_map(fig_articles, fig_tones, fig_imgs)

    col3, col4 = st.columns(2)
    with col3: # Rank of Attitude toward Immigration
        st.write('#### Rank of Attitude toward Immigration')
        st.dataframe(articles_tone_rank)
        
    with col4: # Rank of Annual New Immigration per Capita
        st.write('#### Rank of Annual New Immigration per Capita')
        st.dataframe(imgs_pops_rank)

with tab3: # Country Level Analysis
    col5, col6 = st.columns([1,1])
    with col5: # Article Tone Trends
        render_trend_tone(client, url, 
                          selected_countries_iso, start_year, end_year)

    with col6: # Immigration Rate Trends
        render_trend_img(imgs_pops, selected_countries_iso, start_year, 
                         end_year, highlight_start, highlight_end, event_name)
        
    # Word Cloud by Country
    render_wordcloud(client, url, selected_countries_iso, date_input)

end = time.perf_counter()
print(f'Time taken: {end - start:.2f} seconds')