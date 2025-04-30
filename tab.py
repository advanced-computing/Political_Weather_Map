import streamlit as st
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from visualization import fig_sct, plot_tone_trends, plot_immigration_trends
from country import iso3_to_iso2, iso2_to_fips, enrich_country_codes
from data_processing import article_country_query, fetch_bigquery_data, stats_trend_query

def render_scatter_plot(scts_year, scts_month, scts_date, selected_countries):
    scts_year = scts_year[scts_year['Alpha3Code'].isin(selected_countries)]
    scts_month = scts_month[scts_month['Alpha3Code'].isin(selected_countries)]
    scts_date = scts_date[scts_date['Alpha3Code'].isin(selected_countries)]

    options = ['Daily', 'Monthly', 'Yearly']
    
    selected_option = st.radio('Select Period:', options, horizontal=True)

    if selected_option == 'Daily':
        st.plotly_chart(fig_sct(scts_year), use_container_width=True)
    elif selected_option == 'Monthly':
        st.plotly_chart(fig_sct(scts_month), use_container_width=True)
    else:
        st.plotly_chart(fig_sct(scts_date), use_container_width=True)

    st.write('This figure maps immigration rates by country and '
             'shows their correlation with anti-immigrant sentiment '
             'in a scatter plot.')

   
def render_data_map(fig_articles, fig_tones, fig_imgs):
    options = ['Number of Articles', 'Mean Article Tones', 'Immigrant Rate']

    selected_option = st.radio(
        'Select Data to Display:', options, index=0, horizontal=True)

    if selected_option == 'Number of Articles':
        st.plotly_chart(fig_articles, use_container_width=True)
    elif selected_option == 'Mean Article Tones':
        st.plotly_chart(fig_tones, use_container_width=True)
    else:
        st.plotly_chart(fig_imgs, use_container_width=True)

    st.write('This figure shows three types of maps to '
             'understand the global position of countries in a map.')

def render_trend_tone(client, url, selected_countries_iso, start_year, end_year):
    query = stats_trend_query('political-weather-map',
        'articles', 'immigration', start_year, end_year)
    df_tone = fetch_bigquery_data(client, query)
    tone = enrich_country_codes(df_tone, url)
    plot_tone_trends(tone, selected_countries_iso, start_year, end_year)
    st.write('Track trends of article tones toward immigrant over time.')

def render_trend_img(imgs_pops, selected_countries_iso, start_year, end_year, highlight_start, highlight_end, event_name):
    plot_immigration_trends(
        imgs_pops, selected_countries_iso, start_year, end_year, 
        highlight_start, highlight_end, event_name)
    st.write('Track trends over time to see how events, '
             'such as wars and elections, shaped immigration rates of'
             'selected countries, revealing their true impact.')

def render_wordcloud(client, url, selected_countries_iso, date_input):
    selected_countries_iso2 = [
        iso3_to_iso2(code) for code in selected_countries_iso]
    selected_countries_fips = iso2_to_fips(url, selected_countries_iso2)
    query_article_country = article_country_query(
        'political-weather-map', 'articles', 'immigration',
        date_input, selected_countries_fips)
    df_wordcloud = fetch_bigquery_data(client, query_article_country)
    text = " ".join(df_wordcloud['ContextualText'].dropna())
    wordcloud = WordCloud(width=700, height=400,
        background_color='white').generate(text)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    ax.set_title(f'Word Cloud for {", ".join(selected_countries_iso)}')
    st.pyplot(fig, use_container_width=True)
    st.write('Users can explore a news word cloud to uncover '
             'dominant narratives and key topics by selecting a country, '
             'helping you predict causal relationships.')