from requests.utils import dict_from_cookiejar
import browser_cookie3 as bc3
import requests
import json
import re

from .ua_getter import UAGetter

def get_mbasic_link(link:str):
    try:
        slash = link.index('/', 8)
    except ValueError:
        try:
            slash = link.index('/', 4) # fb.me/hello, m.me/hello
        except:
            return
    return 'https://mbasic.facebook.com' + link[slash:]

class Configure:
    def __init__(self, config_path):
        self.__config_path = config_path
    
    def id_u(self, res_dot_text):
        try:
            return re.findall('<a href=\\"\\/.{1,}\\/about\\?lst=[^%]+%3A([^%\\"]+)', res_dot_text)[0]
        except:
            return None

    def check_cookie_whois(self, cookie):
        res = requests.get('https://mbasic.facebook.com/me', cookies=cookie)
        if self.id_u(res.text) != cookie.get('c_user'):
            return None
        return re.findall('<title>(.{1,})<\\/title>+', res.text)[0]

    def check_for_fb_profile(self):
        browsers = {'Chrome': bc3.chrome, 'Firefox': bc3.firefox, 'Chromium': bc3.chromium, 'Edge': bc3.edge}
        cookies = []
        for name, browser in browsers.items():
            try:
                cookie = dict_from_cookiejar(browser(domain_name='facebook.com'))
                user_name = self.check_cookie_whois(cookie)
                if user_name != None:
                    cookies.append({'browser_name': name, 'user_name': user_name, 'cookie': cookie})
            except:
                pass
        return cookies
    
    def manual_cookie_in_helper(self, name):
        while True:
            input_ = input(f'Enter cookie {name}: ').strip()
            if input_:
                return input_
            print('Empty input. Enter again.')

    def manual_cookie_in(self):
        cookie = {'wd': '1366x668'}
        required = ['c_user', 'datr', 'sb', 'xs']
        for i in required:
            cookie[i] = self.manual_cookie_in_helper(i)
        user_name =  self.check_cookie_whois(cookie)
        if user_name == None:
            print('Failed to find a valid user with this cookies.')
            return
        print(f'Found user {user_name}')
        return {'user_name': user_name, 'cookie': cookie}

    def get_user_cookie(self):
        print('Checking for facebook profiles on the PC.\nThis may take some time.\nPlease wait...') 
        profiles = []
        for i in self.check_for_fb_profile():
            if i.get('user_name') != 'Facebook – log in or sign up':
                profiles.append(i)
        
        if not profiles:
            print('Unable to find any profile on this PC.\nEnter manually.')
            return self.manual_cookie_in()
            
        while True:
            for i, profile in enumerate(profiles, start=1):
                print(f'{i}. {profile.get("user_name")} on {profile.get("browser_name")}')
            user_input = input('Choose a profile or enter nothing for manual cookie input: ').strip()
            if not user_input:
                return self.manual_cookie_in()
            try: 
                cookie = profiles[int(user_input)-1]
            except: 
                print('Invalid input. Try Again.')
                continue
            print(f'Selected profile: {cookie.get("user_name")}')
            return cookie
    
    def configure_cookie(self):
        cookie = self.get_user_cookie()
        if cookie == None:
            print('Failed to get cookies.')
            return
        return cookie.get('cookie')
    
    def configure_ua(self):
        ua = UAGetter().get()
        if not ua:
            print('Unable to get User-Agent.\n')
            return
        print(f'Got User-Agent: {ua}\n')
        return ua
        
    def configure(self):
        cookies = self.configure_cookie()
        if not cookies:
            print('Configaretion failed.')
            return
        
        ua = self.configure_ua()
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
            json.dump({'headers': headers, 'cookies': cookies}, f, indent=4)

        print('Configure successful')
