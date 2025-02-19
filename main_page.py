import streamlit as st
import pandas as pd
import plotly.express as px
from pycountry import countries
import os

st.title('Political Weather Map by Country')
st.write('Team: Charlotte Bacchetta, Samuel Bennett, Hiroyuki Oiwa')

# Load Data
path_article = os.path.join(os.path.dirname(__file__), 'gdelt_20230204.csv')
path_img = os.path.join(os.path.dirname(__file__), 'immigratation.csv')
path_pop = os.path.join(os.path.dirname(__file__), 'population.csv')

df_article = pd.read_csv(path_article)
df_img = pd.read_csv(path_img)
df_pop = pd.read_csv(path_pop)

articles = pd.DataFrame()
articles['DateTime'] = df_article['DateTime']
articles['CountryCode'] = df_article['CountryCode']
articles['Title'] = df_article['Title']
articles['ContextualText'] = df_article['ContextualText']
articles['DocTone'] = df_article['DocTone']
articles['URL'] = df_article['URL']

# Clean Articles Data
country_code_mapping = {
    'ZI': 'ZW',  # Zimbabwe
    'IZ': 'IQ',  # Iraq
    'LA': 'LV',  # Latvia
    'MU': 'MR',  # Mauritania
    'JA': 'JP',  # Japan
    'LY': 'LB',  # Lebanon
    'MC': 'ME',  # Montenegro
    'BR': 'BG',  # Bulgaria
    'BX': 'BE',  # Belgium
    'GR': 'DE',  # Germany
    'GV': 'GN',  # Guinea
    'KU': 'KW',  # Kuwait
    'LG': 'LV',  # Latvia
    'MI': 'MK',  # North Macedonia
    'RI': 'RS',  # Serbia
    'DA': 'DK',  # Denmark
    'EN': 'EE',  # Estonia
    'EI': 'IE',  # Ireland
    'LE': 'LB',  # Lebanon
    'LO': 'LI',  # Liechtenstein
    'PO': 'PT',  # Portugal
    'LH': 'LT',  # Lithuania
    'NU': 'NR',  # Nauru
    'CE': 'CF',  # Central African Republic
    'AY': 'AI',  # Anguilla
    'AJ': 'AZ',  # Azerbaijan
    'CS': 'CZ',  # Czech Republic
    'RP': 'PH',  # Philippines
    'RQ': 'PR',  # Puerto Rico
    'KS': 'XK',  # Kosovo
    'OD': 'OM',  # Oman
    'BF': 'BG',  # Bulgaria
    'PP': 'PW',  # Palau
    'DR': 'DO',  # Dominican Republic
    'AC': 'AQ',  # Antarctica
    'OC': 'AU',  # Australia
    'OS': 'AT',  # Austria
    'RS': 'RU',  # Russia
    'RB': 'RO',  # Romania
    'PU': 'PT',  # Portugal
    'CG': 'CG',  # Congo
    'IV': 'CI',  # Côte d'Ivoire
    'CJ': 'CY',  # Cyprus
    'MP': 'FM',  # Micronesia
    'MB': 'MT',  # Malta
    'HA': 'HR',  # Croatia
}


articles['CountryCode'] = articles['CountryCode'].replace(country_code_mapping)

def convert_to_alpha3(alpha2_code):
    try:
        return countries.get(alpha_2=alpha2_code).alpha_3
    except AttributeError:
        return None

articles['Alpha3Code'] = articles['CountryCode'].apply(convert_to_alpha3)

# Clean Immigrants Data
imgs = df_img.melt(
    id_vars=['Country Code'], 
    var_name='Year', 
    value_name='Immigrants'
    )
imgs['Year'] = pd.to_datetime(imgs['Year'], format='%Y')

# Clean Population Data
pops = df_pop.melt(
    id_vars=['Country Code'], 
    var_name='Year', 
    value_name='Populations'
    )
pops['Year'] = pd.to_datetime(pops['Year'], format='%Y')

# Merge Data
imgs_pops = pd.merge(imgs, pops, on=['Country Code', 'Year'])
imgs_pops['Rate(%)'] = imgs_pops['Immigrants']/imgs_pops['Populations']*100

# Add Alpha3Code to imgs DataFrame
imgs_pops['Alpha3Code'] = imgs_pops['Country Code']

# Select Data
date_input = st.date_input('Select a Date', value=pd.to_datetime('2023-02-04'))
articles = articles[
    articles['ContextualText'].str.contains('immigra', case=False, na=False)
    ]

# Convert articles' DateTime column to datetime
articles['DateTime'] = pd.to_datetime(articles['DateTime'])
articles_date = articles[articles['DateTime'].dt.date == date_input]

articles_country = (
    articles_date
    .groupby('CountryCode')['DateTime']
    .count()
    .reset_index(name='Count')
    )

articles_country['Alpha3Code'] = (
    articles_country['CountryCode']
    .apply(convert_to_alpha3)
    )

articles_tone = (
    articles_date
    .groupby('CountryCode')['DocTone']
    .mean()
    .reset_index(name='Tone')
    )

articles_tone['Alpha3Code'] = (
    articles_tone['CountryCode']
    .apply(convert_to_alpha3)
    )

imgs_date = imgs_pops[imgs_pops['Year'].dt.year == date_input.year]

# Scatter Plot Data
scts = pd.merge(articles_tone, imgs_date, on='Alpha3Code')

# Illustrate figure
fig_articles = px.choropleth(
    articles_country, 
    locations='Alpha3Code', 
    color='Count', 
    hover_name='CountryCode', 
    color_continuous_scale='Viridis'
    )
fig_articles.update_geos(
    showcoastlines=True, 
    coastlinecolor='Black', 
    showland=True, 
    landcolor='white')
fig_articles.update_layout(
    title='Number of Articles about Immigrants by Country', 
    geo=dict(showframe=False, showcoastlines=True)
    )

fig_tones = px.choropleth(
    articles_tone, 
    locations='Alpha3Code', 
    color='Tone', 
    hover_name='CountryCode', 
    color_continuous_scale='Viridis'
    )
fig_tones.update_geos(
    showcoastlines=True, 
    coastlinecolor='Black', 
    showland=True, 
    landcolor='white')
fig_tones.update_layout(
    title='Mean Tone toward Immigrants by Country', 
    geo=dict(showframe=False, showcoastlines=True)
    )

fig_imgs = px.choropleth(
    imgs_date, 
    locations='Alpha3Code', 
    color='Rate(%)', 
    hover_name='Alpha3Code', 
    color_continuous_scale='Viridis'
    )
fig_imgs.update_geos(
    showcoastlines=True, 
    coastlinecolor='Black', 
    showland=True, 
    landcolor='white')
fig_imgs.update_layout(
    title='Immigration Rate per Capita (%) by Country', 
    geo=dict(showframe=False, showcoastlines=True)
    )

fig_scts = px.scatter(
    scts, 
    x='Rate(%)', 
    y='Tone', 
    text='Alpha3Code', 
    title='Tone toward Immigrants vs. Immigration Rate per Capita(%) by Country',
    hover_data={'Alpha3Code': True, 'Rate(%)': True, 'Tone': True},
    trendline='ols',
    color_discrete_sequence=['black'],
    trendline_color_override='red'
    )
fig_scts.update_traces(textposition='top center')
       
# Streamlit
st.write('Articles Data Sample', articles.sample(5))
st.plotly_chart(fig_articles)
st.plotly_chart(fig_tones)