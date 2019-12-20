import pickle
import re
import time
from pathlib import Path
from typing import List

import twitter
import yaml


class Scraper:
    def __init__(self, apikey_path):
        self.connect(apikey_path)

    def connect(self, apikey_path):
        if not isinstance(apikey_path, Path):
            apikey_path = Path(apikey_path)
        with apikey_path.open('r') as file:
            key = yaml.load(file, Loader=yaml.SafeLoader)
        self.api = twitter.Api(
            consumer_key=key['TWITTER']['API_KEY'],
            consumer_secret=key['TWITTER']['API_SECRET_KEY'],
            access_token_key=key['TWITTER']['ACCESS_TOKEN'],
            access_token_secret=key['TWITTER']['ACCESS_TOKEN_SECRET']
        )

    def get_user_tweets(self, user:str, count=200, **kwargs)  -> List[twitter.Status]:
        return self.api.GetUserTimeline(
            screen_name=user,
            include_rts=False,
            exclude_replies=True,
            count=count,
            trim_user=True,
            **kwargs
        )

    def clean(self):
        ids = set()
        self.tweets = [t for t in self.tweets if t.id not in ids and not ids.add(t.id)]
        self.tweets = self.sort_by('id')[::-1]
        return self.tweets

    def get_older_tweets(self, user:str, count:int = 200, **kwargs):
        initial_length = len(self.tweets)
        new_tweets = self.get_user_tweets(
            user=user,
            count=count,
            max_id=int(self.tweets[-1].id),
            **kwargs
        )
        self.tweets.extend(new_tweets)
        self.clean()
        final_length = len(self.tweets)
        length_res = final_length - initial_length
        print(f'Found {length_res} new tweets')
        return length_res

    def get_keyword_tweets(self, keyword:str) -> List[twitter.Status]:
        return [t for t in self.tweets if re.search(keyword, t.text, re.IGNORECASE)]

    def load_tweets(self, path):
        if not isinstance(path, Path):
            path = Path(path)
        with path.open('rb') as file:
            loaded_tweets = pickle.load(file)
            if hasattr(self, 'tweets'):
                self.tweets.extend(loaded_tweets)
            else:
                self.tweets = loaded_tweets
        self.clean()
        return self.tweets

    @property
    def len(self):
        return len(self.tweets)

    def save_tweets(self, path):
        if not isinstance(path, Path):
            path = Path(path)
        with path.open('wb') as file:
            pickle.dump(self.tweets, file)

    def sort_by(self, key):
        return sorted(self.tweets, key=lambda t: getattr(t, key))

    def print(self):
        for t in self.tweets:
            print(f'{t.text.strip()}')

    def get_continuous(self, save_path, sleep_time=.5, **kwargs):
        res = self.get_older_tweets(**kwargs)
        while res > 0:
            res = self.get_older_tweets(**kwargs)
            time.sleep(sleep_time)
        self.save_tweets(save_path)


if __name__ == '__main__':
    s = Scraper('apikey.yaml')
    SAVE_LOC = 'dril.pickle'
    s.load_tweets(SAVE_LOC)
    for tweet in s.tweets:
        print(tweet.text)