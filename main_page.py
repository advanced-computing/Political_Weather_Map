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

st.title('Political Weather Map')
st.write('Team: Charlotte Bacchetta, Samuel Bennett, Hiroyuki Oiwa')
st.write('This project aims to assess how much immigration rates of a country'
        ' are associated with its tone towards immigrants in news articles.')

# User input
st.sidebar.markdown('# Select a Date')
date_input = st.sidebar.date_input('', value=pd.to_datetime('2025-02-01'))
st.sidebar.write('Data is available from 2023/01/01.')

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

# Rank Data
articles_tone_rank = df_article[['Tone', 'Alpha3Code']].sort_values(
    by='Tone', ascending=False).reset_index(drop=True)
articles_tone_rank.index += 1
articles_tone_rank.index.name = 'Rank'

imgs_pops_rank = imgs_pops[['Rate(%)', 'Alpha3Code']].sort_values(
    by='Rate(%)', ascending=False).reset_index(drop=True)
imgs_pops_rank.index += 1
imgs_pops_rank.index.name = 'Rank'

# Scatter Plot Data
scts = pd.merge(articles[['Tone', 'Alpha3Code']], imgs_date, on='Alpha3Code')

# Plotting
fig_articles = plot_choropleth(
    articles, 
    'Count', 
    'Number of Articles about Immigrants by Country')
fig_tones = plot_choropleth(
    articles, 
    'Tone', 
    'Mean Tone toward Immigrants by Country')
fig_imgs = plot_choropleth(
    imgs_date, 
    'Rate(%)', 
    'New Immigration Rate per Capita (%) by Country')

# Streamlit
st.sidebar.title('Navigation')
page = st.sidebar.radio('Go to',
                        ['Proposal', 
                         'International Level Analysis', 
                         'Country Level Analysis'])

if page == 'Proposal':
    display_proposal() 
elif page == 'International Level Analysis':
    st.title('International Level Analysis')

    # Scatter Plot
    st.write('### Tone toward Immigrants vs Immigration Rate per Capita(%)') 
    st.write('This figure maps immigration rates by country and '
        'shows their correlation with anti-immigrant sentiment in a scatter plot. '
        'As immigration rises, sentiment tends to worsen. '
        'Trend lines by country group reveal its tolerance levels and '
        'help predict shifts in national sentiment.') 

    st.sidebar.title('Filter Options')
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
    scts = scts[scts['Alpha3Code'].isin(selected_countries)]
    st.plotly_chart(fig_sct(scts))
    st.write('Immigration Rate = Immigrants / Population.') 
    
    # Map
    st.write('### Data Map')
    st.write('Users can intuitively understand the position of '
             'that country in the world through the map.')
    option = st.radio(
        'Select Data to Display:', 
        ['Number of Articles', 'Mean Article Tones', 'Immigrant Rate'])
    if option == 'Number of Articles':
        st.plotly_chart(fig_articles)
    elif option == 'Mean Article Tones':
        st.plotly_chart(fig_tones)
    else:
        st.plotly_chart(fig_imgs)
        
    # Rank
    st.write('### Rank of Countries')
    st.write('Users can understand the position of each country in the world.')
    col1, col2 = st.columns(2)
    with col1:
        st.write('**Rank of Attitude toward Immigration**')
        st.dataframe(articles_tone_rank)
    with col2:
        st.write('**Rank of Annual New Immigration per capita**')
        st.dataframe(imgs_pops_rank)

else:
    st.title('Country Level Analysis')
    st.write('### Trends by Country')
    st.write('Users can track trends over time to see how events, '
             'such as wars and elections, shaped immigration rates by country '
             'by selecting countries, revealing their true impact.')
    
    # Show Trend
    st.sidebar.title('Filter Options')
    country_list = get_country_list(imgs_pops)
    selected_countries_iso = st.sidebar.multiselect(
        'Select Countries', country_list, default=['CAN','DEU'])
    min_year = imgs_pops['Year'].dt.year.min()
    max_year = imgs_pops['Year'].dt.year.max()
    start_year, end_year = st.sidebar.slider(
        'Select Year Range', min_year, max_year, (min_year, max_year))

    event_name = st.sidebar.text_input('Event Name', 'Syrian Civil War')
    highlight_start, highlight_end = st.sidebar.slider(
        'Highlight Period', min_year, max_year, (2011, 2023))

    st.write('This plot shows the immigration trends '
             'for selected countries over time.')
    plot_immigration_trends(
        imgs_pops, selected_countries_iso, start_year, end_year, 
        highlight_start, highlight_end, event_name)

    # Word Cloud
    st.write('### Word Cloud by Country')
    st.write('Users can explore a news word cloud to uncover '
             'dominant narratives and key topics by selecting a country, '
             'helping you predict causal relationships.')
    selected_countries_iso2 = [
        iso3_to_iso2(code) for code in selected_countries_iso]
    selected_countries_fips = iso2_to_fips(url, selected_countries_iso2)
    query_article_country = article_country_query(
        'political-weather-map', 'articles', 'immigration',
        date_input, selected_countries_fips)
    df_wordcloud = fetch_bigquery_data(client, query_article_country)
    text = " ".join(df_wordcloud['ContextualText'].dropna())
    wordcloud = WordCloud(
        width=800, height=400, 
        background_color='white').generate(text)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    ax.set_title(f'Word Cloud for {", ".join(selected_countries_iso)}')
    st.pyplot(fig)

end = time.perf_counter()
elapsed = end - start
print(f'Time taken: {elapsed:.2f} seconds')
