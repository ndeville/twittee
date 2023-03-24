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
import csv
import re

from dotenv import load_dotenv
load_dotenv()
bearer_token = os.getenv("TOKEN")

# print(f"\n{bearer_token=}\n")

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



# MOVED TO SEPARATE MODULE
# def search_specific_handle(username,daylimit=7,keywords=[],blacklist=[],whitelist=[],limit = 10):

#     limit = limit - 10

#     DEBUG_MODE = False
#     final_data = []
#     # Warn user if keyword argument is not a list #
#     if type(keywords) != list:
#         return "Function's keyword argument should be a list."
#     # ------------------------------------------- #


#     #Setting variables for search_specific_handle()

#     search_url = "https://api.twitter.com/2/users/by/username/"

#     headers = {"Authorization": "Bearer {}".format(bearer_token)}
#     search_url += username
#     # -------------------------------------------- #


#     # Sending the request and recieving an endpoint json response
#     response = requests.request("GET", search_url, headers = headers)
#     endpoint_response = response.json()
#     # ----------------------    --------------------------------------
#     if DEBUG_MODE:
#         print(endpoint_response)

#     # Set the user_id and set a search_url for that id's tweets
#     try:
#         user_id = response.json()["data"]["id"]
#         if DEBUG_MODE:
#             print(user_id)
#     except:
#         print("Handle does not exist")
#         return None

#     search_url = "https://api.twitter.com/2/users/{}/tweets".format(user_id)

#     #Setting the timedelta
#     # Crate a date/time object that is acceptable by twitter API to use start_time
#     now = datetime.datetime.now()
#     d = datetime.timedelta(days = daylimit)
#     a = now - d
#     a = str(a).replace(" ","T")
#     match = re.findall(pattern="\.\d+",string=a)[0]
#     a = a.replace(match,"") + "Z"
#     # --------------------------------------------------------------------------- #
#     if DEBUG_MODE:
#         print(a)


#     returned = 0
#     # Query for the twitter API request
#     query_params = {
#                     'max_results': '10',
#                     'tweet.fields': 'text,created_at,id,lang,entities',
#                     'expansions': 'author_id',
#                     'user.fields': 'id,name,username,entities,url',
#                     'start_time':f'{a}',
#                     }
#     # --------------------------------- #

#     # Send the request using search_url, parameters and headers set above and recieve a json response from endpoint.
#     response = requests.request("GET", search_url,params=query_params, headers = headers)
#     endpoint_response = response.json()
#     # --------------------------------------------------------------------
#     if DEBUG_MODE:
#         print(endpoint_response)
#         with open('endpoint_response.json','w') as fh:
#             fh.write(json.dumps(endpoint_response,indent=2))

#         print("Waiting for input before processing endpoint_response")
#         input()
#     # --------------------------------------------------------------------   
#     if 'meta' in endpoint_response:
#         if 'result_count' in endpoint_response['meta']:
#             if endpoint_response['meta']['result_count'] == 0:
#                 print('No tweet returned from this handle.')
#                 return []
#     for tweet in endpoint_response['data']:

#         processed_tweet = {
#             'username': '{}'.format(username),
#             'created_at': '{}'.format(tweet['created_at']),
#             'text': '{}'.format(tweet['text']),
#             'lang': '{}'.format(tweet['lang']),
#             'author_url': '{}'.format("https://twitter.com/"+username),
#             'urls': [],
#             'author_id': user_id,
#             'tweet_id': tweet['id']


#         }


#         #Author_webiste_url
#         if 'entities' in endpoint_response['includes']['users'][0]:
#             if 'url' in endpoint_response['includes']['users'][0]['entities']:
#                 processed_tweet['author_website_url'] = endpoint_response['includes']['users'][0]['entities']['url']['urls'][0]['expanded_url']
#             else:
#                 processed_tweet['author_website_url'] = None
#         else:
#             processed_tweet['author_website_url'] = None

#         if DEBUG_MODE:
#             print('author webiste url ==> ',processed_tweet['author_website_url'])

#         #Entities (urls)
#         final_urls = []
#         if 'entities' in tweet:
#             for key in tweet['entities']:

#                 if key != 'urls':
#                     continue
#                 else:
#                     for url in tweet['entities']['urls']:
#                         if 'twitter.com' not in url['expanded_url']:
#                             # Try to get actual_url from shoretened_url

#                             try:
#                                 shortened_url = url['expanded_url']

#                                 print("Gathering actual url from shortened url...")
#                                 time.sleep(0.1)
#                                 r = requests.get(shortened_url, headers={"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"})
#                                 actual_url = r.url

