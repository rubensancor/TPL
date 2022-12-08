import sys
import json
import traceback
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from bs4 import BeautifulSoup
import tweepy

N_FAILS = 5
SCROLL = 1200
HASHTAG = ''
DATA_PATH = './data/'

# Keys for Tweepy
CONFIG_FILEPATH = './conf/'
config_twitter = json.load(open(CONFIG_FILEPATH + 'conf.json', 'r'))


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

# Get desired webpage
driver.get('https://twitter.com/search?q=%23'+ HASHTAG +'&src=typed_query&f=live')
sleep(3)



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
            # print('Fail ++')
            fail = fail + 1
        temp_tweets = set(tweet_ids)
    except:  
        traceback.print_exc()
        driver.close()

    sleep(3)
    driver.execute_script("window.scrollTo(0, " + str(SCROLL * times) + ");var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    times = times + 1

driver.close()

tweet_ids = list(set(tweet_ids))
# print(tweet_ids)
with open(DATA_PATH + HASHTAG +'_ids.txt', 'w') as f:
        for item in tweet_ids:
            f.write("%s\n" % item)

all_tweets = []

for tw_id in tweet_ids:
    tweet = api.get_status(tw_id)
    all_tweets.append(json.dumps(tweet._json) + ",\n")

with open(DATA_PATH + HASHTAG +'_tweets.json', 'w') as f:
    f.write('[')
    for tweet in all_tweets:
        # json_str = tweet.encode('utf-8')
        f.write(tweet)
    f.write(']')