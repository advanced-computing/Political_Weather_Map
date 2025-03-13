import plotly.express as px
import streamlit as st
import plotly.graph_objects as go

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

def plot_immigration_trends(df, selected_countries, start_year, end_year,
                            highlight_start=None, highlight_end=None, event_name=''):
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
    if highlight_start and highlight_end:
        fig.add_trace(go.Scatter(
            x=[highlight_start, highlight_end, highlight_end, highlight_start, highlight_start],
            y=[df_filtered['Rate(%)'].min()] * 2 + [df_filtered['Rate(%)'].max()] * 2 + [df_filtered['Rate(%)'].min()],
            fill='toself',
            fillcolor='rgba(255, 0, 0, 0.2)', 
            line=dict(color='rgba(255, 0, 0, 0)'),
            name=event_name if event_name else "Highlighted Period"
        ))
    st.plotly_chart(fig)
