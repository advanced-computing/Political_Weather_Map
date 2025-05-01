import streamlit as st
import requests
from bs4 import BeautifulSoup
from pycountry import countries

# ------------------Load Country Code Mapping Data------------------
# Fetch and Parse FIPS to ISO Mappings
@st.cache_data
def get_fips_to_iso(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    fips_to_iso = {}
    table = soup.find('table')
    for row in table.find_all('tr')[1:]:
        cols = row.find_all('td')
        fips_code = cols[1].text.strip()
        iso_code = cols[2].text.strip()
        fips_to_iso[fips_code] = iso_code

    return fips_to_iso

# Fetch and Parse ISO Alpha-2 to FIPS Mappings
@st.cache_data
def get_iso_to_fips(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    iso_to_fips = {}
    table = soup.find('table')
    for row in table.find_all('tr')[1:]:
        cols = row.find_all('td')
        iso_alpha2 = cols[2].text.strip()
        fips_code = cols[1].text.strip()
        iso_to_fips[iso_alpha2] = fips_code

    return iso_to_fips

# ------------------Convert Country Codes------------------
# Convert FIPS to ISO Alpha-2 Country Codes
def fips_to_iso2(url, articles, column):
    fips_to_iso = get_fips_to_iso(url)
    articles.loc[:, column] = articles[column].replace(fips_to_iso)
    return articles

# Convert ISO Alpha-2 to FIPS Country Codes
def iso2_to_fips(url, data_list):
    iso_to_fips = get_iso_to_fips(url)
    return [iso_to_fips.get(code, code) for code in data_list]

# Convert ISO Alpha-2 to Alpha-3 Country Codes
def iso2_to_iso3(alpha2_code):
    """Convert Alpha-2 country code to Alpha-3 country code."""
    try:
        return countries.get(alpha_2=alpha2_code).alpha_3
    except AttributeError:
        return None

# Convert ISO Alpha-3 to Alpha-2 Country Codes 
def iso3_to_iso2(alpha3_code):
    try:
        return countries.get(alpha_3=alpha3_code).alpha_2
    except AttributeError:
        return None

# Convert FIPS to ISO Alpha-3 Country Codes 
def enrich_country_codes(df, url, country_col='CountryCode'):
    df = fips_to_iso2(url, df, country_col)
    df['Alpha3Code'] = df['CountryCode'].apply(iso2_to_iso3)
    return df

# ------------------Get unique list of Alpha-3 country codes from the dataset------------------
def get_country_list(df):
    return sorted(df['Alpha3Code'].dropna().unique())
