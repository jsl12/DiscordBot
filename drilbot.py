import re
from pathlib import Path
from random import choice

import discord
import twitter
import yaml

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
        await msg.channel.send(random_tweet('dril'))

def random_tweet(screen_name, count=200):
    return choice(api.GetUserTimeline(
        screen_name=screen_name,
        include_rts=False,
        exclude_replies=True,
        count=count
    )).text

client.run(key['DISCORD_TOKEN'])
