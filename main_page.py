import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from data_processing import load_data, select_columns, melt_clean_data
from country import code_mapping, convert_to_alpha3, get_country_list
from visualization import plot_choropleth, plot_immigration_trends

st.title('Political Weather Map')
st.write('Team: Charlotte Bacchetta, Samuel Bennett, Hiroyuki Oiwa')
st.write('This project aims to assess how much immigration rates of a country'
        ' are associated with its tone towards immigrants in news articles.')

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
st.sidebar.markdown("## Select a Date")
date_input = st.sidebar.date_input('', value=pd.to_datetime('2023-02-04'))
st.sidebar.write('We currently only have data for one date, 2023/02/04. '
                 'We will include all the dates in a later phase of the project.')

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

# Rank Data
articles_tone_rank = articles_tone[['Tone', 'Alpha3Code']].sort_values(
    by='Tone', ascending=False).reset_index(drop=True)
articles_tone_rank.index += 1
articles_tone_rank.index.name = 'Rank'

imgs_pops_rank = imgs_pops[['Rate(%)', 'Alpha3Code']].sort_values(
    by='Rate(%)', ascending=False).reset_index(drop=True)
imgs_pops_rank.index += 1
imgs_pops_rank.index.name = 'Rank'

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

def fig_sct(scts):
    fig_scts = px.scatter(
        scts, 
        x='Rate(%)', 
        y='Tone', 
        text='Alpha3Code',
        hover_data={'Alpha3Code': True, 'Rate(%)': True, 'Tone': True},
        trendline='ols',
        color_discrete_sequence=['black'],
        trendline_color_override='red'
    )
    fig_scts.update_traces(textposition='top center')
    return fig_scts

df_country = pd.read_csv(r'C:\Users\oiwah\OneDrive\デスクトップ\2025_Spring_Python\project\Political_Weather_Map\Political_Weather_Map\country.csv')

# Streamlit
st.sidebar.title('Navigation')
page = st.sidebar.radio('Go to', ['Proposal', 'International Level Analysis', 'Country Level Analysis'])

if page == 'Proposal':
    st.title('XXX')

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
        sub_region_options = ['All'] + df_country['sub-region'].unique().tolist()
    else:
        sub_region_options = ['All'] + df_country[df_country['region'] == selected_region]['sub-region'].unique().tolist()
    selected_sub_region = st.sidebar.selectbox('Select Sub-region', sub_region_options)
    if selected_region != 'World':
        selected_countries = df_country[df_country['region'] == selected_region]['alpha-3'].tolist()
    else:
        selected_countries = df_country['alpha-3'].tolist()
    if selected_sub_region != 'All':
        selected_countries = df_country[df_country['sub-region'] == selected_sub_region]['alpha-3'].tolist()
    scts = scts[scts['Alpha3Code'].isin(selected_countries)]
    st.plotly_chart(fig_sct(scts))
    st.write('Immigration Rate = Immigrants / Population. Immigration Data is from World Bank. Article Data is from GDELT.') 

    # Map
    st.write('### Data Map')
    st.write('Users can intuitively understand the position of that country in the world through the map.')
    option = st.radio('Select Data to Display:', ['Number of Articles', 'Mean Article Tones', 'Immigrant Rate'])
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
    st.write('Users can track trends over time to see how events, such as wars and elections, '
             'shaped immigration rates by country '
             'by selecting countries, revealing their true impact.')
    
    # Show Trend
    st.sidebar.title('Filter Options')
    country_list = get_country_list(imgs_pops)
    selected_countries = st.sidebar.multiselect('Select Countries', country_list, default=country_list[:3])
    min_year = imgs_pops['Year'].dt.year.min()
    max_year = imgs_pops['Year'].dt.year.max()
    start_year, end_year = st.sidebar.slider("Select Year Range", min_year, max_year, (min_year, max_year))

    st.write('This plot shows the immigration trends for selected countries over time.')
    plot_immigration_trends(imgs_pops, selected_countries, start_year, end_year)

    # Word Cloud
    st.write('### Word Cloud by Country')
    st.write('Users can explore a news word cloud to uncover dominant narratives and key topics '
             'by selecting a country, helping you predict causal relationships.')
    articles_word = articles[articles['Alpha3Code'].isin(selected_countries)]['ContextualText'].values[0]
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(articles_word)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    ax.set_title(f'Word Cloud for {", ".join(selected_countries)}')
    st.pyplot(fig)