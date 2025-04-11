import streamlit as st
import pandas as pd
import json
from google.cloud import bigquery
from google.oauth2 import service_account
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from proposal import display_proposal
from data_processing import melt_clean_data, fetch_bigquery_data, article_groupby_query, article_country_query, data_query
from country import fips_to_iso2, iso2_to_fips, iso2_to_iso3, iso3_to_iso2, get_country_list
from visualization import plot_choropleth, plot_immigration_trends, fig_sct
import time
start = time.perf_counter()

st.set_page_config(layout='wide')

st.title('Political Weather Map')
st.write('Unveil the link between immigration rate and tones toward immigrants.')

# User input
st.sidebar.markdown('## Filter')
date_input = st.sidebar.date_input('Select a Date from 2021/01/01',
                                   value=pd.to_datetime('2025-02-01'))

# Access to BigQuery
credentials_info = json.loads(st.secrets['bigquery']['credentials_json'])
credentials = service_account.Credentials.from_service_account_info(
    credentials_info)
client = bigquery.Client(
    credentials=credentials, project=credentials.project_id)
    
# Load Data
query_article_groupby = article_groupby_query(
    'political-weather-map', 'articles', 'immigration', date_input)
query_img = data_query('political-weather-map', 'WorldBankData', 'Immigration')
query_pop = data_query('political-weather-map', 'WorldBankData', 'Population')

df_article = fetch_bigquery_data(client, query_article_groupby)
df_img = fetch_bigquery_data(client, query_img)
df_pop = fetch_bigquery_data(client, query_pop)
df_country = pd.read_csv('country.csv')
    
# Prepare Data
url = 'https://www.geodatasource.com/resources/tutorials/international-country-code-fips-versus-iso-3166/?form=MG0AV3'
articles = fips_to_iso2(url, df_article, 'CountryCode')
articles.loc[:,'Alpha3Code'] = articles['CountryCode'].apply(iso2_to_iso3)
imgs = melt_clean_data(df_img, 'Immigrants')
pops = melt_clean_data(df_pop, 'Populations')

# Merge Data
imgs_pops = pd.merge(imgs, pops, on=['Country Code', 'Year'])
imgs_pops['Rate(%)'] = imgs_pops['Immigrants']/imgs_pops['Populations']*100
imgs_pops['Alpha3Code'] = imgs_pops['Country Code']

# Filter Articles
if date_input.year >= 2024:
    imgs_date = imgs_pops[imgs_pops['Year'].dt.year == 2023]
else:
    imgs_date = imgs_pops[imgs_pops['Year'].dt.year == date_input.year]

# Filter Option
st.sidebar.markdown('### International Level')
region_options = ['World'] + df_country['region'].unique().tolist()
selected_region = st.sidebar.selectbox('Select Region', region_options)
if selected_region == 'World':
    sub_region_options=['All'] + df_country['sub-region'].unique().tolist()
else:
    sub_region_options = (
        ['All'] + 
        df_country[df_country['region'] == selected_region
            ]['sub-region'].unique().tolist())

selected_sub_region = st.sidebar.selectbox(
    'Select Sub-region', sub_region_options)
if selected_region != 'World':
    selected_countries = df_country[
        df_country['region'] == selected_region
        ]['alpha-3'].tolist()
else:
    selected_countries = df_country['alpha-3'].tolist()
if selected_sub_region != 'All':
    selected_countries = df_country[
        df_country['sub-region'] == selected_sub_region
        ]['alpha-3'].tolist()

st.sidebar.markdown('### Country Level')
country_list = get_country_list(imgs_pops)
selected_countries_iso = st.sidebar.multiselect(
    'Select Countries', country_list, default=['CAN','DEU'])
min_year = imgs_pops['Year'].dt.year.min()
max_year = imgs_pops['Year'].dt.year.max()
start_year, end_year = st.sidebar.slider(
    'Select Year Range', min_year, max_year, (min_year, max_year))
event_name = st.sidebar.text_input(' Write any intervention event',
                                   'Syrian War')
highlight_start, highlight_end = st.sidebar.slider(
    'Highlight Period', min_year, max_year, (2011, 2023))

# Rank Data
selected_articles = articles[articles['Alpha3Code'].isin(selected_countries)]
articles_tone_rank = selected_articles[['Tone', 'Alpha3Code']].sort_values(
    by='Tone', ascending=False).reset_index(drop=True)