#                                 print(shortened_url[0:25]+"..."," >>> ", actual_url[0:25]+"...","\n")
#                                 final_urls.append(actual_url)
#                             # -----------------------------------------


#                             # If cant, use another method, if that fails too return the shoretened url
#                             except:
#                                 try:
#                                     time.sleep(0.1)
#                                     actual_url = requests.get(shortened_url).url


#                                     print(shortened_url[0:25]+"..."," >>> ", actual_url[0:25]+"...","\n")
#                                     final_urls.append(actual_url)
#                                 except:
#                                     print("Couldn't convert:", str(url), " skipping..\n")
#                                     final_urls.append(url)
#                             # ----------------------------------
    
#         # Blacklist and whitelist !!
#         for link in final_urls[:]:

#             skip_url_w = False
#             skip_url_b = False

#             for item in blacklist:
#                 if item in link:
#                     skip_url_b = True
#                     break 

#             for item in whitelist:
#                 if item not in link:
#                     skip_url_w = True
#                     break

#             if skip_url_b or skip_url_w:
#                 final_urls.remove(link)
        
#         if final_urls != []:
#             processed_tweet['urls'] = final_urls
#             all_keywords_found = True
            
#             for keyword in keywords:
#                 if keyword in processed_tweet['text']:
#                     continue
#                 else:
#                     all_keywords_found = False
#                     break
#             if all_keywords_found:
#                 final_data.append(processed_tweet)
#                 returned += 1

#     if 'meta' in endpoint_response:
#         if DEBUG_MODE:
#             print('\nFound META!\n')
#         if 'next_token' in endpoint_response['meta']:
#             if DEBUG_MODE:
#                 print('\nFound next_token!\n')
#             next_token = endpoint_response['meta']['next_token']
#             token_found = True
#         else:
#             token_found = False
#     else:
#         token_found= False

#     print('Processed first page got {} tweet'.format(returned))



#     while token_found:
#         if limit != -10:
#             if returned >= limit:
#                     token_found = False
#                     break

#         found_this_step = 0
#         #Setting the timedelta
#         # Crate a date/time object that is acceptable by twitter API to use start_time
#         now = datetime.datetime.now()
#         d = datetime.timedelta(days = daylimit)
#         a = now - d
#         a = str(a).replace(" ","T")
#         match = re.findall(pattern="\.\d+",string=a)[0]
#         a = a.replace(match,"") + "Z"
#         # --------------------------------------------------------------------------- #
#         if DEBUG_MODE:
#             print(a)



#         # Query for the twitter API request
#         query_params = {
#                         'max_results': '10',
#                         'tweet.fields': 'text,created_at,id,lang,entities',
#                         'expansions': 'author_id',
#                         'user.fields': 'id,name,username,entities,url',
#                         'start_time':f'{a}',
#                         'pagination_token': next_token
#                         }
#         # --------------------------------- #

#         # Send the request using search_url, parameters and headers set above and recieve a json response from endpoint.
#         response = requests.request("GET", search_url,params=query_params, headers = headers)

#         endpoint_response = response.json()
#         if 'data' not in endpoint_response:
#             print("No data in next page")
#             token_found = False
#             break
#         # --------------------------------------------------------------------
#         if DEBUG_MODE:
#             print(endpoint_response)
#             with open('endpoint_response.json','w') as fh:
#                 fh.write(json.dumps(endpoint_response,indent=2))

#             print("Waiting for input before processing endpoint_response")
#             input()
#         # --------------------------------------------------------------------        
#         for tweet in endpoint_response['data']:

#             print(f"\nendpoint_response['data']= {endpoint_response['data']}\n")

#             processed_tweet = {
#                 'username': '{}'.format(username),
#                 'created_at': '{}'.format(tweet['created_at']),
#                 'text': '{}'.format(tweet['text']),
#                 'lang': '{}'.format(tweet['lang']),
#                 'author_url': '{}'.format("https://twitter.com/"+username),
#                 'entities': {'urls':[]},
#                 'author_id': user_id,
#                 'tweet_id': tweet['id'],
#                 'tweet_url': tweet['tweet_url'],

#             }


#             #Author_webiste_url
#             if 'entities' in endpoint_response['includes']['users'][0]:
#                 if 'url' in endpoint_response['includes']['users'][0]['entities']:
#                     processed_tweet['author_website_url'] = endpoint_response['includes']['users'][0]['entities']['url']['urls'][0]['expanded_url']
#                 else:
#                     processed_tweet['author_website_url'] = None
#             else:
#                 processed_tweet['author_website_url'] = None

