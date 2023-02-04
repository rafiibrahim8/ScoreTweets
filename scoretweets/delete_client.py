import os
import asyncio
import json
import time

from . import CONFIG_DIR

class DeleteClient:
    def __init__(self, keep_day, facebook_client, debug_discord, **kwargs):
        self.__save_dir = os.path.join(os.path.expanduser(CONFIG_DIR), 'post_ids')
        self.__keep_time = keep_day * 24 * 60 * 60
        self.__facebook_client = facebook_client
        self.__debug_discord = debug_discord
        self.__wait_time = kwargs.get('wait_time', 1800)
    
    def __delete_post(self, file):
        with open(os.path.join(self.__save_dir, file), 'r') as f:
            post = json.load(f)
        if self.__facebook_client.delete_post(post['story_id']):
            os.remove(os.path.join(self.__save_dir, file))
        else:
            self.__debug_discord.error(f'Facebook post deletion failed.')
    
    def __delete(self):
        if not os.path.exists(self.__save_dir):
            return
        files = sorted(os.listdir(self.__save_dir))
        for file in files:
            post_time = int(file.split('.')[0])
            if time.time() - post_time > self.__keep_time:
                self.__delete_post(file)
                continue
            break

    async def run(self):
        while True:
            await asyncio.sleep(self.__wait_time)
            self.__delete()
