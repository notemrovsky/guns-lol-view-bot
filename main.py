import sys
sys.dont_write_bytecode = True

import random
import string
import threading
import time
import uuid
import os

import json
import curl_cffi
from urllib.parse import urlencode

from utils.pow_solver import PowSolver
from utils.cf_solver import solve_turnstile

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")) as f:
    config = json.load(f)

sent = 0
lock = threading.Lock()


class ViewBot:
    def __init__(self):
        self.session = curl_cffi.requests.Session(impersonate="chrome146")
        self.session.headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'priority': 'u=0, i',
            'sec-ch-ua': '"Google Chrome";v="149", "Chromium";v="149", "Not)A;Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36',
        }

        s = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        proxy = config["proxy"].replace("{s}", s)
        self.session.proxies = {"all": proxy}

    def get_page(self, username):
        return self.session.get(f'https://guns.lol/{username}').text

    def solve_pow(self, html):
        challenge = json.loads(html.split(r'"_gpp_ch\":')[1].split(r',\"success')[0].replace("\\", ""))
        return PowSolver().solve(challenge)

    def send_sa_pixel(self, username):
        page_id = str(uuid.uuid4())
        params = {
            'version': 'custom_latest_11',
            'hostname': 'guns.lol',
            'ua': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36',
            'https': 'true',
            'timezone': 'Europe/Istanbul',
            'page_id': page_id,
            'session_id': str(uuid.uuid4()),
            'sri': 'false',
            'mobile': 'false',
            'brands': json.dumps([{"brand": "Google Chrome", "version": "149"}, {"brand": "Chromium", "version": "149"}, {"brand": "Not)A;Brand", "version": "24"}]),
            'os_name': 'Linux',
            'os_version': '',
            'path': f'/{username}',
            'viewport_width': str(random.randint(900, 1920)),
            'viewport_height': str(random.randint(800, 1080)),
            'language': 'en-US',
            'screen_width': '1920',
            'screen_height': '1080',
            'unique': 'true',
            'id': page_id,
            'type': 'pageview',
            'time': str(int(time.time() * 1000)),
        }
        self.session.headers = {
            'accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'priority': 'u=4, i',
            'referer': f'https://guns.lol/{username}',
            'sec-ch-ua': '"Google Chrome";v="149", "Chromium";v="149", "Not)A;Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
            'sec-fetch-dest': 'image',
            'sec-fetch-mode': 'no-cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36',
        }
        self.session.get(f'https://sa.guns.lol/simple.gif?{urlencode(params)}')

    def send_view(self, username):
        html = self.get_page(username)
        pow_solution = self.solve_pow(html)
        self.send_sa_pixel(username)
        turnstile_token = solve_turnstile()
        time.sleep(5)

        self.session.headers = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'no-cache',
            'content-type': 'text/plain;charset=UTF-8',
            'origin': 'https://guns.lol',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': f'https://guns.lol/{username}',
            'sec-ch-ua': '"Google Chrome";v="149", "Chromium";v="149", "Not)A;Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36',
        }

        data = json.dumps({"_t": turnstile_token, "_gpp_ch": pow_solution, "username": username, "deviceType": "desktop", "event": "view", "linkId": None, "referrer": ""}, separators=(",", ":"))
        response = self.session.post('https://guns.lol/api/analytics/record', data=data)
        print(f"{response.status_code} {response.text}")


def run_threads():
    global sent
    while True:
        with lock:
            if sent >= config["views"]:
                return
            sent += 1
            current = sent
        try:
            ViewBot().send_view(config["username"])
        except Exception as E:
            print(f"[{current}] error: {E}")


if __name__ == "__main__":
    print(f'target: {config["views"]} views for {config["username"]} with {config["threads"]} threads')
    threads = []
    for _ in range(config["threads"]):
        t = threading.Thread(target=run_threads)
        t.start()
        threads.append(t)
        time.sleep(config["sleep"])
    for t in threads:
        t.join()
    print("done")