#             if DEBUG_MODE:
#                 print('author webiste url ==> ',processed_tweet['author_website_url'])

#             #Entities (urls)
#             final_urls = []
#             if 'entities' in tweet:
#                 for key in tweet['entities']:

#                     if key != 'urls':
#                         continue
#                     else:
#                         for url in tweet['entities']['urls']:
#                             if 'twitter.com' not in url['expanded_url']:

#                                 # Try to get actual_url from shoretened_url

#                                 try:
#                                     shortened_url = url['expanded_url']

#                                     print("Gathering actual url from shortened url...")
#                                     time.sleep(0.1)
#                                     r = requests.get(shortened_url, headers={"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"})
#                                     actual_url = r.url

#                                     print(shortened_url[0:25]+"..."," >>> ", actual_url[0:25]+"...","\n")
                                    
#                                     final_urls.append(actual_url)
#                                 # -----------------------------------------


#                                 # If cant, use another method, if that fails too return the shoretened url
#                                 except:
#                                     try:
#                                         time.sleep(0.1)
#                                         actual_url = requests.get(shortened_url).url


#                                         print(shortened_url[0:25]+"..."," >>> ", actual_url[0:25]+"...","\n")
#                                         final_urls.append(actual_url)
#                                     except:
#                                         print("Couldn't convert:", str(url), " skipping..\n")
#                                         final_urls.append(url)
#                                 # ----------------------------------
#             # Blacklist and whitelist !!
#             for link in final_urls[:]:

#                 skip_url_w = False
#                 skip_url_b = False

#                 for item in blacklist:
#                     if item in link:
#                         skip_url_b = True
#                         break

#                 for item in whitelist:
#                     if item not in link:
#                         skip_url_w = True
#                         break

#                 if skip_url_b or skip_url_w:
#                     final_urls.remove(link)
            
#             if final_urls != []:
#                 processed_tweet['entities']['urls'] = final_urls
#                 all_keywords_found = True
#                 """
#                 for keyword in keywords:
#                     if keyword in processed_tweet['text']:
#                         continue
#                     else:
#                         all_keywords_found = False
#                         break
#                 """
#                 if all_keywords_found:
#                     final_data.append(processed_tweet)
#                     found_this_step += 1

#         returned += found_this_step

#         if 'meta' in endpoint_response:
#             if DEBUG_MODE:
#                 print('\nFound META!\n')
#             if 'next_token' in endpoint_response['meta'] and 'data' in endpoint_response:
#                 if DEBUG_MODE:
#                     print('\nFound more data with next_token!\n')
#                 next_token = endpoint_response['meta']['next_token']
#                 token_found = True
#             else:
#                 token_found = False



#     # --------------------------------------------------------------------
#     if DEBUG_MODE:
#         print(final_data)
#         with open('endpoint_response.json','w') as fh:
#             fh.write(json.dumps(final_data,indent=2))
#     # --------------------------------------------------------------------

#     return final_data
## (end search_specific_handle)































# def search_handle_recent(username,daylimit=7,keywords=[],blacklist=[],whitelist=[]):
#     DEBUG_MODE = False
#     # Warn the user if the keyword argument is not a list
#     if type(keywords) != list:
#         return "Function's keyword argument must be a list."
#     # -------------------------------------------------- #

#     # Check if handle includes '@' if it does, remove it
#     if username.startswith('@'):
#         username = username.replace('@','')
#     # ------------------------------------------------ #

#     # Endpoint to use
#     search_url = "https://api.twitter.com/2/tweets/search/recent" 


#     # Header to send bearer token to twitter API
#     headers = {"Authorization": "Bearer {}".format(bearer_token)}


#     # Create a string keyword query with the provided keyword list from function.
    
#     if keywords != []:
#         query = ""


#         add_after = []
#         for keyword in keywords:
#             if ' ' in keyword:
#                 add_after.append(keyword)
#             else:
#                 last_keywords = []
#                 last_keywords.append(keyword.capitalize())
#                 last_keywords.append(keyword)
#                 last_keywords.append(keyword.lower())
#                 temp_keys = []
#                 for kw in last_keywords:
#                     if kw not in temp_keys:
#                         temp_keys.append(kw)

#                 keywords = temp_keys

#                 for keyword in keywords:
#                     if keyword == keywords[0]: query += '('
#                     if keyword != keywords[-1]:
#                         query += keyword+" OR "
#                     else:
#                         query += keyword+') '
                

#         # query.strip()
#         query = query.strip()
#         if len(add_after) > 0:
#             for kw in add_after:
#                 query += '"'+kw+'" '


