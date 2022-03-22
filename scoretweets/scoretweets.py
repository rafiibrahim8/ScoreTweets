from argparse import ArgumentParser
import asyncio
import json
import os

from . import __version__, __config_dir
from .score_poster import FacebookPostClient, DiscordPostClient, ScoreTweetClient
from .configure import Configure
from .discord_debug import DebugDiscord



def run_score_tweet(env_path, config_path, required_words):
    with open(os.path.expanduser(env_path), 'r') as f:
        env = json.load(f)
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    debug_discord = DebugDiscord(env['debug_discord'])

    fpc = FacebookPostClient(config, env['facebook_group_id'], debug_discord)
    dpc = DiscordPostClient(env['discord_hook'], debug_discord)
    stc = ScoreTweetClient(env, dpc, fpc, required_words, debug_discord)

    print('Running...')

    loop = asyncio.get_event_loop()
    loop.create_task(fpc.run())
    loop.create_task(dpc.run())
    loop.create_task(stc.run())
    loop.run_forever()

def main():
    env_path = os.path.join(os.path.expanduser(__config_dir), 'env.json')
    config_path = os.path.join(os.path.expanduser(__config_dir), 'config.json')

    parser = ArgumentParser(description='Post score tweets by PCSPro to discord and facebook')
    parser.add_argument('-c,--configure', action='store_true', dest='is_configure', default=False, help='Configure facebook cookies and other stuffs.')
    parser.add_argument('-e,--env', dest='env_path', default=env_path, help=f'Environment file path. Default: {env_path}')
    parser.add_argument('-v','--version',help='Prints version information.',action='version',version= 'v'+ __version__)
    parser.add_argument('required_word', nargs='*', help='Word thats must be present in tweet to count as score')
    
    args = parser.parse_args()
    os.makedirs(os.path.expanduser(__config_dir), exist_ok=True)

    if args.is_configure:
        Configure(config_path=config_path).configure()
    else:
        run_score_tweet(args.env_path, config_path, args.required_word)
