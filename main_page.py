import streamlit as st
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from data_processing import load_data, select_columns, melt_clean_data
from country import code_mapping, convert_to_alpha3, get_country_list
from visualization import plot_choropleth, plot_immigration_trends, fig_sct

st.title('Political Weather Map')
st.write('Team: Charlotte Bacchetta, Samuel Bennett, Hiroyuki Oiwa')
st.write('This project aims to assess how much immigration rates of a country'
        ' are associated with its tone towards immigrants in news articles.')

# Load Data
df_article = load_data('gdelt_20230204.csv')
df_img = load_data('immigratation.csv')
df_pop = load_data('population.csv')
df_country = pd.read_csv('country.csv')

# Prepare Data
articles = select_columns(df_article)
articles = code_mapping(articles, 'CountryCode')
articles.loc[:,'Alpha3Code'] = articles['CountryCode'].apply(convert_to_alpha3)
imgs = melt_clean_data(df_img, 'Immigrants')
pops = melt_clean_data(df_pop, 'Populations')

# Merge Data
imgs_pops = pd.merge(imgs, pops, on=['Country Code', 'Year'])
imgs_pops['Rate(%)'] = imgs_pops['Immigrants']/imgs_pops['Populations']*100
imgs_pops['Alpha3Code'] = imgs_pops['Country Code']

# User input
st.sidebar.markdown("# Select a Date")
date_input = st.sidebar.date_input('', value=pd.to_datetime('2023-02-04'))
st.sidebar.write('We currently only have data for one date, 2023/02/04 '
                 'and will include all the dates in Part 5.')

# Filter Articles
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

# Streamlit
st.sidebar.title('Navigation')
page = st.sidebar.radio('Go to',
                        ['Proposal', 
                         'International Level Analysis', 
                         'Country Level Analysis'])

if page == 'Proposal':
    st.title('Updated Proposal')
    st.write('**1. What dataset are you going to use?**')
    st.write('- Articles: [Gdelt](https://www.gdeltproject.org/)')
    st.write('- Immigration: [World Bank](https://data.worldbank.org/indicator/SM.POP.NETM)')
    st.write('- Population: [World Bank](https://data.worldbank.org/indicator/SP.POP.TOTL)')
    st.write('- Country: [Code / Region]'
             '(https://github.com/lukes/ISO-3166-Countries-with-Regional-Codes/blob/master/all/all.csv)')
    st.write('**2. What are your research questions?**')
    st.write('- How are immigration rates associated with tone '
             'towards immigrants in news articles?')
    st.write('- At the international level, do different groups '
             'of countries show different trends?')
    st.write('- At the country level, what drives opinions about immigrants?')
    st.write('**3. What is your target visualization?**')
    st.write('- Scatter Plot: Tone toward Immigrants '
             'vs Immigration Rate per Capita(%)')
    st.write('- Map: Number of Articles about Immigrants by Country, '
             'Mean Article Tone toward Immigrants by Country, '
             'New Immigration Rate per Capita (%) by Country')
    st.write('- Rank of Countries: Rank of Attitude toward Immigration, '
             'Rank of Annual New Immigration per Capita')
    st.write('- Trend Line: Immigration Rate Trends, '
             'Number of Articles Trends*, MeanTone Trends*')
    st.write('*These graphs cannot be created using only sample data '
             'from articles, so they will be created after utilizing '
             'Google BigQuery in Part 5 to obtain data on articles '
             'spanning decades for all countries.')
    st.write('- Word Cloud: Popular Words in Articles by County')
    st.write('**4. What are your known unknowns?**')
    st.write('In recent years, anti-immigrant movements have been gaining '
             'momentum in many countries, including the United States, '
             'France, and Germany. These movements are often linked to '
             'several factors like the following examples. However, '
             'the precise ways in which these factors interact, '
             'and which one plays the most significant role, remain unclear. '
             'As a result, the underlying mechanisms and root causes driving '
             'anti-immigrant sentiment are still "known, but not understood.')
    st.write('- Geopolitical Context: A neighboring war can heighten '
             'security concerns, political rhetoric, and public anxiety, '
             'leading to an increased anti-immigration articles, '
             'exacerbating public sentiment than expected.'
             'This tool allows users to test hypotheses '
             'by comparing the media tone and immigration rate trends of '
             'all countries with those of a user-selected group. '
             'In this case, neighboring countries of a war-torn nation might '
             'exhibit a lower media tone compared to the general trend.')
    st.write('- Political Context: Anti-immigration parties '
             'with strong media ties may amplify negative narratives, '
             'disproportionately increasing anti-immigration articles. '
             'This tool allows users to test hypotheses '
             'by comparing the media tone trends and a specific event period. '
             'In this case, when anti-immigration party gains power, '
             'media tone may be lower than the general trend.')
    st.write('Thus, this project aims to provide a tool for analyzing '
             'the causes of this phenomenon by comparing the tone of '
             'news articles about immigration as a metric for gauging '
             'public sentiment toward immigrants with the immigration rate '
             'from various perspectives, such as region, trend, and '
             'popular words in news articles.')
    st.write('**5. What challenges do you anticipate?**')
    st.write('- Currently, we only have English articles, but we can include '
             'other languages as well by searching for the words “immigration”'
             ' and “immigrant” in other languages.')
    st.write('- We are limited to yearly immigration data. Therefore, '
             'we do not know how immigration rates change within the year '
             'and how that affects tone on a short-term basis.')
    st.write('- Since 2023 is the latest available immigration data, '
             'we must use it in our scatterplot when analyzing daily DocTone '
             'from 2024 and 2025, which may misrepresent trends. '
             'After taking the entire data of the article tone, '
             'we wil make this modification.')
    st.write('- Note that Geopolitical events, such as wars '
             'in neighboring countries, could drive real increases '
             'in immigration in 2024 and 2025 that are not reflected '
             'in the dataset. This could exaggerate the link '
             'between immigration rates and media tone.')

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
    selected_countries = st.sidebar.multiselect(
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
        imgs_pops, selected_countries, start_year, end_year, 
        highlight_start, highlight_end, event_name)

    # Word Cloud
    st.write('### Word Cloud by Country')
    st.write('Users can explore a news word cloud to uncover '
             'dominant narratives and key topics by selecting a country, '
             'helping you predict causal relationships.')
    articles_word = articles[
        articles['Alpha3Code'].isin(selected_countries)
        ]['ContextualText'].values[0]
    wordcloud = WordCloud(
        width=800, height=400, 
        background_color='white').generate(articles_word)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    ax.set_title(f'Word Cloud for {", ".join(selected_countries)}')
    st.pyplot(fig)