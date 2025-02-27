import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import plotly.express as px
from pycountry import countries
import os

st.title('Political Weather Map by Country')
st.write('Team: Charlotte Bacchetta, Samuel Bennett, Hiroyuki Oiwa')
st.write('This project aims to assess how much immmigration rates of a country'
        ' are associated with its tone towards immigrants in news articles')

# Function to load data
def load_data(file_name):
    path = os.path.join(os.path.dirname(__file__), file_name)
    return pd.read_csv(path)

# Function to select columns
def select_columns(df_article):
    columns = ['DateTime',
               'CountryCode',
               'Title',
               'ContextualText',
               'DocTone',
               'URL'
               ]
    df_article['DateTime'] = pd.to_datetime(df_article['DateTime'])
    return df_article[columns]

# Function to convert original country code to alpha2 codes
def code_mapping(articles, column):
    url = 'https://www.geodatasource.com/resources/tutorials/international-country-code-fips-versus-iso-3166/?form=MG0AV3'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    fips_to_iso = {}
    table = soup.find('table')
    for row in table.find_all('tr')[1:]: 
        cols = row.find_all('td')
        fips_code = cols[1].text.strip()
        iso_code = cols[2].text.strip()
        fips_to_iso[fips_code] = iso_code 

    articles.loc[:, column] = articles[column].replace(fips_to_iso)
    return articles

# Function to convert alpha2 to alpha3 country codes
def convert_to_alpha3(alpha2_code):
    try:
        return countries.get(alpha_2=alpha2_code).alpha_3
    except AttributeError:
        return None

# Function to melt and clean data
def melt_clean_data(df, value_name):
    df_melted = df.melt(
        id_vars=['Country Code'], 
        var_name='Year', 
        value_name=value_name
        )
    df_melted['Year'] = pd.to_datetime(df_melted['Year'], format='%Y')
    return df_melted

# Functon to plot map
def plot_choropleth(data, value, title):
    fig = px.choropleth(
        data, 
        locations='Alpha3Code', 
        color=value, 
        hover_name='Alpha3Code', 
        color_continuous_scale='Viridis'
        )
    fig.update_geos(
        showcoastlines=True, 
        coastlinecolor='Black', 
        showland=True, 
        landcolor='white'
        )
    fig.update_layout(
        title=title, 
        geo=dict(showframe=False, showcoastlines=True)
        )
    return fig

# Load Data
df_article = load_data('gdelt_20230204.csv')
df_img = load_data('immigratation.csv')
df_pop = load_data('population.csv')

# Prepare Data
articles = select_columns(df_article)
articles = code_mapping(articles, 'CountryCode')
articles.loc[:, 'Alpha3Code'] = articles['CountryCode'].apply(convert_to_alpha3)
imgs = melt_clean_data(df_img, 'Immigrants')
pops = melt_clean_data(df_pop, 'Populations')

# Merge Data
imgs_pops = pd.merge(imgs, pops, on=['Country Code', 'Year'])
imgs_pops['Rate(%)'] = imgs_pops['Immigrants']/imgs_pops['Populations']*100
imgs_pops['Alpha3Code'] = imgs_pops['Country Code']

# User input
date_input = st.date_input('Select a Date', value=pd.to_datetime('2023-02-04'))
st.write('We currently only have data for one date, 2023/02/04. '
         'We will include all the dates in a later phase of the project')

# Filter articles
articles = articles[articles['ContextualText']
                    .str.contains('immigra', case=False, na=False)]
articles_date = articles[articles['DateTime'].dt.date == date_input]
articles_country = articles_date.groupby('CountryCode')['DateTime']\
    .count().reset_index(name='Count')
articles_country.loc[:, 'Alpha3Code'] = articles_country['CountryCode']\
    .apply(convert_to_alpha3)
articles_tone = articles_date.groupby('CountryCode')['DocTone']\
    .mean().reset_index(name='Tone')
articles_tone.loc[:, 'Alpha3Code'] = articles_tone['CountryCode']\
    .apply(convert_to_alpha3)
imgs_date = imgs_pops[imgs_pops['Year'].dt.year == date_input.year]

# Scatter Plot Data
scts = pd.merge(articles_tone, imgs_date, on='Alpha3Code')

# Plotting
fig_articles = plot_choropleth(
    articles_country, 
    'Count', 
    'Number of Articles about Immigrants by Country')
fig_tones = plot_choropleth(
    articles_tone, 
    'Tone', 
    'Mean Tone toward Immigrants by Country')
fig_imgs = plot_choropleth(
    imgs_date, 
    'Rate(%)', 
    'New Immigration Rate per Capita (%) by Country')

fig_scts = px.scatter(
    scts, 
    x='Rate(%)', 
    y='Tone', 
    text='Alpha3Code',
    title='Tone toward Immigrants vs Immigration Rate per Capita(%) by State',
    hover_data={'Alpha3Code': True, 'Rate(%)': True, 'Tone': True},
    trendline='ols',
    color_discrete_sequence=['black'],
    trendline_color_override='red'
)
fig_scts.update_traces(textposition='top center')

# Streamlit
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Main Page", "Second Page"])

if page == "Main Page":
    st.title('Main Page')
    st.write('On this page we show data for articles on immigration on a map')
    st.write('Articles Data Sample', articles.sample(5))
    st.plotly_chart(fig_articles)
    st.plotly_chart(fig_tones)
else:
    st.title('Immigrant Trend by Country')
    st.write('On this page we show immigration rate per country on a map and '
        'how that is associated with tone toward immigrants in a scatter plot')
    st.write('Immigration Data Sample', imgs_pops.sample(5))
    st.write('Data from World Bank. Rate(%) is Immigrants / Population')
    st.plotly_chart(fig_imgs)
    st.plotly_chart(fig_scts)