#     else:
#         query = ""

#     print(f"Query: {query}")
#     # ------------------------------------------------------------------- #

    

#     # Crate a date/time object that is acceptable by twitter API to use start_time
#     now = datetime.datetime.now()
#     d = datetime.timedelta(days = daylimit)
#     a = now - d
#     a = str(a).replace(" ","T")
#     match = re.findall(pattern="\.\d+",string=a)[0]
#     a = a.replace(match,"") + "Z"
#     # --------------------------------------------------------------------------- #

 
        
#     # Query for the twitter API request
#     query_params = {'query': f'{query}has:links (from:{username}) -is:retweet -is:reply',
#                     'max_results': '{}'.format(10),
#                     'tweet.fields': 'text,created_at,id,lang,entities',
#                     'expansions': 'author_id',
#                     'user.fields': 'id,name,username,entities,url',
#                     'start_time':f'{a}',
#                     }
#     # --------------------------------- #

#     if DEBUG_MODE: 
#         print(f'\n\nQuery Params: {query_params}\n\n')
#         input()

#     # Send the request using search_url, parameters and headers set above and recieve a json response from endpoint.
#     response = requests.request("GET", search_url,params=query_params, headers = headers)

#     endpoint_response = response.json()
#     # --------------------------------------------------------------------

#     if DEBUG_MODE: 
#         print('\n\nEndpoint Response: ',endpoint_response,'\n')
#         input()

#     # FINAL DATA TO RETURN
#     final_data = []
#     # -------------------#



#     # Warn if no tweet is found in 7 days or endpoint returns an error by printing the error.
#     try:
#         if endpoint_response['meta']['result_count'] == 0:
#             print('No matched tweet found in 7 days.')
#             return None
#     except:
#         print("\n\n\n Endpoint Response Error Check Log: \n",endpoint_response)
#         return None
#     # --------------------------------------------------------------------------------------#


#     # For each individual tweet in the endpoint response, create a tweet_data list to store the data and get the data from endpoint response
#     for tweet in endpoint_response["data"]:

#         tweet_data = {
#             "entities":{"urls":None}

#         }


#         # Get every 'expanded_url' except if there is twitter.com in link
#         tweet_data["entities"]["urls"] = [gag["expanded_url"] for gag in tweet["entities"]["urls"] if "twitter.com" not in gag["expanded_url"]]
#         # ------------------------------------------------------------- #



#         #Try to gather author_website_url of the author, if not available, append []
#         try:
#             tweet_data['author_website_url'] = endpoint_response['includes']['users'][0]['entities']['url']['urls'][0]['expanded_url']
#         except:
#             tweet_data['author_website_url'] = None
#         # ------------------------------------------------------------------------ #

#         # Set the author_url using the handle
#         tweet_data["author_url"] = "https://twitter.com/"+username
#         # ----------------------------------#


#         # Final urls to store
#         final_urls = []

#         # For every url stored in tweet_data
#         for link in tweet_data["entities"]["urls"]:

#                         # Try to get actual_url from shoretened_url
#                         try:
#                             shortened_url = link

#                             print("Gathering actual url from shortened url...")
#                             time.sleep(0.1)
#                             r = requests.get(shortened_url, headers={"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"})
#                             actual_url = r.url

#                             print(shortened_url[0:25]+"..."," >>> ", actual_url[0:25]+"...","\n")
#                             final_urls.append(actual_url)
#                         # -----------------------------------------


#                         # If cant, use another method, if that fails too return the shoretened url
#                         except:
#                             try:
#                                 time.sleep(0.1)
#                                 actual_url = requests.get(shortened_url).url


#                                 print(shortened_url[0:25]+"..."," >>> ", actual_url[0:25]+"...","\n")
#                                 final_urls.append(actual_url)
#                             except:
#                                 print("Couldn't convert:", str(link), " skipping..\n")
#                                 final_urls.append(link)
#                         # ----------------------------------
#         # Blacklist and whitelist !!
#         for link in final_urls[:]:

#             skip_url_w = False
#             skip_url_b = False

#             for item in blacklist:
#                 if item in link:
#                     skip_url_b = True
#                     break

#             for item in whitelist:
#                 if item not in link:
#                     skip_url_w = True
#                     break

#             if skip_url_b or skip_url_w:
#                 final_urls.remove(link)

