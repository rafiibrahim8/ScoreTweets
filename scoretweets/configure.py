from requests.utils import dict_from_cookiejar
from copy import deepcopy
import browser_cookie3 as bc3
import requests
import json
import re

from .ua_getter import UAGetter

class Configure:
    def __init__(self, config_path):
        self.__config_path = config_path
    
    def check_entity(self, facebook_id):
        res = requests.get(f'https://mbasic.facebook.com/{facebook_id}')
        try:
            return re.findall(r'<title.*?>(.*?)\s\|\sFacebook<\/title>', res.text)[0]
        except IndexError:
            return None

    def check_cookie_valid(self, cookie):
        cookie_ = deepcopy(cookie)
        cookie_.pop('i_user', None)
        res = requests.get('https://mbasic.facebook.com/me', cookies=cookie_)
        user_name = re.findall(r'<title.*?>(.*?)<\/title>', res.text)[0]
        if 'log in or sign up' in user_name:
            return False, None
        if 'Facebook' == user_name:
            return True, self.check_entity(cookie_.get('c_user'))
        return True, user_name

    def check_for_fb_profile(self):
        browsers = {'Chrome': bc3.chrome, 'Firefox': bc3.firefox, 'Chromium': bc3.chromium, 'Edge': bc3.edge, 'Opera': bc3.opera}
        cookies = []
        for name, browser in browsers.items():
            try:
                cookie = dict_from_cookiejar(browser(domain_name='facebook.com'))
                if 'c_user' not in cookie:
                    continue
                valid, user_name = self.check_cookie_valid(cookie)
                if not valid:
                    continue
                page_name = cookie.get('i_user') and self.check_entity(cookie.get('i_user'))
                cookies.append({'browser_name': name, 'user_name': user_name, 'page_name': page_name, 'cookie': cookie})
            except bc3.BrowserCookieError:
                pass
            except Exception as e:
                print(f'Error while checking for {name}: {e}')
        return cookies
    
    def manual_cookie_in_helper(self, name, required=True):
        while True:
            input_ = input(f'Enter cookie {name}: ').strip()
            if input_ or not required:
                return input_
            print('Empty input. Enter again.')

    def manual_cookie_in(self):
        cookies = {}
        cookie_names = {
            'c_user': True,
            'datr': True,
            'sb': True,
            'xs': True,
            'i_user': False,
        }
        for c, r in cookie_names.items():
            cookie_in = self.manual_cookie_in_helper(c, r)
            if not cookie_in:
                continue
            cookies[c] = cookie_in
        cookies['m_page_voice'] = cookies.get('c_user')
        cookies['wd'] = '1366x668'
        valid, user_name = self.check_cookie_valid(cookies)
        if not valid:
            print('Failed to find a valid user with this cookies.')
            return
        page_name = cookies.get('i_user') and self.check_entity(cookies.get('i_user'))
        print(f'Found user {user_name}\nFound page {page_name}')
        return {'user_name': user_name, 'page_name': page_name, 'cookie': cookies}

    def get_user_cookie(self):
        print('Checking for facebook profiles on the PC.\nThis may take some time.\nPlease wait...') 
        profiles = self.check_for_fb_profile()
        
        if not profiles:
            print('Unable to find any profile on this PC.\nEnter manually.')
            return self.manual_cookie_in()
            
        while True:
            for i, profile in enumerate(profiles, start=1):
                page_str = (profile.get('page_name') or '') and f' with page {profile.get("page_name")}'
                print(f'{i}. {profile.get("user_name")} on {profile.get("browser_name")}{page_str}')
            user_input = input('Choose a profile or enter nothing for manual cookie input: ').strip()
            if not user_input:
                return self.manual_cookie_in()
            try: 
                selected = profiles[int(user_input)-1]
            except (ValueError, IndexError): 
                print('Invalid input. Try Again.')
                continue
            page_str = (selected.get('page_name') or '') and f' with page {selected.get("page_name")}'
            print(f'Selected profile: {selected.get("user_name")}{page_str}')
            return selected
    
    def configure_cookie(self):
        cookie = self.get_user_cookie()
        if cookie == None:
            print('Failed to get cookies.')
            return
        if not cookie.get('page_name'):
            print('Warning: You have not selected a page. You will be posting from your personal profile.')
        return cookie.get('cookie')
    
    def configure_ua(self):
        ua = UAGetter().get()
        if not ua:
            print('Unable to get User-Agent.\n')
            return
        print(f'Got User-Agent: {ua}\n')
        return ua
    
    def configure_keep_day(self):
        while True:
            print('If you choose to delete posts later, you can choose how many days to keep posts.\n')
            keep_day = input('Enter number of days (default: 2): ').strip()
            if not keep_day:
                return 2
            try:
                keep_day = int(keep_day)
            except ValueError:
                print('Invalid input. Enter again.')
                continue
            if keep_day < 1:
                print('Invalid input. Enter again.')
                continue
            return keep_day

    def configure(self):
        cookies = self.configure_cookie()
        if not cookies:
            print('Configaretion failed.')
            return
        
        ua = self.configure_ua()
        keep_day = self.configure_keep_day()
        if not ua:
            print('Configaretion failed.')
            return

        headers = {
            'User-Agent': ua,
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Te': 'trailers'
        }

        with open(self.__config_path, 'w') as f:
            json.dump({'headers': headers, 'cookies': cookies, 'keep_day': keep_day}, f, indent=4)

        print('Configure successful')
