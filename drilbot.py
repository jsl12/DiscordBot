import re
from pathlib import Path
from random import choice

import discord
import twitter
import yaml

KEYWORDS = ['dick', 'trol', 'ass', 'cum', 'smok']

apikey = Path('apikey.yaml')

with apikey.open('r') as file:
    key = yaml.load(file, Loader=yaml.SafeLoader)

client = discord.Client()
api = twitter.Api(
    consumer_key=key['TWITTER']['API_KEY'],
    consumer_secret=key['TWITTER']['API_SECRET_KEY'],
    access_token_key=key['TWITTER']['ACCESS_TOKEN'],
    access_token_secret=key['TWITTER']['ACCESS_TOKEN_SECRET']
)

@client.event
async def on_ready():
    print(f'connected as {client.user}')

@client.event
async def on_message(msg: discord.Message):
    if (msg.author == client.user) or (msg.channel.name != 'robotics-facility'):
        return

    if re.search('dril', msg.content):
        for k in KEYWORDS:
            if k in msg.content:
                text = recent_keyword_tweet('dril', keyword=k).text
                if text is not None:
                    await msg.channel.send(text)
                else:
                    break
                return
        await msg.channel.send(random_tweet('dril'))

def random_tweet(screen_name:str , count=200) -> str:
    return choice(recent_tweets(screen_name, count)).text

def recent_tweets(screen_name: str, count:int = 200):
    return api.GetUserTimeline(
        screen_name=screen_name,
        include_rts=False,
        exclude_replies=True,
        count=count
    )

def recent_keyword_tweet(screen_name:str, keyword:str, count:int = 200):
    try:
        return choice([tweet for tweet in recent_tweets(screen_name, count) if keyword in tweet.text])
    except IndexError:
        return

client.run(key['DISCORD_TOKEN'])