#         # Set all of the tweet_data values before exiting from the tweet
#         tweet_data["entities"]["urls"] = final_urls
#         tweet_data["username"] = username 
#         tweet_data["author_id"] = tweet["author_id"]
#         tweet_data["created_at"] = tweet["created_at"]
#         tweet_data["text"] = tweet["text"]
#         tweet_data["lang"] = tweet["lang"]
#         tweet_data["tweet_id"] = tweet["id"]
#         tweet_data["tweet_url"] = "https://twitter.com/"+username+"/status/"+tweet_data["tweet_id"]
#         # -------------------------------------------------------------#

#         # Exit the individual tweet
#         final_data.append(tweet_data)   
#         # ------------------------ #




#     # Final lookthrough of tweets before returning the final_data


#     # Remove the tweet if there is no url left
#     for tweet in final_data[:]:
#         if len(tweet["entities"]["urls"]) == 0 or tweet["entities"]["urls"] == []:
#             final_data.remove(tweet)

#     # Remove the url from the tweet if it includes youtube.com
#     for tweet in final_data:
#         for url in tweet["entities"]["urls"][:]:
#             if "youtube.com" in url:
#                 tweet["entities"]["urls"].remove(url)

#     # Last check if there is any no url tweet left
#     for tweet in final_data[:]:
#         if len(tweet["entities"]["urls"]) == 0:
#             final_data.remove(tweet)
    

#     # Return
#     return final_data


