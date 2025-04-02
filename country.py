import requests
from bs4 import BeautifulSoup
from pycountry import countries

def fips_to_iso2(articles, column):
    """Convert FIPS country codes to ISO Alpha-2 country codes."""
    url = 'https://www.geodatasource.com/resources/tutorials/international-country-code-fips-versus-iso-3166/?form=MG0AV3'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    fips_to_iso = {}
    table = soup.find('table')
    for row in table.find_all('tr')[1:]: 
        cols = row.find_all('td')
        fips_code = cols[1].text.strip()
        iso_code = cols[2].text.strip()
        fips_to_iso[fips_code] = iso_code 

    articles.loc[:, column] = articles[column].replace(fips_to_iso)
    return articles

def iso2_to_fips(data_list):
    """Convert ISO Alpha-2 country codes to FIPS country codes."""
    url = 'https://www.geodatasource.com/resources/tutorials/international-country-code-fips-versus-iso-3166/?form=MG0AV3'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    iso_to_fips = {}
    table = soup.find('table')
    for row in table.find_all('tr')[1:]:  
        cols = row.find_all('td')
        iso_alpha2 = cols[2].text.strip()  
        fips_code = cols[1].text.strip()   
        iso_to_fips[iso_alpha2] = fips_code

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

def get_country_list(df):
    """Get unique list of Alpha-3 country codes from the dataset."""
    return sorted(df['Alpha3Code'].dropna().unique())
