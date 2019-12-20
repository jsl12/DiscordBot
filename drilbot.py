import re
from pathlib import Path
from random import choice
from typing import List

import discord
import twitter
import yaml

from scraper import Scraper


class DrilBot(Scraper):
    CFG = 'dril.yaml'
    REGEX_INDEX = re.compile('dril\[(-?\d+)\]')
    REGEX_ADD_KEYWORD = re.compile('^dril add "(.*)"$')

    def __init__(self, cfg_path=None):
        if cfg_path is not None:
            self.CFG = cfg_path
        self.load_tweets()
        self.init_table()
        self.client = discord.Client()

    def init_table(self):
        self.table = {key: super(DrilBot, self).get_keyword_tweets(key) for key in self.keywords}
        self.table = {key: tweets for key, tweets in self.table.items() if len(tweets) > 0}

    def run(self):
        self.client.run(self.api_key['DISCORD_TOKEN'])

    @property
    def cfg(self):
        with Path(self.CFG).open('r') as file:
            return yaml.load(file, Loader=yaml.SafeLoader)

    @property
    def api_key(self):
        with Path(self.cfg['API']).open('r') as file:
            return yaml.load(file, Loader=yaml.SafeLoader)

    @property
    def keywords(self):
        return self.cfg['KEYWORDS']

    def load_tweets(self):
        return super().load_tweets(self.cfg['TWEETS'])

    def print_keyword_tweets(self, keyword:str):
        for t in self.get_keyword_tweets(keyword):
            print(t.text)

    def get_user_tweets(self, count=200, **kwargs):
        if not hasattr(self, 'api'):
            self.connect(self.cfg['API'])
        kwargs['user'] = 'dril'
        return super(DrilBot, self).get_user_tweets(count=count, **kwargs)

    def get_older_tweets(self, count=200, **kwargs):
        if not hasattr(self, 'api'):
            self.connect(self.cfg['API'])
        return super().get_older_tweets(user='dril', count=count, **kwargs)

    def process_message(self, msg: str):
        if 'dril' in msg:
            match_index = self.REGEX_INDEX.search(msg)
            match_add_keyword = self.REGEX_ADD_KEYWORD.search(msg)
            match_keyword = self.keyword_tweet(msg)

            if msg == 'dril keywords':
                # this is like the help command
                return self.print_keywords()
            elif match_add_keyword is not None:
                self.add_keyword(match_add_keyword.group(1))
            elif match_index is not None:
                # looks for something like 'dril[0]' which would be the first (most recent) tweet
                return self.tweets[int(m.group(1))]
            elif match_keyword:
                # looks for some kind of keyword based on dril.yaml
                return match_keyword
            else:
                # in the default case, just return a random tweet
                return choice(self.tweets)

    def add_keyword(self, new_keyword):
        with Path(self.CFG).open('r') as file:
            cfg = yaml.load(file, Loader=yaml.SafeLoader)
        cfg['KEYWORDS'].append(new_keyword)
        with Path(self.CFG).open('w') as file:
            yaml.dump(cfg, file, Dumper=yaml.SafeDumper)

    def print_keywords(self):
        res = 'drilbot has the following keywords:\n'
        for key in self.keywords:
            res += f' - {key}\n'
        return res

    def keyword_tweet(self, msg:str):
        for k in self.keywords:
            m = re.search(k, msg, re.IGNORECASE)
            if m is not None:
                print(m.string[:m.start()] + f'({m.group()})' + m.string[m.end():])
                return choice(self.get_keyword_tweets(k))

    def get_keyword_tweets(self, keyword:str) -> List[twitter.Status]:
        return self.table[keyword]

if __name__ == '__main__':
    drilbot = DrilBot()

    CHANNEL_WHITELIST = ['robotics-facility', 'star-wars-shit']

    @drilbot.client.event
    async def on_ready():
        print(f'connected as {drilbot.client.user}')

    @drilbot.client.event
    async def on_message(msg: discord.Message):
        if msg.author == drilbot.client.user:
            return

        m = re.search('dril is (playing|listening|watching) ([\w ]+)', msg.content)
        if m is not None:
            print(f'Status: {m.group(1)} {m.group(2)}')
            if m.group(1) == 'playing':
                await drilbot.client.change_presence(activity=discord.Game(m.group((2))))
            elif m.group(1) == 'listening':
                await drilbot.client.change_presence(activity=discord.Activity(name=m.group(2), type=discord.ActivityType.listening))
            elif m.group(1) == 'watching':
                await drilbot.client.change_presence(activity=discord.Activity(name=m.group(2), type=discord.ActivityType.watching))
            return

        if msg.channel.name not in CHANNEL_WHITELIST:
            return
        else:
            response = drilbot.process_message(msg.content)
            if response is not None:
                if isinstance(response, twitter.Status):
                    drilbot.last_tweet = response
                    response = response.text
                await msg.channel.send(response)

    drilbot.run()
