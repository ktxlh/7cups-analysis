"""Scraper for listeners' public, anonymous profile data

1. SALT Lab was granted permission to utilize this info by 7 Cups via Haard Shah, as long as no actual screen names are made public.
2. Robot access is allowed by https://www.7cups.com/robots.txt :
```
User-agent: *
Disallow: /connect/js/
Disallow: /connect/* 
Disallow: /member/
Disallow: /forum/*
Disallow: /dashboard/
Disallow: /path/
```
"""
import requests
from typing import List

from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm


def get_7cups_profile(username: str):
    page = requests.get(f"https://www.7cups.com/@{username}")
    if page.status_code != 200:
        raise Exception(f"Username {username} returns status code {page.status_code}")

    soup = BeautifulSoup(page.content, 'html.parser')
    data_html = soup.find_all("table", class_="listenerData")
    data_dfs = [pd.read_html(str(x), index_col=0)[0] for x in data_html]

    # data_dfs[0:3] are attribute key-value pairs
    df = pd.concat(data_dfs[:3])
    # data_dfs[3] contains Categories but not every Listener configures that
    categories = data_dfs[3].index.tolist()[1:] if len(data_dfs) == 4 else []

    data_row = df.transpose()
    data_row["Username"] = username
    data_row["Categories"] = ", ".join(categories)
    return data_row


def get_7cups_profiles_from_list(usernames: List[str]):
    rows = []
    for username in tqdm(usernames):
        rows.append(get_7cups_profile(username))
    df = pd.concat(rows)
    df = df.reset_index(drop=True)
    return df


if __name__ == "__main__":
    user_file = "/Users/shanglinghsu/Library/CloudStorage/OneDrive-GeorgiaInstituteofTechnology/7 Cups Participants.xlsx"
    # I added extra rows in my sheet for other info. You may not need this.
    user_df = pd.read_excel(user_file)

    user_df = user_df[user_df["Username"].notna()]
    user_df = user_df[user_df["Category Chosen"].notna()]
    user_df.reset_index(inplace=True, drop=True)
    
    df = get_7cups_profiles_from_list(user_df["Username"])
    df.to_csv("profiles.csv")
