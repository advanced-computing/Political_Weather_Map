import plotly.express as px
import streamlit as st
import plotly.graph_objects as go

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
    fig_scts.update_layout(width=700,
                           height=400,
                            xaxis_title='Immigration Rate(%) (Immigrants / Population)',
                            yaxis_title='Article Tone toward Immigrants')
    return fig_scts

def plot_choropleth(data, value, title):
    """Create a choropleth map visualization."""
    fig = px.choropleth(
        data, 
        locations='Alpha3Code', 
        color=value, 
        hover_name='Alpha3Code', 
        color_continuous_scale='Viridis',
        range_color=[data[value].quantile(0.1), data[value].quantile(0.9)]
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
    fig.update_layout(width=700, height=400)
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
    st.plotly_chart(fig, use_container_width=True)

def plot_immigration_trends(df, selected_countries,
                            start_year, end_year,
                            highlight_start=None,
                            highlight_end=None,
                            event_name=''):
    """Plot immigration rate trends over time for selected countries."""
    df_filtered = df[(df['Year'].dt.year >= start_year) & 
                     (df['Year'].dt.year <= end_year) & 
                     (df['Alpha3Code'].isin(selected_countries))]
    fig = px.line(df_filtered,
                  x='Year',
                  y='Rate(%)',
                  color='Alpha3Code',
                  markers=True)
    if highlight_start and highlight_end:
        fig.add_trace(go.Scatter(
            x=[
                highlight_start, highlight_end, 
                highlight_end, highlight_start, highlight_start],
            y=(
                [df_filtered['Rate(%)'].min()] * 2 + 
                [df_filtered['Rate(%)'].max()] * 2 + 
                [df_filtered['Rate(%)'].min()]
               ),
            fill='toself',
            fillcolor='rgba(255, 0, 0, 0.2)', 
            line=dict(color='rgba(255, 0, 0, 0)'),
            name=event_name if event_name else "Highlighted Period"
        ))
    st.plotly_chart(fig, use_container_width=True)
    
def plot_tone_trends(df_tone, selected_countries, start_year, end_year):
    df_tone['Year'] = df_tone['Year'].astype(int)
    df_tone = df_tone[
        (df_tone['Year'] >= start_year) & 
        (df_tone['Year'] <= end_year) & 
        (df_tone['Alpha3Code'].isin(selected_countries))
    ]
    fig = px.line(df_tone,
                  x='Year',
                  y='Tone',
                  color='Alpha3Code',
                  markers=True)
    fig.update_layout(xaxis_title='Year',
                      yaxis_title='Article Tone toward Immigrants')

    st.plotly_chart(fig, use_container_width=True)
    
def make_rank_df(df, value_col, country_col='Alpha3Code'):
    ranked = df[[value_col, country_col]].sort_values(by=value_col, ascending=False)
    ranked = ranked.reset_index(drop=True)
    ranked.index += 1
    ranked.index.name = 'Rank'
    return ranked

