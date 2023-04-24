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
# from pprint import pprint
import pprint
pp = pprint.PrettyPrinter(indent=4)

from urllib.parse import urlparse

from dotenv import load_dotenv
load_dotenv()
PROJECTS_FOLDER = os.getenv("PROJECTS_FOLDER")

import sys
sys.path.append(f"{PROJECTS_FOLDER}/indeXee")

import my_utils

import csv
import re

from dotenv import load_dotenv
load_dotenv()
bearer_token = os.getenv("TOKEN")

# print(f"\n{bearer_token=}\n")

list_blacklist = []
error_list = []

# try:
#     with open('/Users/nicolas/Python/indeXee/data/blacklist_domain.csv', 'r', newline='', encoding='UTF-8') as h:
#         reader = csv.reader(h, delimiter=",")
#         data = list(reader)
#         for row in data:
#             list_blacklist.append(row[0])
# except:
#     pass

#############################

def generic_search(daylimit=7,keywords=[],blacklist=[],whitelist=[],limit=100,continue_from_cache=False):
    #Just in case anything bad happens :D
    verbose = False

    if verbose:
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
        if verbose:
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
        
        if verbose:
            print(query_params)
            # input()


        # Send the request using search_url, parameters and headers set above.
        response = requests.request("GET", search_url,params=query_params, headers = headers)

        endpoint_response = response.json()
        # --------------------------------------------------------------------
        # if verbose:
        #     pp.pprint(endpoint_response)

            # with open('yaman.txt','w') as fh:
            #     json.dump(endpoint_response,fh)

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
                if verbose:
                    print('\nFound META!\n')
                if 'next_token' in endpoint_response['meta']:
                    if verbose:
                        print('\nFound next_token!\n')
                    next_token = endpoint_response['meta']['next_token']
                    token_found = True
                else:
                    token_found = False
            else:
                token_found = False

            if 'data' in endpoint_response:

                if verbose:
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
                                if verbose:
                                    print('\nFound META!\n')
                                if 'next_token' in endpoint_response['meta']:
                                    if verbose:
                                        print('\nFound next_token!\n')
                                    next_token = endpoint_response['meta']['next_token']
                                    token_found = True
                                else:
                                    token_found= False
                else:
                            token_found = False
                
                returned += found_this_step
                if verbose:
                    print('Processing ->', end=' ')
                    print(next_token,' New tweet data length :: ', len(tweet_data))
                else:
                    print('Current data length : ', len(tweet_data))
            
            # #Save the response just in case you want to continue from where you've left off
            # cached_file = open('twittee_cached.json','w')
            # json.dump(tweet_data,cached_file)
            # cached_file.close()

        # Shortened_url to actual_url transformer:

        # #First, restore the already processed tweets
        # if continue_from_cache:
        #     try:
        #         cached_file = open('twittee_cached.json','r')
        #         tweet_data = json.load(cached_file)
        #         print('Successfully returned response of length: {} from cache.'.format(len(tweet_data)))
        #         cached_file.close()
        #     except:
        #         print("Couldn't load twittee_cached.json, make sure file exists or continue_from_cache == False ")
        #         return
        #     processed_cache_file = open('processed_cache_file.txt','r')
        #     already_processed_temp = processed_cache_file.readlines()
        #     already_processed = [id.strip() for id in already_processed_temp]
        #     processed_cache_file.close()
        

        #Continue processing tweet data list normally
        index = 1

        num_of_tw = len(tweet_data)

        converted_urls = {}
        
        print(f"\nUnfurling bit.ly URLs...")
        for tweet in tweet_data[:]:

            # # But skip if tweet is already processed
            # if continue_from_cache:
            #     if tweet['tweet_id'] in already_processed:
            #         num_of_tw -= 1
            #         continue
                
            # print(f"Tweet: {index}/{num_of_tw}") # moved below


            # URL CLEANING
            # index2 = 0

            for url in tweet["entities"]["urls"][:]:
                # index2 += 1

                # final_urls list of the specific tweet
                final_urls = []

                if 'bit.ly' in url:

                    if url not in converted_urls:

                        # Try to convert shortened_url to actual_url
                        try:

                            shortened_url = url
                            print(f"Gathering actual url from shortened url... Tweet: {index}/{num_of_tw}", end='\r', flush=True)

                            actual_url = my_utils.expand_bitly_url(shortened_url)

                            # print(shortened_url[0:25]+"..."," >>> " ,actual_url[0:25]+"...","\n")
                            print(f"{actual_url}")
                            
                            final_urls.append(actual_url)

                            converted_urls[shortened_url] = actual_url

                        # If cant convert, append the normal url 
                        except:
                            final_urls.append(url)

                    else:
                        # If already converted, append the converted url
                        final_urls.append(converted_urls[url])

                else:
                    # If not shortened url, append the normal url
                    final_urls.append(url)


            # Blacklist and whitelist implementation
            for link in final_urls[:]:
            # for link in tweet_data[:]:

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
            
            # Remove links / TODO Extract to function
            remove_links = [
                'facebook.com',
                'instagram.com',
                'www.google.com',
                'consent.google.com',
                'www.msn.com',
                'www.ebay.com',
                'accounts.google.com',
                'marketwirenews.com',
                'news.beeken.io',
                'www.businesswire.com',
                'www.baesystems.com',
                'gocon.connpass.com',
                'odysee.com',
                'wtvm.com',
                'domain.com',
                'website.com',
                'sentry.io',
                'businesswire.com',
                'linkedin.com',
                'youtu.be',
                'youtube.com',
            ]
            for url in tweet["entities"]["urls"][:]:
                    if any(ele in url for ele in remove_links):
                        tweet["entities"]["urls"].remove(url)
            
            # CACHING / 230417-2206 removed to test if printing disappears
            if len(tweet["entities"]["urls"]) != 0:
                # print('Writing tweet to cache...')
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

    # import pprint
    # pp = pprint.PrettyPrinter(indent=4)

    # print()
    # print()
    # print('-------------------------------')
    # print(f"{os.path.basename(__file__)}")
    
    # keywords = [
    #     'symposium',
    # ]

    # tweet_data = generic_search(daylimit=7,keywords=keywords,blacklist=[],whitelist=[],limit=100,continue_from_cache=False)
    # print(f"\nGeneric search finished with keywords '{keywords}':\n")
    # pp.pprint(tweet_data)
    
    print('-------------------------------')
    run_time = round((time.time() - start_time), 1)
    if run_time > 60:
        print(f'{os.path.basename(__file__)} finished in {run_time/60} minutes.')
    else:
        print(f'{os.path.basename(__file__)} finished in {run_time}s.')
    print()