import json
import argparse
import telegram

# Arguments for the data collection software
parser = argparse.ArgumentParser(description='Main file')
parser.add_argument('-c', '--config',
                    required=True,
                    default='config.json',
                    help='The config file to use.')
parser.add_argument('-m',
                    required=True,
                    help='Message to send to the bot.')                    
args = parser.parse_args()

# Keys for Tweepy
config_file = json.load(open(args.config, 'r'))

telegram_token = config_file['TELEGRAM_TOKEN']
telegram_chat_id = config_file['TELEGRAM_CHAT_ID']

bot = telegram.Bot(token=telegram_token)
bot.sendMessage(chat_id=telegram_chat_id, text=args.m)
