import os
import sys
import json
import codecs
import pickle
import tweepy
import random
import socket
from datetime import datetime
import argparse
import telegram
import traceback
from tqdm import tqdm
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Arguments for the data collection software
parser = argparse.ArgumentParser(description='Main file')
parser.add_argument('-f', '--file',
                    required=True,
                    help='The dataset file to use.')
parser.add_argument('-c', '--config',
                    required=True,
                    default='config.json',
                    help='The config file to use.')
parser.add_argument('-t',
                    action='store_true',
                    help='Testing mode.')
parser.add_argument('--lang',
                    action='store_true',
                    help='Use if the language used employs non ascii characters.')
args = parser.parse_args()

# Keys for Tweepy
config_file = json.load(open(args.config, 'r'))

consumer_key = config_file['CONSUMER_KEY']
consumer_secret = config_file['CONSUMER_SECRET']
access_token = config_file['ACCESS_TOKEN']
access_token_secret = config_file['ACCESS_TOKEN_SECRET']
telegram_token = config_file['TELEGRAM_TOKEN']
telegram_chat_id = config_file['TELEGRAM_CHAT_ID']

if args.t:
    N_FAILS = 1
else:
    N_FAILS = 5
SCROLL = 1200
DATA_PATH = './userdata/'

def recover_tweets(driver, api, user, prefix, first_datetime, last_datetime, name=None):
    # Get desired webpage
    
    driver.get('https://twitter.com/search?q=(from%3A'+ user +')%20until%3A'+ last_datetime +'%20since%3A'+ first_datetime +'&src=typed_query&f=live')
    sleep(3)

    print('Gathering tweets from --> %s' % user)

    tweet_ids = []

    fail = 0
    times = 1
    temp_tweets = []
    while(fail < N_FAILS):
        try:
            html = (driver.page_source)
            soup = BeautifulSoup(html, "html.parser")
            tweet_articles = soup.find_all('article')

            for tweet in tweet_articles:
                time = tweet.find("time")
                if time is not None:
                    tweet_ids.append(time.parent['href'].split('/')[-1])

            if len(temp_tweets) == len(set(tweet_ids)):
                fail = fail + 1
            
            temp_tweets = set(tweet_ids)
        
        except:  
            traceback.print_exc()
            driver.close()

        sleep(3)
        driver.execute_script("window.scrollTo(0, " + str(SCROLL * times) + ");var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        times = times + 1

    tweet_ids = list(set(tweet_ids))

    if name is not None:
        with codecs.open(DATA_PATH + prefix + name +'_ids.txt', 'w', encoding='utf-8') as f:
                for item in tweet_ids:
                    f.write("%s\n" % item)
    else:
        print('Saving %i tweets' % len(tweet_ids))
        with codecs.open(DATA_PATH + prefix + user +'_ids.txt', 'w', encoding='utf-8') as f:
                for item in tweet_ids:
                    f.write("%s\n" % item)

    all_tweets = []

    if len(tweet_ids) > 1000:
        tweet_ids = random.sample(tweet_ids, 1000)

    for tw_id in tweet_ids:
        try:
            tweet = api.get_status(tw_id)
        except tweepy.TweepError:
            pass
        all_tweets.append(json.dumps(tweet._json) + ",\n")
    
    write_tweets(user, prefix, all_tweets, name)


def write_tweets(user, prefix, tweets, name=None):
    if name is not None:
        with codecs.open(DATA_PATH + prefix + name +'_tweets.pickle', 'wb') as f:
            pickle.dump(tweets, f)
    else:
        with codecs.open(DATA_PATH + prefix + user +'_tweets.pickle', 'wb') as f:
            pickle.dump(tweets, f)

if __name__ == "__main__":
    # Set Tweepy API
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True)

    # Set Selenium webDriver
    chrome_options = webdriver.ChromeOptions()
    chrome_options.headless = True
    # Fix for chromedriver
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome( options=chrome_options, service_log_path='log.txt')

    with codecs.open(args.file, 'r', encoding='utf-8',) as f:
        lines = f.readlines()
        
        for num, line in enumerate(tqdm(lines)):
            if num == 0:
                first_ts = float(line.split(' ')[0])
                last_ts = float(line.split(' ')[-1])
                first_datetime = datetime.fromtimestamp(first_ts).strftime('%Y-%m-%d')
                last_datetime = datetime.fromtimestamp(last_ts).strftime('%Y-%m-%d')
                print(first_datetime)
                print(last_datetime)
                continue
            name = None
            if args.lang:
                name = 'hashtag_' + str(num + 1)
            user = line.split(' ')[0]
            prefix = args.file.split('_')[0] +'/'

            if not os.path.isdir(DATA_PATH + '/' + prefix):
                os.mkdir(DATA_PATH + '/' + prefix)

            if name:
                recover_tweets(driver, api, user, prefix, first_datetime, last_datetime, name)
            else:
                recover_tweets(driver, api, user, prefix, first_datetime, last_datetime)

    driver.close()



