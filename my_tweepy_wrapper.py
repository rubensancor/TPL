import tweepy, json, time, datetime, gzip, sys, argparse

CONFIG_FILEPATH = './conf/'
config_twitter = json.load(open(CONFIG_FILEPATH + 'conf.json', 'r'))

CONSUMER_KEY = config_twitter['CONSUMER_KEY']
CONSUMER_SECRET = config_twitter['CONSUMER_SECRET']
USER_TOKEN = config_twitter['USER_TOKEN']
USER_SECRET = config_twitter['USER_SECRET']


parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--dataset', type=str,
                    choices=['deloitte', 'verizon', 'microsoft', 'boeing'
                             'amnesty', 'labour'],
                    help='Dataset to snif the tweets from')

args = parser.parse_args()

tweets = []
initial_time = time.time()

def get_list_members_ids(api, list_owner, list_name):
    members = []
    for page in list(tweepy.Cursor(api.list_members, list_owner, list_name).items()):
        members.append(page)
    print((str(len(members))))
    return [ m.id_str for m in members ]

def streaming_timeline_users(auth, list_ids):
    listener = StdOutListener()
    stream = tweepy.Stream(auth, listener)
    stream.filter(follow=list_ids)

def get_last_4000_tweets(api, list_ids):
    loops = 40
    WAIT_MINS = 5
    for id_str in list_ids:
        print(('Checking the timeline of %s' % (id_str)))
        new_tweets = []
        i = 0
        repeat = True
        while repeat:
            try:
                for i in range(loops):
                    if len(new_tweets) > 0:
                        new_tweets.extend(api.user_timeline(user_id=id_str, max_id=new_tweets[-1].id_str, count=100 ,tweet_mode='extended'))
                    else:
                        new_tweets.extend(api.user_timeline(user_id=id_str, count=100, tweet_mode='extended'))
                repeat = False
            except tweepy.error.TweepError as e:
                repeat = True
                print(('(%s) Time limit exceeded. Waiting %s mins' % (time.ctime(), WAIT_MINS)))
                print(('\t', e))
                sys.stdout.flush()
                try:
                    if e.args[0][0]['code'] == 88:
                        print(i)
                        i -= 1
                        time.sleep(WAIT_MINS * 60)
                    else:
                        repeat = False
                except:
                    repeat = False
        
        print(('%s tweets have been recovered from %s timeline' % (len(new_tweets), id_str)))
        print((len(new_tweets)))
        file_name = '../Data/Tweets/tweets_raw/{}/tweets-{}.txt.gz'.format(args.dataset, id_str)
        print(('Writing file:', file_name))
        with gzip.open(file_name, 'wb',) as f:
            for tweet in new_tweets:
                json_str = json.dumps(tweet._json) + "\n"
                json_str = json_str.encode('utf-8')
                f.write(json_str)
        print('Writing finished')

class StdOutListener(tweepy.StreamListener):

    def on_data(self, raw_data):
        folder_name = ''
        global tweets, initial_time
        elapsed_time = time.time () - initial_time #elapsed secons
        #save the status every 30 mins
        if elapsed_time >= 60 * 30:
            now = datetime.datetime.now()
            file_name = './'+folder_name+'/tweets-%s-%s-%s-%s-%s.txt.gz' % (now.month, now.day, now.hour, now.minute, now.second)
            print('Writing file:', file_name)
            with gzip.open(file_name, 'w') as f:
                for tweet in tweets:
                    f.write(json.dumps(tweet) + '\n')
            print('Writing finished')
            tweets = []
            initial_time = time.time()

        try:
            data = json.loads(raw_data)
            tweets.append(data)
        except:
            now = datetime.datetime.now()
            print('(%s %s:%s)Invalid json data: %s' % (now.day, now.hour, now.minute, raw_data))

        return True

    def on_error(self, status_code):
        now = datetime.datetime.now()
        print('(%s %s:%s)Got an error with status code: %s' % (now.day, now.hour, now.minute, status_code))
        #sleep 5 mins if an error occurs
        time.sleep(5 * 60)
        return True # To continue listening

    def on_timeout(self):
        print('Timeout...')
        return True # To continue listening


def get_status_text(api, status_id):
    print("Status id: " + str(status_id))
    try:
        return api.get_status(status_id, tweet_mode='extended').full_text
    except tweepy.error.TweepError as e:
        if e[0][0]['code'] == 88:
            print("Rate limit exceeded, waiting 15 minutes.")
            time.sleep(60*15)
            get_status_text(api, status_id)
        else:
            print(e)
            return None


def get_status(api, status_id):
    print("Status id: " + str(status_id))
    try:
        return api.get_status(status_id, tweet_mode='extended')._json
    except tweepy.error.TweepError as e:
        print(e)
        try:
            if e[0][0]['code'] == 88:
                print("Rate limit exceeded, waiting 15 minutes.")
                #print e
                time.sleep(60*15)
                get_status(api, status_id)
            else:
                print(e)
                return None
        except Exception as e_2:
            print(e_2)
            return None


def get_list_of_tweets(api, tweets_ids):
    recovered_tweets = []
    for tweet_id in tweets_ids:
        recovered_tweets.append(get_status(api, tweet_id))
    return recovered_tweets

def get_usernames(api, id_list):
    usernames = []
    for user_id in id_list:
        user = api.get_user(int(user_id))
        usernames.append(user.screen_name)
    return usernames

if __name__ == '__main__':
    print('Starting...')


    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(USER_TOKEN, USER_SECRET)

    api = tweepy.API(auth, 
                    wait_on_rate_limit=True, 
                    wait_on_rate_limit_notify=True)
    
    twitter_ids = []

    with open('../Data/Organisation_employees/users/' + args.dataset + '.json') as data_file:
        data = json.load(data_file)
        for key in data.keys():
            twitter_ids.append(key)

    get_last_4000_tweets(api, twitter_ids)
