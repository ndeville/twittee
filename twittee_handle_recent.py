import datetime
from multiprocessing.connection import answer_challenge
import requests
import json
import urllib3
import certifi

http = urllib3.PoolManager(ca_certs=certifi.where())

payload = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0'}

import os
from requests.sessions import InvalidSchema
import time
from geopy.geocoders import Nominatim
from pprint import pprint
# import pprint
# pp = pprint.PrettyPrinter(indent=4)

import csv
import re

from dotenv import load_dotenv
load_dotenv()
bearer_token = os.getenv("TOKEN")


list_blacklist = []
error_list = []

try:
    with open('/Users/nicolas/Python/indeXee/data/blacklist_domain.csv', 'r', newline='', encoding='UTF-8') as h:
        reader = csv.reader(h, delimiter=",")
        data = list(reader)
        for row in data:
            list_blacklist.append(row[0])
except:
    pass


def search_handle_recent(username,daylimit=7,keywords=[],blacklist=[],whitelist=[]):
    DEBUG_MODE = False
    # Warn the user if the keyword argument is not a list
    if type(keywords) != list:
        return "Function's keyword argument must be a list."
    # -------------------------------------------------- #

    # Check if handle includes '@' if it does, remove it
    if username.startswith('@'):
        username = username.replace('@','')
    # ------------------------------------------------ #

    # Endpoint to use
    search_url = "https://api.twitter.com/2/tweets/search/recent" 


    # Header to send bearer token to twitter API
    headers = {"Authorization": "Bearer {}".format(bearer_token)}


    # Create a string keyword query with the provided keyword list from function.
    
    if keywords != []:
        query = ""


        add_after = []
        for keyword in keywords:
            if ' ' in keyword:
                add_after.append(keyword)
            else:
                last_keywords = []
                last_keywords.append(keyword.capitalize())
                last_keywords.append(keyword)
                last_keywords.append(keyword.lower())
                temp_keys = []
                for kw in last_keywords:
                    if kw not in temp_keys:
                        temp_keys.append(kw)

                keywords = temp_keys

                for keyword in keywords:
                    if keyword == keywords[0]: query += '('
                    if keyword != keywords[-1]:
                        query += keyword+" OR "
                    else:
                        query += keyword+') '
                

        # query.strip()
        query = query.strip()
        if len(add_after) > 0:
            for kw in add_after:
                query += '"'+kw+'" '


    else:
        query = ""

    print(f"Query: {query}")
    # ------------------------------------------------------------------- #

    

    # Crate a date/time object that is acceptable by twitter API to use start_time
    now = datetime.datetime.now()
    d = datetime.timedelta(days = daylimit)
    a = now - d
    a = str(a).replace(" ","T")
    match = re.findall(pattern="\.\d+",string=a)[0]
    a = a.replace(match,"") + "Z"
    # --------------------------------------------------------------------------- #

 
        
    # Query for the twitter API request
    query_params = {'query': f'{query}has:links (from:{username}) -is:retweet -is:reply',
                    'max_results': '{}'.format(10),
                    'tweet.fields': 'text,created_at,id,lang,entities',
                    'expansions': 'author_id',
                    'user.fields': 'id,name,username,entities,url',
                    'start_time':f'{a}',
                    }
    # --------------------------------- #

    if DEBUG_MODE: 
        print(f'\n\nQuery Params: {query_params}\n\n')
        input()

    # Send the request using search_url, parameters and headers set above and recieve a json response from endpoint.
    response = requests.request("GET", search_url,params=query_params, headers = headers)

    endpoint_response = response.json()
    # --------------------------------------------------------------------

    if DEBUG_MODE: 
        print('\n\nEndpoint Response: ',endpoint_response,'\n')
        input()

    # FINAL DATA TO RETURN
    final_data = []
    # -------------------#



    # Warn if no tweet is found in 7 days or endpoint returns an error by printing the error.
    try:
        if endpoint_response['meta']['result_count'] == 0:
            print('No matched tweet found in 7 days.')
            return None
    except:
        print("\n\n\n Endpoint Response Error Check Log: \n",endpoint_response)
        return None
    # --------------------------------------------------------------------------------------#


    # For each individual tweet in the endpoint response, create a tweet_data list to store the data and get the data from endpoint response
    for tweet in endpoint_response["data"]:

        tweet_data = {
            "entities":{"urls":None}

        }


        # Get every 'expanded_url' except if there is twitter.com in link
        tweet_data["entities"]["urls"] = [gag["expanded_url"] for gag in tweet["entities"]["urls"] if "twitter.com" not in gag["expanded_url"]]
        # ------------------------------------------------------------- #



        #Try to gather author_website_url of the author, if not available, append []
        try:
            tweet_data['author_website_url'] = endpoint_response['includes']['users'][0]['entities']['url']['urls'][0]['expanded_url']
        except:
            tweet_data['author_website_url'] = None
        # ------------------------------------------------------------------------ #

        # Set the author_url using the handle
        tweet_data["author_url"] = "https://twitter.com/"+username
        # ----------------------------------#


        # Final urls to store
        final_urls = []

        # For every url stored in tweet_data
        for link in tweet_data["entities"]["urls"]:

                        # Try to get actual_url from shoretened_url
                        try:
                            shortened_url = link

                            print("Gathering actual url from shortened url...")
                            time.sleep(0.1)
                            r = requests.get(shortened_url, headers={"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"})
                            actual_url = r.url

                            print(shortened_url[0:25]+"..."," >>> ", actual_url[0:25]+"...","\n")
                            final_urls.append(actual_url)
                        # -----------------------------------------


                        # If cant, use another method, if that fails too return the shoretened url
                        except:
                            try:
                                time.sleep(0.1)
                                actual_url = requests.get(shortened_url).url


                                print(shortened_url[0:25]+"..."," >>> ", actual_url[0:25]+"...","\n")
                                final_urls.append(actual_url)
                            except:
                                print("Couldn't convert:", str(link), " skipping..\n")
                                final_urls.append(link)
                        # ----------------------------------
        # Blacklist and whitelist !!
        for link in final_urls[:]:

            skip_url_w = False
            skip_url_b = False

            for item in blacklist:
                if item in link:
                    skip_url_b = True
                    break

            for item in whitelist:
                if item not in link:
                    skip_url_w = True
                    break

            if skip_url_b or skip_url_w:
                final_urls.remove(link)

        # Set all of the tweet_data values before exiting from the tweet
        tweet_data["entities"]["urls"] = final_urls
        tweet_data["username"] = username 
        tweet_data["author_id"] = tweet["author_id"]
        tweet_data["created_at"] = tweet["created_at"]
        tweet_data["text"] = tweet["text"]
        tweet_data["lang"] = tweet["lang"]
        tweet_data["tweet_id"] = tweet["id"]
        tweet_data["tweet_url"] = "https://twitter.com/"+username+"/status/"+tweet_data["tweet_id"]
        # -------------------------------------------------------------#

        # Exit the individual tweet
        final_data.append(tweet_data)   
        # ------------------------ #




    # Final lookthrough of tweets before returning the final_data


    # Remove the tweet if there is no url left
    for tweet in final_data[:]:
        if len(tweet["entities"]["urls"]) == 0 or tweet["entities"]["urls"] == []:
            final_data.remove(tweet)

    # Remove the url from the tweet if it includes youtube.com
    for tweet in final_data:
        for url in tweet["entities"]["urls"][:]:
            if "youtube.com" in url:
                tweet["entities"]["urls"].remove(url)

    # Last check if there is any no url tweet left
    for tweet in final_data[:]:
        if len(tweet["entities"]["urls"]) == 0:
            final_data.remove(tweet)
    

    # Return
    return final_data