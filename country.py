import streamlit as st
import requests
from bs4 import BeautifulSoup
from pycountry import countries

@st.cache_data
def get_fips_to_iso(url):
    """Fetch and parse FIPS to ISO mappings (Cache the parsed data)."""
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

@st.cache_data
def get_iso_to_fips(url):
    """Fetch and parse ISO Alpha-2 to FIPS mappings (Cache the parsed data)."""
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

def fips_to_iso2(url, articles, column):
    """Convert FIPS country codes to ISO Alpha-2 country codes."""
    fips_to_iso = get_fips_to_iso(url)
    articles.loc[:, column] = articles[column].replace(fips_to_iso)
    return articles

def iso2_to_fips(url, data_list):
    """Convert ISO Alpha-2 country codes to FIPS country codes."""
    iso_to_fips = get_iso_to_fips(url)
    return [iso_to_fips.get(code, code) for code in data_list]

def iso2_to_iso3(alpha2_code):
    """Convert Alpha-2 country code to Alpha-3 country code."""
    try:
        return countries.get(alpha_2=alpha2_code).alpha_3
    except AttributeError:
        return None

def iso3_to_iso2(alpha3_code):
    """Convert Alpha-2 country code to Alpha-3 country code."""
    try:
        return countries.get(alpha_3=alpha3_code).alpha_2
    except AttributeError:
        return None

def enrich_country_codes(df, url, country_col='CountryCode'):
    df = fips_to_iso2(url, df, country_col)
    df['Alpha3Code'] = df['CountryCode'].apply(iso2_to_iso3)
    return df

def get_country_list(df):
    """Get unique list of Alpha-3 country codes from the dataset."""
    return sorted(df['Alpha3Code'].dropna().unique())
