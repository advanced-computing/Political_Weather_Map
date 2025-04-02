import streamlit as st

def display_proposal():
    st.markdown("""
    # Updated Proposal

    ## 1. What dataset are you going to use?
    - **Articles**: [Gdelt](https://www.gdeltproject.org/)
    - **Immigration**: [World Bank](https://data.worldbank.org/indicator/SM.POP.NETM)
    - **Population**: [World Bank](https://data.worldbank.org/indicator/SP.POP.TOTL)
    - **Country Codes & Regions**: [ISO-3166](https://github.com/lukes/ISO-3166-Countries-with-Regional-Codes/blob/master/all/all.csv)

    ## 2. What are your research questions?
    - How are immigration rates associated with tone towards immigrants in news articles?
    - At the international level, do different groups of countries show different trends?
    - At the country level, what drives opinions about immigrants?

    ## 3. What is your target visualization?
    - **Scatter Plot**: Tone toward Immigrants vs Immigration Rate per Capita (%)
    - **Map**: 
      - Number of Articles about Immigrants by Country
      - Mean Article Tone toward Immigrants by Country
      - New Immigration Rate per Capita (%) by Country
    - **Rank of Countries**: 
      - Rank of Attitude toward Immigration
      - Rank of Annual New Immigration per Capita
    - **Trend Line**: 
      - Immigration Rate Trends
      - Number of Articles Trends*
      - Mean Tone Trends*
      - (*These graphs require more data from Google BigQuery in Part 5.*)
    - **Word Cloud**: Popular Words in Articles by Country

    ## 4. What are your known unknowns?
    Anti-immigrant movements have gained momentum in many countries. However, the interactions between influencing factors remain unclear.

    - **Geopolitical Context**: 
      - Wars in neighboring countries may heighten security concerns, increase anti-immigration rhetoric, and shift media tone.
    - **Political Context**: 
      - Media-influential anti-immigration parties may amplify negative narratives, increasing anti-immigration articles.

    This project provides tools to analyze how immigration-related news tone correlates with immigration rates across various perspectives.

    ## 5. What challenges do you anticipate?
    - Currently, only English articles are included; expanding to other languages requires additional search terms.
    - Immigration data is yearly, limiting short-term trend analysis.
    - The latest available immigration data is from 2023, which may misrepresent 2024–2025 trends.
    - Geopolitical events, such as wars, could distort correlations between immigration rates and media tone.
    """)

