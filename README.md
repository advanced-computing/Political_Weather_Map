## Political Weather Map

We will assess how much a country's tone towards immigrants in news articles is associated with its immigration rates. For immigration tone, we will use the DocTone column in the GDELT data and filter on "immigra" in the ContextualText column. For immigration rates, we will use immigration data and divide the raw number of immigrants by the population.


[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/advanced-computing/Political_Weather_Map/blob/main/your_notebook.ipynb)


***Steps to Run the app locally:***
1. Clone the Political Weather Map reporistory in your local environment  
2. Create a Service Account key in Google Big Query  
3. Create a secrets.toml file under a new folder called .streamlit
4. In the secrets.toml file, add three lines before the service key and two lines after:
<pre>[bigquery]  
credentials_json = """  
{ 
# Copy and paste your service account key here...    
}  
"""</pre>  
5. In the "private_key" line of your secrets.toml file, replace every occurence of "\n" with "\\\n". You can use ChatGPT to do this quicker.
6. In the terminal, run "streamlit run main_page.py". This will load the app locally.
7. Now you can interact with the app. Read the proposal on the "Proposal" page to understand our app.
8. Then navigate to the "International Level Analysis". You can select a date and country you want to analyze. You will see a scatterplot, map and rank
9. Finally, navigate to "Country Level Analysis". You can select a date and country you want to analyze. You will see immigration rates over time by country and a word cloud. You can also enter events in the "Event Name" input box and choose a highlight period to understand how events imapct immigration rates.