def generic_search(daylimit=7,keywords=[],blacklist=[],whitelist=[],limit=100,continue_from_cache=False):
    #Just in case anything bad happens :D
    DEBUG_MODE = False

    print(f"\n{keywords=}\n")

    #Final return of generic_search
    final_data = []


    # # If you already have the response and want to continue from where you've left off
    # #Loads already processed tweets that might have been lost because of some error
    # if os.path.exists('twittee_processed.json'):
    #     if continue_from_cache:
    #         final_data.extend(json.loads('['+open('twittee_processed.json','r').read().replace('}{','},{')+']'))
    #         print('Successfully restored {} tweets from cache!'.format(len(final_data)))
    #         time.sleep(1)
    #     else:
    #         answer = input("Noticed the file 'twittee_processed.json' Would you like to continue_from_cache instead? (Y/N)\n Old cache file(s) will be deleted if you type 'N'")
    #         if answer.startswith('y') or answer.startswith('Y'):
    #             return generic_search(daylimit,keywords,blacklist,whitelist,limit,continue_from_cache=True)
    #         elif answer.startswith('n') or answer.startswith('N'):
    #             if os.path.exists('twittee_cached.json'): os.remove('twittee_cached.json')
    #             if os.path.exists('twittee_processed.json'): os.remove('twittee_processed.json')
    #             if os.path.exists('processed_cache_file.txt'): os.remove('processed_cache_file.txt')
    # else:

    #     if continue_from_cache:
    #         print("Parameter continue_from_cache = True but couldn't find file 'twittee_processed.json' please check ")
    #         return

    # If continue_from_cache = False, run generic_search normally
    if not continue_from_cache:
        
        #Keyword list error
        if type(keywords) != list:
            return "Function's keyword argument must be a list."

        if limit != 0:
            limit -= 100

        returned = 0
        # Endpoint to use
        search_url = "https://api.twitter.com/2/tweets/search/recent" 



        # Header to send bearer token to twitter API
        headers = {"Authorization": "Bearer {}".format(bearer_token)}


        # Create a string keyword query with the provided *args to function.
        query = ""

        # Cool keyword function?
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
                query += ' "'+kw+'" '


        query = query.strip()
        print(f"\nQuery: {query}\n")
        # --------------------------------------------------------------------


        # Crate a date/time object that is acceptable by twitter API to use start_time
        now = datetime.datetime.now()
        d = datetime.timedelta(days = daylimit)
        a = now - d
        a = str(a).replace(" ","T")
        match = re.findall(pattern="\.\d+",string=a)[0]
        a = a.replace(match,"") + "Z"
        # --------------------------------------------------------------------------- #


        # Query for the twitter API request
        query_params = {'query': f'{query}has:links -is:retweet -is:reply',
        # query_params = {'query': '{query} has:links -is:retweet'.format(query),
                        'max_results': '{}'.format(100),
                        'expansions': 'author_id',
                        'tweet.fields': 'text,entities,created_at,id,lang',
                        'user.fields': 'id,name,username,url,entities',
                        'start_time': f'{a}'
                        }
        # ---------------------------------
        
        if DEBUG_MODE:
            print(query_params)
            input()


        # Send the request using search_url, parameters and headers set above.
        response = requests.request("GET", search_url,params=query_params, headers = headers)

        endpoint_response = response.json()
        # --------------------------------------------------------------------
        if DEBUG_MODE:
            pprint(endpoint_response)
            with open('yaman.txt','w') as fh:
                json.dump(endpoint_response,fh)
            input()

        #Error if connection could not be established with the endpoint.
        if response.status_code != 200:
            print("\n\nConnection to endpoint was NOT sucessfull..\n")
            raise Exception(response.status_code, response.text)
        # --------------------------------------------------------------




        # This will be the final list of tweet datas
        tweet_data = []
        # *-*-*-*-*-*-*-*-*-*-*-*-*-*-*-**-*-**-*-*-



        # Check the length of the response tweets
        if len(endpoint_response) == 0:

            print("No data found with given keywords...")
            return None
        
        # Proceed if not 0 :)
        else:


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
                token_found = False

            if DEBUG_MODE:
                print('Endpoint data length: ',len(endpoint_response['data']))

            for i in range(0,len(endpoint_response['data'])):
                
                # Gather all info in this dictionary
                data_of_tweet = {}



                # Get text, entities, created_at, urls and author_id for data_of_tweet from endpoint_response
                data_of_tweet["created_at"] = (endpoint_response["data"][i]["created_at"])
                data_of_tweet["text"] = endpoint_response["data"][i]["text"]
                data_of_tweet["entities"] = {}
                data_of_tweet["entities"]["urls"] = []
                data_of_tweet["author_id"] = endpoint_response["data"][i]["author_id"]
                # ---------------------------------------------------------------------------


                # Filter url's based on list_blacklist and hardcode-remove some urls
                for url in endpoint_response["data"][i]["entities"]["urls"]:

                    if not url["expanded_url"].startswith("https://twitter.com") and 'facebook.com' not in url and 'linkedin.com' not in url:
                        domain = url["expanded_url"].split("//")[1].split("/")[0]
                        if domain not in list_blacklist:
                            data_of_tweet["entities"]["urls"].append(url["expanded_url"])
                # ------------------------------------------------------------------
        

                users = endpoint_response["includes"]["users"]

                #Match user in users with the author of the tweet to gather author info

                for user in users:


                    if data_of_tweet["author_id"] == user["id"]:

                        #Try to gather author_website_url of the author, if not available, append []
                        try:
                            data_of_tweet['author_website_url'] = user['entities']['url']['urls'][0]['expanded_url']

                        except:
                            data_of_tweet['author_website_url'] = None


                        # ---------------------------------------------------------------------------

                        # Set name, username, user_url from endpoint_response to data_of_tweet
                        data_of_tweet["name"] = user["name"]
                        data_of_tweet["username"] = user["username"]
                        data_of_tweet["user_url"] = "https://twitter.com/" + user["username"]

                # --------------------------------------------------------------------------

                # Set tweet_id and tweet_url
                data_of_tweet["tweet_id"] = endpoint_response["data"][i]["id"]
                data_of_tweet["tweet_url"] = "https://twitter.com/"+data_of_tweet["username"]+"/status/"+data_of_tweet["tweet_id"]
                # ---------------------------------------------------------------------------------------------------------------

                # Getting the tweet language from endpoint_response
                data_of_tweet["lang"] = endpoint_response["data"][i]["lang"]
                # ---------------------------------------------------------

                #Only append this tweet to tweet_data if it has any url.
                if len(data_of_tweet["entities"]["urls"]) > 0:
                    tweet_data.append(data_of_tweet)
                    returned += 1
                # ------------------------------------------------------


                

        print('Got {} tweet from first request'.format(returned))
        
        #Check if more pages are available
        while token_found:
            time.sleep(2.2)
            if limit != -100:
                if returned >= limit:
                        token_found = False
                        break

            found_this_step = 0

            # Query for the twitter API request
            query_params = {
                        'query': '{} has:links -is:retweet'.format(query),
                        'max_results': '{}'.format(100),
                        'expansions': 'author_id',
                        'tweet.fields': 'text,entities,created_at,id,lang',
                        'user.fields': 'id,name,username,url,entities',
                        'start_time': f'{a}',
                        'next_token': next_token
                        }
            # ---------------------------------


            # Send the request using search_url, parameters and headers set above.
            response = requests.request("GET", search_url,params=query_params, headers = headers)

            endpoint_response = response.json()
            # --------------------------------------------------------------------


            #Error if connection could not be established with the endpoint.
            if response.status_code != 200:
                print("\n\nConnection to endpoint was NOT sucessfull..\n")
                raise Exception(response.status_code, response.text)
            # --------------------------------------------------------------




            
            # Proceed if not 0 :)



            i = 0
            for i in range(0,len(endpoint_response['data'])):
                    
                    data_of_tweet = {}

                    # Get text, entities, created_at, urls and author_id for data_of_tweet from endpoint_response
                    data_of_tweet["created_at"] = (endpoint_response["data"][i]["created_at"])
                    data_of_tweet["text"] = endpoint_response["data"][i]["text"]
                    data_of_tweet["entities"] = {}
                    data_of_tweet["entities"]["urls"] = []
                    data_of_tweet["author_id"] = endpoint_response["data"][i]["author_id"]
                    # ---------------------------------------------------------------------------
                    


                    # Filter url's based on list_blacklist and hardcode-remove some urls
                    for url in endpoint_response["data"][i]["entities"]["urls"]:

                        if not url["expanded_url"].startswith("https://twitter.com") and url != 'facebook.com' and url != 'linkedin.com':
                            domain = url["expanded_url"].split("//")[1].split("/")[0]
                            if domain not in list_blacklist:
                                data_of_tweet["entities"]["urls"].append(url["expanded_url"])
                    # ------------------------------------------------------------------
                



                    users = endpoint_response["includes"]["users"]

                    #Match user in users with the author of the tweet to gather author info

                    for user in users:


                        if data_of_tweet["author_id"] == user["id"]:

                            #Try to gather author_website_url of the author, if not available, append []
                            try:
                                data_of_tweet['author_website_url'] = user['entities']['url']['urls'][0]['expanded_url']

                            except:
                                data_of_tweet['author_website_url'] = None


                            # ---------------------------------------------------------------------------

                            # Set name, username, user_url from endpoint_response to data_of_tweet
                            data_of_tweet["name"] = user["name"]
                            data_of_tweet["username"] = user["username"]
                            data_of_tweet["user_url"] = "https://twitter.com/" + user["username"]

                    # --------------------------------------------------------------------------

                    # Set tweet_id and tweet_url
                    data_of_tweet["tweet_id"] = endpoint_response["data"][i]["id"]
                    data_of_tweet["tweet_url"] = "https://twitter.com/"+data_of_tweet["username"]+"/status/"+data_of_tweet["tweet_id"]
                    # ---------------------------------------------------------------------------------------------------------------

                    # Getting the tweet language from endpoint_response
                    data_of_tweet["lang"] = endpoint_response["data"][i]["lang"]
                    # ---------------------------------------------------------

                    #Only append this tweet to tweet_data if it has any url.
                    if len(data_of_tweet["entities"]["urls"]) > 0:
                        tweet_data.append(data_of_tweet)
                        found_this_step += 1
                    # ------------------------------------------------------

            if 'meta' in endpoint_response:
                            if DEBUG_MODE:
                                print('\nFound META!\n')
                            if 'next_token' in endpoint_response['meta']:
                                if DEBUG_MODE:
                                    print('\nFound next_token!\n')
                                next_token = endpoint_response['meta']['next_token']
                                token_found = True
                            else:
                                token_found= False
            else:
                        token_found = False
            
            returned += found_this_step
            if DEBUG_MODE:
                print('Processing ->', end=' ')
                print(next_token,' New tweet data length :: ', len(tweet_data))
            else:
                print('Current data length : ', len(tweet_data))
        
        #Save the response just in case you want to continue from where you've left off
        cached_file = open('twittee_cached.json','w')
        json.dump(tweet_data,cached_file)
        cached_file.close()

    # Shortened_url to actual_url transformer:

    #First, restore the already processed tweets
    if continue_from_cache:
        try:
            cached_file = open('twittee_cached.json','r')
            tweet_data = json.load(cached_file)
            print('Successfully returned response of length: {} from cache.'.format(len(tweet_data)))
            cached_file.close()
        except:
            print("Couldn't load twittee_cached.json, make sure file exists or continue_from_cache == False ")
            return
        processed_cache_file = open('processed_cache_file.txt','r')
        already_processed_temp = processed_cache_file.readlines()
        already_processed = [id.strip() for id in already_processed_temp]
        processed_cache_file.close()
    

    #Continue processing tweet data list normally
    index = 1
    num_of_tw = len(tweet_data)
    for tweet in tweet_data[:]:
                # But skip if tweet is already processed
                if continue_from_cache:
                    if tweet['tweet_id'] in already_processed:
                        num_of_tw -= 1
                        continue
                    
                print(f"Tweet: {index}/{num_of_tw}")
                index2 = 0
                for url in tweet["entities"]["urls"][:]:
                        index2 += 1
                        print(f"Url #{index2}",end=" ")
                        # final_urls list of the specific tweet
                        final_urls = []


                        # Try to convert shortened_url to actual_url
                        try:

                            shortened_url = url
                            print("Gathering actual url from shortened url...")
                            req = http.request('GET', url, fields=payload)

                            actual_url = req.geturl()
                            #r = requests.get(shortened_url, timeout=15, headers={"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"})
                            #actual_url = r.url

                            print(shortened_url[0:25]+"..."," >>> " ,actual_url[0:25]+"...","\n")
                            
                            final_urls.append(actual_url)
                            if DEBUG_MODE:
                                if 'zoom' in actual_url:
                                    with open('yaman.txt','a') as df: df.write(actual_url+'\n')
                        #-------------------------------------------

                        # If cant convert, append the normal url 
                        except:

                            print("Couldn't convert:", url, " skipping..\n")
                            final_urls.append(url)

                        # ---------------------------------------

                # Blacklist and whitelist implementation
                for link in final_urls[:]:

                    skip_url_w = False
                    skip_url_b = False
                        
                    for item in blacklist:
                        if item in url:
                            skip_url_b = True
                            break

                    for item in whitelist:
                        if item not in url:
                            skip_url_w = True
                            break

                    if skip_url_b or skip_url_w:
                        final_urls.remove(link)
                # -------------------------------------- #


                tweet["entities"]["urls"] = final_urls
                index += 1
                
                for url in tweet["entities"]["urls"][:]:
                        if "youtube.com" in url:
                            tweet["entities"]["urls"].remove(url)
                
                if len(tweet["entities"]["urls"]) != 0:
                    print('Writing tweet to cache...')
                    write_data_file = open('twittee_processed.json','a')
                    json.dump(tweet,write_data_file)
                    final_data.append(tweet)
                processed_cache_file = open('processed_cache_file.txt','a')
                processed_cache_file.write(tweet['tweet_id']+'\n')
                processed_cache_file.close()

        
                # Final lookthrough of tweets before returning the final_data

    
    return final_data
        # End of generic_search()




