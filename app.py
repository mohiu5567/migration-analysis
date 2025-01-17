

import time
import praw
from prawcore.exceptions import ResponseException, RequestException

try:
    reddit = praw.Reddit(
        client_id="COm5Ms_7OsuACtim62OEnA",
        client_secret="q5_pjZ0dhTq_o_mXoIRMaL_TAEsX0w",
        user_agent="migration analysis",
    )

    subreddit = reddit.subreddit("IWantOut")
    posts = []
    
    # Use a loop to avoid exceeding the rate limit
    for post in subreddit.new(limit=1000):
        posts.append(post.title)
        time.sleep(1)  # Add a small delay between requests to avoid rate limits

except ResponseException as e:
    print("Authentication failed. Check your credentials.")
    print(e)
except RequestException as e:
    print("Request failed. Check your internet connection or Reddit API status.")
    print(e)
except Exception as e:
    print("An unexpected error occurred.")
    print(e)




import re

pattern = r"(?P<origin>[A-Za-z\s]+)\s*->\s*(?P<destination>[A-Za-z\s]+)"
countries = []
for title in posts:
    match = re.search(pattern, title)
    if match:
        countries.append((match.group("origin").strip(), match.group("destination").strip()))
        
        
from rapidfuzz import process, fuzz

def normalize_country(name, country_list):
    match, score = process.extractOne(name, country_list, scorer=fuzz.ratio)
    return match if score > 85 else None


import pandas as pd

df = pd.DataFrame(countries, columns=["Origin", "Destination"])
origin_counts = df["Origin"].value_counts()
destination_counts = df["Destination"].value_counts()


import wbgapi as wb

gdp_data = wb.data.DataFrame("NY.GDP.PCAP.CD", mrv=1)  # Most recent value
gdp_data.reset_index(inplace=True)
gdp_data.rename(columns={"NY.GDP.PCAP.CD": "GDP_per_capita"}, inplace=True)


gdp_data["Country"] = gdp_data["Country"].apply(lambda x: normalize_country(x, df["Origin"].unique()))



merged_df = pd.merge(
    df,
    gdp_data,
    how="left",
    left_on="Origin",
    right_on="Country"
)

origin_gdp = merged_df.groupby("Origin").agg({
    "GDP_per_capita": "mean",
    "Origin": "size"
}).rename(columns={"Origin": "Mentions"}).reset_index()

import matplotlib.pyplot as plt
import seaborn as sns

sns.scatterplot(data=origin_gdp, x="GDP_per_capita", y="Mentions")
plt.title("Origin Countries: Mentions vs GDP per Capita")
plt.show()


import streamlit as st

st.title("Migration Patterns from Reddit")
st.dataframe(merged_df)

scatter_option = st.selectbox("Select scatterplot", ["Origin", "Destination"])
if scatter_option == "Origin":
    sns.scatterplot(data=origin_gdp, x="GDP_per_capita", y="Mentions")
    plt.title("Origin Countries: Mentions vs GDP per Capita")
else:
    sns.scatterplot(data=destination_gdp, x="GDP_per_capita", y="Mentions")
    plt.title("Destination Countries: Mentions vs GDP per Capita")
st.pyplot(plt)

