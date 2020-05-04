from multiprocessing.pool import ThreadPool
import threading
import subprocess
import configparser
import requests
import psutil
import signal
import random
import string
import os.path
import time
import sys
import os


class RobloxBot:
        """A simple Roblox bot class"""
        def __init__(self):
                # creates a request session
                self.session = requests.session()
                # creates headers
                self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0' }
                # sets sessions headers
                self.session.headers.update(self.headers)

        def sign_in(self, username, password):
                # creates login payload
                payload = {'username': username, 'password': password, 'submitLogin': 'Log+In'}
                # loops until successful
                while True:
                        # grabs random proxy
                        proxy = random.choice(proxies)
                        # notifies user
                        # print('Trying proxy:', proxy)
                        # adds proxy to the proxies dict to be used with requests
                        proxy_payload = {'http': 'http://' + proxy, 'https': 'https://' + proxy}
                        # sets sessions proxy
                        self.session.proxies.update(proxy_payload)
                        # attempts to log in via proxy
                        try:
                                # posts login data to roblox
                                r = self.session.post('https://www.roblox.com/newlogin', data=payload, headers={'Referer': 'https://www.roblox.com/'}, timeout=5)
                                # checks status
                                r.raise_for_status()
                                # notifies user
                                # print('Found working proxy:', proxy)
                        except:
                                # print(proxy, 'could not connect.')
                                continue
                        # validates log in
                        if 'My Feed' in r.text:
                                # notifies user
                                print('Successfully logged into:', username)
                                return True
                        elif 'not a robot!' in r.text:
                                # if a captcha is present
                                # print('Captcha found. Retrying.')
                                continue
                        else:
                                # notifies user
                                # print('Login failed for:', username)
                                return False

        def like_game(self, game_id):
                # creates referer headers
                referer = {'Referer': 'https://www.roblox.com/games/{}'.format(game_id), "RBX-For-Gameauth": "true"}
                # gets authticket for user
                auth_ticket = self.session.get('https://www.roblox.com/game-auth/getauthticket', headers=referer).text
                # gets browser tracker
                browser = ''.join(str(random.randint(0,9)) for x in range(10))
                # formats uri parameters for game launch
                mapped_uri = "roblox-player:1+launchmode:play+gameinfo:{}+launchtime:1493656459622+placelauncherurl:https%3A%2F%2Fassetgame.roblox.com%2Fgame%2FPlaceLauncher.ashx%3Frequest%3DRequestGame%26browserTrackerId%3D{}%26placeId%3D{}%26isPartyLeader%3Dfalse+browsertrackerid:{}".format(auth_ticket, browser, game_id, browser)
                with launch_lock:
                        # launches roblox
                        roblox = subprocess.Popen([game_path, mapped_uri])
                        # notifies user
                        print('Successfully launched Roblox and joined game:', game_id)
                        # waits 10 seconds
                        time.sleep(game_launch_time)
                        # kills process
                        for process in psutil.process_iter():
                                # check whether the process name matches
                                if process.name() == 'RobloxPlayerBeta.exe':
                                        # kills process
                                        process.kill()
                # gets cookies
                r = self.session.get('https://www.roblox.com/games/{}'.format(game_id))
                # extracts csrf token
                csrf_token = r.text.split("Roblox.XsrfToken.setToken('")[-1].split("');")[0]
                # creates like payload
                payload = {'assetId': game_id, 'vote': votecheck}
                # creates like headers
                headers = {'X-CSRF-TOKEN': csrf_token, 'Referer': r.url}
                # sends like post request to roblox
                r = self.session.post('https://www.roblox.com/voting/vote', params=payload, headers=headers)
                # validates like
                if r.json()['Success']:
                        # notifies user
                        print('Successfully liked game:', game_id)
                else:
                        # notifies user
                        print('There was a problem liking the game:', game_id)
                        print('Reason:', r.json()['Model']['ReasonForNotVoteable'])
                # sends favourite to roblox
                r = self.session.post('https://www.roblox.com/favorite/toggle', params={'assetId': game_id}, headers=headers)
                # validates favourite
                if r.json()['success']:
                        # notifies user
                        print('Successfully favourited game:', game_id)
                else:
                        # notifies user
                        print('There was a problem favoriting game:', game_id)

def start(userpass):
        # instantiates roblox bot
        bot = RobloxBot()
        # signs up on roblox with username and password
        if bot.sign_in(username=userpass[0], password=userpass[1]):
                # likes game with certain id
                bot.like_game(game_id=game_id)

if __name__ == '__main__':
        launch_lock = threading.Lock()
        # reads config file
        config = configparser.ConfigParser()
        config.read('config.ini')
        try:
                print("Modded and fixed by psyduckc @ v3rmillion")
                # sets game path
                game_path = config['general']['game_path']
                # verifies game exists
                if os.path.isfile(game_path):
                        print('Verified game exists.')
                else:
                        sys.exit('Could not find your Roblox launcher.')
                # sets proxy list path
                proxy_list_path = config['general']['proxy_list_path']
                # gets proxy list
                proxies = open(proxy_list_path).read().split('\n')
                # notifies user
                print('Loaded proxies.')
                # sets account list path
                account_list_path = config['general']['account_list_path']
                # notifies user
                print('Loaded accounts.')
                # gets thread count
                thread_count = int(config['general']['thread_count'])
                game_launch_time = int(config['general']['game_launch_time'])
        except KeyError:
                sys.exit('Config file error.')
        # prompts user for game id
        game_id = input('Please enter the game mode ID: ')
        # gets accounts
        votecheck = input("Like = true, Dislike = false, Remove likes/dislikes = nil: ")
        votecheck.lower()
        #
        accounts = [x.split(':') for x in open(account_list_path).read().split('\n')]
        # iterates through accounts
        # multi-threaded processes
        p = ThreadPool(processes=thread_count)  # creates a pool of workers
        while True:
                try:
                        p.map(start, accounts)  # calls check_proxy with the proxy as parameter
                except:
                        print('Error?!')
                        continue
        p.close()  # closes the multi-threaded processes