def check_loc(handle):

    query_params = {
                    'user.fields': 'id,name,location'
                    }

    search_url = "https://api.twitter.com/2/users/by/username/"
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    search_url += handle
    # ---------------------------------------------


    # Sending the request and recieving an endpoint json response
    response = requests.request("GET", search_url, headers = headers, params=query_params)
    endpoint_response = response.json()
    try:
        final_val = endpoint_response["data"]["location"]
        
    except:
        final_val = None

    if final_val != None:
        words = final_val.split(",")

        for word in words:

            word = word.split()

            try:
                geolocator = Nominatim(user_agent='myapplication')
                location = geolocator.geocode(word)
                loc_data = (location.raw["display_name"])
                infos = loc_data.split(",")

                final_val = infos[-1]
            except:
                final_val = None
                continue


            if final_val != None:
                return final_val



    

    return None

    # ------------------------------------------------------------

def check_handle(handle):

    #Setting variables for search_specific_handle()

    search_url = "https://api.twitter.com/2/users/by/username/"
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    search_url += handle
    # ---------------------------------------------


    # Sending the request and recieving an endpoint json response
    response = requests.request("GET", search_url, headers = headers)
    endpoint_response = response.json()

    # ------------------------------------------------------------


    # Set the user_id and set a search_url for that id's tweets
    try:
        user_id = response.json()["data"]["id"]
    except:
        error_list.append(handle)
        return False

    search_url = "https://api.twitter.com/2/users/{}/tweets".format(user_id)


    # --------------------------------------------------------------------------


    # Set query
    query_params = {
                    'user.fields': 'id,name,username,entities,url'
                    }

    # Send the request to recieve the tweets of that id


    response = requests.request("GET", search_url, headers = headers,params=query_params)
    endpoint_response = response.json()
    # --------------------------------------------------

    # Get author_website_url here since it is only 1 user
    try:
        user = endpoint_response["includes"]["users"][0]
    except:
        error_list.append(handle)
        return False

    return True


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
    
    keywords = [
        'symposium',
    ]

    tweet_data = generic_search(daylimit=7,keywords=keywords,blacklist=[],whitelist=[],limit=100,continue_from_cache=False)
    print(f"\nGeneric search finished with keywords '{keywords}':\n")
    pp.pprint(tweet_data)
    
    print('-------------------------------')
    run_time = round((time.time() - start_time), 1)
    if run_time > 60:
        print(f'{os.path.basename(__file__)} finished in {run_time/60} minutes.')
    else:
        print(f'{os.path.basename(__file__)} finished in {run_time}s.')
    print()