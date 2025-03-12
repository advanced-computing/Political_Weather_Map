import plotly.express as px
import streamlit as st

def plot_choropleth(data, value, title):
    """Create a choropleth map visualization."""
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

def plot_trends(df, selected_countries, start_year, end_year, y):
    """Plot trends over time for selected countries."""
    df_filtered = df[(df['Year'].dt.year >= start_year) & 
                     (df['Year'].dt.year <= end_year) & 
                     (df['Alpha3Code'].isin(selected_countries))]
    fig = px.line(df_filtered,
                  x='Year',
                  y=f'{y}',
                  color='Alpha3Code',
                  markers=True,
                  title=f'{y} Trends by Country')
    st.plotly_chart(fig)

def plot_immigration_trends(df, selected_countries, start_year, end_year):
    """Plot immigration rate trends over time for selected countries."""
    df_filtered = df[(df['Year'].dt.year >= start_year) & 
                     (df['Year'].dt.year <= end_year) & 
                     (df['Alpha3Code'].isin(selected_countries))]
    fig = px.line(df_filtered,
                  x='Year',
                  y='Rate(%)',
                  color='Alpha3Code',
                  markers=True,
                  title='Immigration Rate Trends by Country')
    st.plotly_chart(fig)
