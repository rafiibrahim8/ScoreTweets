from requests.utils import cookiejar_from_dict
from traceback import format_exc
from bs4 import BeautifulSoup
from datetime import datetime
import requests
import asyncio
import random
import time
import re

class PostClient:
    def __init__(self):
        self.__queue = asyncio.Queue()
        self._session = requests.Session()

    def put_score(self, score):
        self.__queue.put_nowait(score)

    def _post(self, score):
        raise NotImplementedError('Subclass should implement this')

    async def run(self):
        while True:
            score = await self.__queue.get()
            self._post(score)

class FacebookPostClient(PostClient):
    EMOJI_SEQUENCES = ['8)']
    def __init__(self, config, group_id, debug_discord):
        super().__init__()
        self._session.cookies = cookiejar_from_dict(config['cookies'])
        self._session.headers = config['headers']
        self.__group_id = group_id
        self.__debug_discord = debug_discord
    
    @staticmethod
    def __replace_auto_emoji(text):
        for seq in FacebookPostClient.EMOJI_SEQUENCES:
            text = text.replace(seq, seq[0] + ' ' + seq[1:])
        return text
    
    def __post_impl(self, text):
        res = self._session.get(f'https://mbasic.facebook.com/groups/{self.__group_id}')
        soup = BeautifulSoup(res.text, 'html.parser')
        
        fb_dtsg = soup.find(attrs={'name':'fb_dtsg'}).get('value')
        jazoest = soup.find(attrs={'name':'jazoest'}).get('value')
        action = soup.find(attrs={'id': 'mbasic-composer-form'}).get('action')
        
        data = {
            'fb_dtsg': fb_dtsg,
            'jazoest': jazoest,
            'target': self.__group_id,
            'c_src':'group',
            'cwevent': 'composer_entry',
            'referrer':'group',
            'ctype': 'inline',
            'cver': 'amber',
            'rst_icv': '',
            'xc_message': self.__replace_auto_emoji(text),
            'view_post': 'Post'
        }

        res=self._session.post(f'https://mbasic.facebook.com{action}', data=data)


    def _post(self, score):
        try:
            self.__post_impl(score)
        except KeyboardInterrupt:
            raise
        except:
            self.__debug_discord.error(f'Facebook posting failed. Reason:\n{format_exc()}')

class DiscordPostClient(PostClient):
    def __init__(self, hook_url, debug_discord):
        super().__init__()
        self.__hook_url = hook_url
        self.__debug_discord = debug_discord
    
    @staticmethod
    def __fmt_post_data(score):
        data = {'embeds':[{'color': random.randint(0, 0xffffff)}]}
        score_split = [i.strip() for i in score.split('\n') if i.strip()]
        if not re.fullmatch('[A-Z]{3} v [A-Z]{3}', score_split[0]) or len(score_split)<2:
            data['embeds'][0]['description'] = score
            return data
        x, y = re.findall('([A-Z]{3})', score_split[0])
        score_split[0] = f'**{x}** v **{y}**'
        data['content'] = score_split[0]
        data['embeds'][0]['description'] = '\n'.join(score_split[1:])
        return data


    def _post(self, score): 
        try:
            self._session.post(self.__hook_url, json=self.__fmt_post_data(score))
        except:
            self.__debug_discord.error(f'Discord posting failed. Reason: {format_exc()}')

class ScoreTweetClient:
    def __init__(self, env, discord_client, facebook_client, required_words, debug_discord, **kwargs):
        self.__url = f"https://api.twitter.com/2/users/{env['twitter_id']}/tweets"
        self.__required_words = required_words
        self.__debug_discord = debug_discord
        self.__debug_discord_url = env.get('debug_discord')
        self.__last_posted = time.time()
        self.__discord_client = discord_client
        self.__facebook_client = facebook_client
        self.__session = requests.Session()
        self.__session.headers = {'Authorization' : f"Bearer {env['bearer_token']}"}
        self.__wait_time = kwargs.get('wait_time', 5)
        self.__params = {'tweet.fields': 'created_at', 'max_results': kwargs.get('max_results', 10)}

    @staticmethod
    def __timestamp_parser(tweet):
        return {
            'timestamp': datetime.fromisoformat(tweet['created_at'].replace('Z','+00:00')).timestamp(),
            'text': tweet['text'],
            'id': tweet['id']
        }

    def __eligible_required_words(self, tweet):
        for i in self.__required_words:
            if not i in tweet['text']:
                return False
        return True

    def __run_impl(self):
        tweets = self.__session.get(self.__url, params=self.__params).json()
        tweets = tweets.get('data', [])
        tweets = map(self.__timestamp_parser, tweets)
        tweets = filter(self.__eligible_required_words, tweets)
        tweets = list(filter(lambda x: x['timestamp'] > self.__last_posted, tweets))
        tweets.sort(key=lambda x: x['timestamp'])
        for t in tweets:
            self.__discord_client.put_score(t['text'])
            self.__facebook_client.put_score(t['text'])
            self.__last_posted = t['timestamp']
            
    async def run(self):
        while True:
            try:
                self.__run_impl()
            except KeyboardInterrupt:
                raise
            except:
                self.__debug_discord.error(f'Running error occoured. Reason: {format_exc()}')
            await asyncio.sleep(self.__wait_time)
