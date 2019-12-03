import re
from pathlib import Path
from random import choice

from typing import List
import discord
import twitter
import yaml


class DrilBot:
    KEYWORDS = [
        'dick',
        'trol',
        'ass',
        'shit'
        'cum',
        'smok',
        'media',
        'otis',
        'digimon',
        'human',
        'loyalty',
        'youtube',
        'celebs',
        'girl',
        'food',
        'politics',
        'culture',
        'jack(ing)? off',
        'dog',
        'blue check mark',
        'account',
        'wisdom',
        'sports',
        'dinner',
        'kfc',
        'donald'
    ]

    def __init__(self, apikey_path):
        self.load_keys(apikey_path)
        self.connect_to_twitter()
        self.connect_to_discord()

    def load_keys(self, apikey_path):
        if not isinstance(apikey_path, Path):
            apikey_path = Path(apikey_path)

        with apikey_path.open('r') as file:
            self.key = yaml.load(file, Loader=yaml.SafeLoader)

    def connect_to_twitter(self):
        self.api = twitter.Api(
            consumer_key=self.key['TWITTER']['API_KEY'],
            consumer_secret=self.key['TWITTER']['API_SECRET_KEY'],
            access_token_key=self.key['TWITTER']['ACCESS_TOKEN'],
            access_token_secret=self.key['TWITTER']['ACCESS_TOKEN_SECRET']
        )

    def connect_to_discord(self):
        self.client = discord.Client()

    def run(self):
        self.client.run(self.key['DISCORD_TOKEN'])

    def get_tweets(self, **kwargs) -> List[twitter.Status]:
        return self.api.GetUserTimeline(
            screen_name='dril',
            include_rts=False,
            exclude_replies=True,
            count=200,
            **kwargs
        )

    def get_keyword_tweets(self, keyword:str, min:int = 5) -> List[twitter.Status]:
        res = []
        while len(res) < min:
            try:
                last_tweet = next_page[-1].id
            except UnboundLocalError:
                last_tweet = None
            except IndexError:
                # TODO figure out why this happens sometimes
                break
            next_page = self.get_tweets(max_id=last_tweet)
            res.extend([tweet for tweet in next_page if re.search(keyword, tweet.text, re.IGNORECASE)])
        return res

    def process_message(self, msg: discord.Message):
        if msg.author == self.client.user:
            return

        if msg.channel.name != 'robotics-facility':
            return

        if re.search('dril', msg.content, re.IGNORECASE):
            for k in self.KEYWORDS:
                if re.search(k, msg.content, re.IGNORECASE):
                    try:
                        return choice(self.get_keyword_tweets(k)).text
                    except IndexError:
                        # no tweets found
                        break
            return choice(self.get_tweets()).text


if __name__ == '__main__':
    drilbot = DrilBot('apikey.yaml')

    @drilbot.client.event
    async def on_ready():
        print(f'connected as {drilbot.client.user}')

    @drilbot.client.event
    async def on_message(msg: discord.Message):
        response = drilbot.process_message(msg)
        if response is not None:
            await msg.channel.send(response)

    drilbot.run()