articles_tone_rank.index += 1
articles_tone_rank.index.name = 'Rank'

selected_imgs_date = imgs_date[imgs_date['Alpha3Code'].isin(selected_countries)]
imgs_pops_rank = selected_imgs_date[['Rate(%)', 'Alpha3Code']].sort_values(
    by='Rate(%)', ascending=False).reset_index(drop=True)
imgs_pops_rank.index += 1
imgs_pops_rank.index.name = 'Rank'

# Scatter Plot Data
scts = pd.merge(articles[['Tone', 'Alpha3Code']], imgs_date, on='Alpha3Code')

# Plotting
fig_articles = plot_choropleth(
    selected_articles, 
    'Count', 
    'Number of Articles about Immigrants by Country')
fig_tones = plot_choropleth(
    selected_articles, 
    'Tone', 
    'Mean Tone toward Immigrants by Country')
fig_imgs = plot_choropleth(
    selected_imgs_date, 
    'Rate(%)', 
    'New Immigration Rate per Capita (%) by Country')

# Streamlit
tab1, tab2, tab3 = st.tabs(
    ['Proposal','International Level Analysis','Country Level Analysis'])

with tab1:
    display_proposal() 

with tab2:
    col1, col2 = st.columns([1,1])
    # Scatter Plot
    with col1:
        st.write('#### Immigration & Article Sentiment)') 
        scts = scts[scts['Alpha3Code'].isin(selected_countries)]
        st.plotly_chart(fig_sct(scts), use_container_width=True)
        st.write('This figure maps immigration rates by country and '
            'shows their correlation with anti-immigrant sentiment '
            'in a scatter plot.') 

    # Map    
    with col2:
        st.write('#### Data Map')
        if 'map_option' not in st.session_state:
            st.session_state.map_option = 'Number of Articles'
        if st.session_state.map_option == 'Number of Articles':
            st.plotly_chart(fig_articles, use_container_width=True)
        elif st.session_state.map_option == 'Mean Article Tones':
            st.plotly_chart(fig_tones, use_container_width=True)
        else:
            st.plotly_chart(fig_imgs, use_container_width=True)
        st.write('This figure shows three types of maps to '
                'understand the global position of countries in a map.')            
        option = st.radio(
            'Select Data to Display:', 
            ['Number of Articles', 'Mean Article Tones', 'Immigrant Rate'],
            index=['Number of Articles',
                   'Mean Article Tones',
                   'Immigrant Rate'].index(st.session_state.map_option),
            key='map_option'
        )

    # Rank
    st.write('#### Rank of Countries')
    col1, col2 = st.columns(2)
    with col1:
        st.write('**Rank of Attitude toward Immigration**')
        st.dataframe(articles_tone_rank)
    with col2:
        st.write('**Rank of Annual New Immigration per capita**')
        st.dataframe(imgs_pops_rank)

with tab3:
    col3, col4 = st.columns([1,1])
    # Word Cloud
    with col3:
        st.write('#### Word Cloud by Country')
        selected_countries_iso2 = [
            iso3_to_iso2(code) for code in selected_countries_iso]
        selected_countries_fips = iso2_to_fips(url, selected_countries_iso2)
        query_article_country = article_country_query(
            'political-weather-map', 'articles', 'immigration',
            date_input, selected_countries_fips)
        df_wordcloud = fetch_bigquery_data(client, query_article_country)
        text = " ".join(df_wordcloud['ContextualText'].dropna())
        wordcloud = WordCloud(
            width=700, height=400, 
            background_color='white').generate(text)
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        ax.set_title(f'Word Cloud for {", ".join(selected_countries_iso)}')
        st.pyplot(fig, use_container_width=True)
        st.write('Users can explore a news word cloud to uncover '
                 'dominant narratives and key topics by selecting a country, '
                 'helping you predict causal relationships.')

    # Trends by Country
    with col4:
        st.write('#### Immigration Rate Trends')             
        plot_immigration_trends(
            imgs_pops, selected_countries_iso, start_year, end_year, 
            highlight_start, highlight_end, event_name)
        st.write('Track trends over time to see how events, '
                 'such as wars and elections, shaped immigration rates of'
                 'selected countries, revealing their true impact.')

end = time.perf_counter()
elapsed = end - start
print(f'Time taken: {elapsed:.2f} seconds')