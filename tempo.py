import streamlit as st
import pandas as pd
import plotly.express as px
from pycountry import countries
import os

# Function to load data
def load_data(file_name):
    path = os.path.join(os.path.dirname(__file__), file_name)
    return pd.read_csv(path)

# Function to convert alpha2 to alpha3 country codes
def convert_to_alpha3(alpha2_code):
    try:
        return countries.get(alpha_2=alpha2_code).alpha_3
    except AttributeError:
        return None


def select_columns(df_article):
    articles = pd.DataFrame()
    articles['DateTime'] = pd.to_datetime(df_article['DateTime'])
    articles['CountryCode'] = df_article['CountryCode']
    articles['Title'] = df_article['Title']
    articles['ContextualText'] = df_article['ContextualText']
    articles['DocTone'] = df_article['DocTone']
    articles['URL'] = df_article['URL']
    return articles


# Function to prepare articles data
def prepare_articles(df_article):
    articles = pd.DataFrame()
    articles['DateTime'] = pd.to_datetime(df_article['DateTime'])
    articles['CountryCode'] = df_article['CountryCode']
    articles['Title'] = df_article['Title']
    articles['ContextualText'] = df_article['ContextualText']
    articles['DocTone'] = df_article['DocTone']
    articles['URL'] = df_article['URL']

    country_code_mapping = {
        'ZI': 'ZW', 'IZ': 'IQ', 'LA': 'LV', 'MU': 'MR', 'JA': 'JP',
        'LY': 'LB', 'MC': 'ME', 'BR': 'BG', 'BX': 'BE', 'GR': 'DE',
        'GV': 'GN', 'KU': 'KW', 'LG': 'LV', 'MI': 'MK', 'RI': 'RS',
        'DA': 'DK', 'EN': 'EE', 'EI': 'IE', 'LE': 'LB', 'LO': 'LI',
        'PO': 'PT', 'LH': 'LT', 'NU': 'NR', 'CE': 'CF', 'AY': 'AI',
        'AJ': 'AZ', 'CS': 'CZ', 'RP': 'PH', 'RQ': 'PR', 'KS': 'XK',
        'OD': 'OM', 'BF': 'BG', 'PP': 'PW', 'DR': 'DO', 'AC': 'AQ',
        'OC': 'AU', 'OS': 'AT', 'RS': 'RU', 'RB': 'RO', 'PU': 'PT',
        'CG': 'CG', 'IV': 'CI', 'CJ': 'CY', 'MP': 'FM', 'MB': 'MT',
        'HA': 'HR'
    }
    articles['CountryCode'] = articles['CountryCode'].replace(country_code_mapping)
    articles['Alpha3Code'] = articles['CountryCode'].apply(convert_to_alpha3)
    return articles

# Function to melt and clean data
def melt_clean_data(df, value_name):
    df_melted = df.melt(id_vars=['Country Code'], var_name='Year', value_name=value_name)
    df_melted['Year'] = pd.to_datetime(df_melted['Year'], format='%Y')
    return df_melted

# Load Data
df_article = load_data('gdelt_20230204.csv')
df_img = load_data('immigratation.csv')
df_pop = load_data('population.csv')

# Prepare Data
articles = prepare_articles(df_article)
imgs = melt_clean_data(df_img, 'Immigrants')
pops = melt_clean_data(df_pop, 'Populations')

# Merge Data
imgs_pops = pd.merge(imgs, pops, on=['Country Code', 'Year'])
imgs_pops['Rate(%)'] = imgs_pops['Immigrants']/imgs_pops['Populations']*100
imgs_pops['Alpha3Code'] = imgs_pops['Country Code']

# User input
date_input = st.date_input('Select a Date', value=pd.to_datetime('2023-02-04'))

# Filter articles
articles = articles[articles['ContextualText'].str.contains('immigra', case=False, na=False)]
articles_date = articles[articles['DateTime'].dt.date == date_input]
articles_country = articles_date.groupby('CountryCode')['DateTime'].count().reset_index(name='Count')
articles_country['Alpha3Code'] = articles_country['CountryCode'].apply(convert_to_alpha3)
articles_tone = articles_date.groupby('CountryCode')['DocTone'].mean().reset_index(name='Tone')
articles_tone['Alpha3Code'] = articles_tone['CountryCode'].apply(convert_to_alpha3)
imgs_date = imgs_pops[imgs_pops['Year'].dt.year == date_input.year]

# Scatter Plot Data
scts = pd.merge(articles_tone, imgs_date, on='Alpha3Code')

# Plotting
def plot_choropleth(data, value, title):
    fig = px.choropleth(data, locations='Alpha3Code', color=value, hover_name='Alpha3Code', color_continuous_scale='Viridis')
    fig.update_geos(showcoastlines=True, coastlinecolor='Black', showland=True, landcolor='white')
    fig.update_layout(title=title, geo=dict(showframe=False, showcoastlines=True))
    return fig

fig_articles = plot_choropleth(articles_country, 'Count', 'Number of Articles about Immigrants by Country')
fig_tones = plot_choropleth(articles_tone, 'Tone', 'Mean Tone toward Immigrants by Country')
fig_imgs = plot_choropleth(imgs_date, 'Rate(%)', 'Immigration Rate per Capita (%) by Country')

fig_scts = px.scatter(
    scts, x='Rate(%)', y='Tone', text='Alpha3Code', title='Tone toward Immigrants vs. Immigration Rate per Capita(%) by Country',
    hover_data={'Alpha3Code': True, 'Rate(%)': True, 'Tone': True}, trendline='ols', color_discrete_sequence=['black'], trendline_color_override='red'
)
fig_scts.update_traces(textposition='top center')

# Streamlit
st.write('Articles Data Sample', articles.sample(5))
st.plotly_chart(fig_articles)
st.plotly_chart(fig_tones)
st.plotly_chart(fig_imgs)
st.plotly_chart(fig_scts)