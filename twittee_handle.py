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


def search_specific_handle(username,daylimit=7,keywords=[],blacklist=[],whitelist=[],limit = 10):

    limit = limit - 10

    DEBUG_MODE = False
    final_data = []
    # Warn user if keyword argument is not a list #
    if type(keywords) != list:
        return "Function's keyword argument should be a list."
    # ------------------------------------------- #


    #Setting variables for search_specific_handle()

    search_url = "https://api.twitter.com/2/users/by/username/"

    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    search_url += username
    # -------------------------------------------- #


    # Sending the request and recieving an endpoint json response
    response = requests.request("GET", search_url, headers = headers)
    endpoint_response = response.json()

    # print(f"\nendpoint_response for {username}:")
    # pp.pprint(endpoint_response)

    # ----------------------    --------------------------------------
    if DEBUG_MODE:
        print(endpoint_response)

    # Set the user_id and set a search_url for that id's tweets
    try:
        user_id = response.json()["data"]["id"]
        if DEBUG_MODE:
            print(user_id)
    except:
        print("Handle does not exist")
        return None

    search_url = "https://api.twitter.com/2/users/{}/tweets".format(user_id)

    #Setting the timedelta
    # Crate a date/time object that is acceptable by twitter API to use start_time
    now = datetime.datetime.now()
    d = datetime.timedelta(days = daylimit)
    a = now - d
    a = str(a).replace(" ","T")
    match = re.findall(pattern="\.\d+",string=a)[0]
    a = a.replace(match,"") + "Z"
    # --------------------------------------------------------------------------- #
    if DEBUG_MODE:
        print(a)


    returned = 0
    # Query for the twitter API request
    query_params = {
                    'max_results': '10',
                    'tweet.fields': 'text,created_at,id,lang,entities',
                    'expansions': 'author_id',
                    'user.fields': 'id,name,username,entities,url',
                    'start_time':f'{a}',
                    }
    # --------------------------------- #

    # Send the request using search_url, parameters and headers set above and recieve a json response from endpoint.
    response = requests.request("GET", search_url,params=query_params, headers = headers)
    endpoint_response = response.json()
    # --------------------------------------------------------------------
    if DEBUG_MODE:
        print(endpoint_response)
        with open('endpoint_response.json','w') as fh:
            fh.write(json.dumps(endpoint_response,indent=2))

        print("Waiting for input before processing endpoint_response")
        input()
    # --------------------------------------------------------------------   
    if 'meta' in endpoint_response:
        if 'result_count' in endpoint_response['meta']:
            if endpoint_response['meta']['result_count'] == 0:
                print('No tweet returned from this handle.')
                return []
    for tweet in endpoint_response['data']:

        # TO REVIEW TWEET RESPONSE
        # print(f"\ntweet:")
        # pp.pprint(endpoint_response)

        processed_tweet = {
            'username': '{}'.format(username),
            'created_at': '{}'.format(tweet['created_at']),
            'text': '{}'.format(tweet['text']),
            'lang': '{}'.format(tweet['lang']),
            'author_url': '{}'.format("https://twitter.com/"+username),
            'urls': [],
            'author_id': user_id,
            'tweet_id': tweet['id'],
            'tweet_url': f"https://twitter.com/{username}/status/{tweet['id']}",

        }


        #Author_webiste_url
        if 'entities' in endpoint_response['includes']['users'][0]:
            if 'url' in endpoint_response['includes']['users'][0]['entities']:
                processed_tweet['author_website_url'] = endpoint_response['includes']['users'][0]['entities']['url']['urls'][0]['expanded_url']
            else:
                processed_tweet['author_website_url'] = None
        else:
            processed_tweet['author_website_url'] = None

        if DEBUG_MODE:
            print('author webiste url ==> ',processed_tweet['author_website_url'])

        #Entities (urls)
        final_urls = []
        if 'entities' in tweet:
            for key in tweet['entities']:

                if key != 'urls':
                    continue
                else:
                    for url in tweet['entities']['urls']:
                        if 'twitter.com' not in url['expanded_url']:
                            # Try to get actual_url from shoretened_url

                            try:
                                shortened_url = url['expanded_url']

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
                                    print("Couldn't convert:", str(url), " skipping..\n")
                                    final_urls.append(url)
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
        
        if final_urls != []:
            processed_tweet['urls'] = final_urls
            all_keywords_found = True
            
            for keyword in keywords:
                if keyword in processed_tweet['text']:
                    continue
                else:
                    all_keywords_found = False
                    break
            if all_keywords_found:
                final_data.append(processed_tweet)
                returned += 1

    if 'meta' in endpoint_response:
        if DEBUG_MODE:
            print('\nFound META!\n')
        if 'next_token' in endpoint_response['meta']:
            if DEBUG_MODE:
                print('\nFound next_token!\n')
            next_token = endpoint_response['meta']['next_token']
            token_found = True
        else:
            token_found = False
    else:
        token_found= False

    print('Processed first page got {} tweet'.format(returned))



    while token_found:
        if limit != -10:
            if returned >= limit:
                    token_found = False
                    break

        found_this_step = 0
        #Setting the timedelta
        # Crate a date/time object that is acceptable by twitter API to use start_time
        now = datetime.datetime.now()
        d = datetime.timedelta(days = daylimit)
        a = now - d
        a = str(a).replace(" ","T")
        match = re.findall(pattern="\.\d+",string=a)[0]
        a = a.replace(match,"") + "Z"
        # --------------------------------------------------------------------------- #
        if DEBUG_MODE:
            print(a)



        # Query for the twitter API request
        query_params = {
                        'max_results': '10',
                        'tweet.fields': 'text,created_at,id,lang,entities',
                        'expansions': 'author_id',
                        'user.fields': 'id,name,username,entities,url',
                        'start_time':f'{a}',
                        'pagination_token': next_token
                        }
        # --------------------------------- #

        # Send the request using search_url, parameters and headers set above and recieve a json response from endpoint.
        response = requests.request("GET", search_url,params=query_params, headers = headers)

        endpoint_response = response.json()
        if 'data' not in endpoint_response:
            print("No data in next page")
            token_found = False
            break
        # --------------------------------------------------------------------
        if DEBUG_MODE:
            print(endpoint_response)
            with open('endpoint_response.json','w') as fh:
                fh.write(json.dumps(endpoint_response,indent=2))

            print("Waiting for input before processing endpoint_response")
            input()
        # --------------------------------------------------------------------        
        for tweet in endpoint_response['data']:

            print(f"\nendpoint_response['data']= {endpoint_response['data']}\n")

            processed_tweet = {
                'username': '{}'.format(username),
                'created_at': '{}'.format(tweet['created_at']),
                'text': '{}'.format(tweet['text']),
                'lang': '{}'.format(tweet['lang']),
                'author_url': '{}'.format("https://twitter.com/"+username),
                'entities': {'urls':[]},
                'author_id': user_id,
                'tweet_id': tweet['id'],
                'tweet_url': tweet['tweet_url'],

            }


            #Author_webiste_url
            if 'entities' in endpoint_response['includes']['users'][0]:
                if 'url' in endpoint_response['includes']['users'][0]['entities']:
                    processed_tweet['author_website_url'] = endpoint_response['includes']['users'][0]['entities']['url']['urls'][0]['expanded_url']
                else:
                    processed_tweet['author_website_url'] = None
            else:
                processed_tweet['author_website_url'] = None

            if DEBUG_MODE:
                print('author webiste url ==> ',processed_tweet['author_website_url'])

            #Entities (urls)
            final_urls = []
            if 'entities' in tweet:
                for key in tweet['entities']:

                    if key != 'urls':
                        continue
                    else:
                        for url in tweet['entities']['urls']:
                            if 'twitter.com' not in url['expanded_url']:

                                # Try to get actual_url from shoretened_url

                                try:
                                    shortened_url = url['expanded_url']

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
                                        print("Couldn't convert:", str(url), " skipping..\n")
                                        final_urls.append(url)
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
            
            if final_urls != []:
                processed_tweet['entities']['urls'] = final_urls
                all_keywords_found = True
                """
                for keyword in keywords:
                    if keyword in processed_tweet['text']:
                        continue
                    else:
                        all_keywords_found = False
                        break
                """
                if all_keywords_found:
                    final_data.append(processed_tweet)
                    found_this_step += 1

        returned += found_this_step

        if 'meta' in endpoint_response:
            if DEBUG_MODE:
                print('\nFound META!\n')
            if 'next_token' in endpoint_response['meta'] and 'data' in endpoint_response:
                if DEBUG_MODE:
                    print('\nFound more data with next_token!\n')
                next_token = endpoint_response['meta']['next_token']
                token_found = True
            else:
                token_found = False



    # --------------------------------------------------------------------
    if DEBUG_MODE:
        print(final_data)
        with open('endpoint_response.json','w') as fh:
            fh.write(json.dumps(final_data,indent=2))
    # --------------------------------------------------------------------

    return final_data



# Original contributor: E Y S



########################################################################################################

if __name__ == '__main__':

    import time
    start_time = time.time()

    import pprint
    pp = pprint.PrettyPrinter(indent=4)

    print()
    print()
    print('-------------------------------')
    print(f"{os.path.basename(__file__)}")
    
    keywords = []

    username = 'McNeese'

    tweet_data = search_specific_handle(username,daylimit=7,keywords=keywords,blacklist=[],whitelist=[],limit = 10)

    for tweet in tweet_data:

        print()
        print()
        pp.pprint(tweet)
    
    print('-------------------------------')
    run_time = round((time.time() - start_time), 1)
    if run_time > 60:
        print(f'{os.path.basename(__file__)} finished in {run_time/60} minutes.')
    else:
        print(f'{os.path.basename(__file__)} finished in {run_time}s.')
    print()