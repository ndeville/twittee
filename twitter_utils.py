import os

from dotenv import load_dotenv
load_dotenv()
bearer_token = os.getenv("TOKEN")

import sys

from dotenv import load_dotenv
load_dotenv()
USER = os.getenv("USER")

import requests

sys.path.append(f"/Users/{USER}/Python/metaurl")

from get.soup import without_js_rendering, with_js_rendering



def url_from_twitter(handle):
    global bearer_token

    if handle.startswith('https://www.twitter.com/'):
        handle = handle.replace('https://www.twitter.com/', '')
        handle = handle.replace('@', '')

    print(f"\nGetting website for {handle}")

    search_url = f"https://api.twitter.com/2/users/by/username/{handle}"
    headers = {"Authorization": f"Bearer {bearer_token}"}
    query_params = {'user.fields': 'entities'}

    response = requests.get(search_url, headers=headers, params=query_params)

    if response.status_code == 200:
        endpoint_response = response.json()
        try:
            user = endpoint_response["data"]
            website_url = user["entities"]["url"]["urls"][0]["expanded_url"]
            print(website_url)
            return website_url
        except KeyError:
            return None
    else:
        print(f"Error: {response.status_code}, {response.json()}")







test = 'https://www.twitter.com/thebpf'

url_from_twitter(test)