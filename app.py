import streamlit as st
import pandas as pd
import plotly.express as px
from pycountry import countries

# Load Data
path_article = r'C:\Users\oiwah\OneDrive\デスクトップ\2025_Spring_Python\project\Political_Weather_Map\gdelt_20230204stre.csv'
path_img = r'C:\Users\oiwah\OneDrive\デスクトップ\2025_Spring_Python\project\Political_Weather_Map\immigratation.csv'

df_article = pd.read_csv(path_article)
df_img = pd.read_csv(path_img)

articles = pd.DataFrame()
articles['DateTime'] = df_article['DateTime']
articles['CountryCode'] = df_article['CountryCode']
articles['Title'] = df_article['Title']
articles['ContextualText'] = df_article['ContextualText']
articles['DocTone'] = df_article['DocTone']
articles['URL'] = df_article['URL']

# Clean Articles Data
country_code_mapping = {
    'EI': 'IE',
    'EZ': 'ES',
    'IZ': 'IT',
    'HA': 'HR',
    'LO': 'LI',
    'OS': 'AT',
}

articles['CountryCode'] = articles['CountryCode'].replace(country_code_mapping)

def convert_to_alpha3(alpha2_code):
    try:
        return countries.get(alpha_2=alpha2_code).alpha_3
    except AttributeError:
        return None

articles['Alpha3Code'] = articles['CountryCode'].apply(convert_to_alpha3)

# Clean Immigrants Data
imgs = df_img.melt(id_vars=['Country Code'], var_name='Year', value_name='Immigrants')
imgs['Year'] = pd.to_datetime(imgs['Year'], format='%Y')

# Add Alpha3Code to imgs DataFrame
imgs['Alpha3Code'] = imgs['Country Code']

# Select Data
date_input = st.date_input("Select a Date", value=pd.to_datetime('2023-02-17'))
date_str = date_input.strftime('%Y')

articles_date = articles[articles['DateTime'].str.startswith(date_str)]
articles_country = articles_date.groupby('CountryCode')['DateTime'].count().reset_index(name='Count')
articles_country['Alpha3Code'] = articles_country['CountryCode'].apply(convert_to_alpha3)

imgs_date = imgs[imgs['Year'].dt.year == date_input.year]
imgs_country = imgs_date.groupby('Alpha3Code')['Immigrants'].sum().reset_index(name='Count')

# Illustrate figure
fig_articles = px.choropleth(articles_country, locations='Alpha3Code', color='Count', hover_name='CountryCode', color_continuous_scale="Viridis")
fig_articles.update_geos(showcoastlines=True, coastlinecolor="Black", showland=True, landcolor="white")
fig_articles.update_layout(title="Global Political News Heatmap by Country", geo=dict(showframe=False, showcoastlines=True))

fig_imgs = px.choropleth(imgs_country, locations='Alpha3Code', color='Count', hover_name='Alpha3Code', color_continuous_scale="Viridis")
fig_imgs.update_geos(showcoastlines=True, coastlinecolor="Black", showland=True, landcolor="white")
fig_imgs.update_layout(title="Global Immigrants Heatmap by Country", geo=dict(showframe=False, showcoastlines=True))

# Streamlit
st.title('Global Political News Heatmap')
st.write('Articles Data Sample', articles.sample(5))
st.write('Imgs Data Sample', imgs.sample(5))
st.plotly_chart(fig_articles)
st.plotly_chart(fig_imgs)