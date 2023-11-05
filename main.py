import httpx
import random
import string
from unicaps import CaptchaSolver, CaptchaSolvingService
from multiprocessing import Process, Lock
from ProxyMGR import ProxyMGR
import config

MGR = ProxyMGR("proxies.txt")

class webshare():
    def __init__(self, solver: CaptchaSolver, proxy: str, domain_mail: str="gmail.com",
                 user_agent: str="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
                 reCAPTCHA_token: str="6LeHZ6UUAAAAAKat_YS--O2tj_by3gv3r_l03j9d"):
        self.domain_mail = "@" + domain_mail

        self.reCAPTCHA_token = reCAPTCHA_token

        self.client = httpx.Client(headers={'user-agent': user_agent}, proxies=proxy)
        self.solver = solver

    def register(self, password: str=None, email: str=None, recaptcha: str=None):
        if not password:
            password = "".join(random.choices(string.hexdigits, k=10))

        if not email:
            email = "".join(random.choices(string.hexdigits, k=10)) + self.domain_mail

        if not recaptcha:
            print("Решаю капчу...")
            solved = self.solver.solve_recaptcha_v2(
                site_key=self.reCAPTCHA_token,
                page_url='https://proxy.webshare.io',
            )
            print(f"solved!")
            recaptcha = solved.solution.token


        json_data = {
            'email': email,
            'password': password,
            'tos_accepted': True,
            'recaptcha': recaptcha,
        }

        resp = self.client.post('https://proxy.webshare.io/api/v2/register/', json=json_data)
        resp_js = resp.json()
        print(resp_js)
        return resp_js.get('token')

    def get_proxys(self, token: str):
        resp = self.client.get(f'https://proxy.webshare.io/api/v2/proxy/list/?mode=direct', headers={"Authorization": f"Token {token}"})
        resp_js = resp.json()
        return resp_js

def reg_and_get():
    while True:
        c = webshare(solver=CaptchaSolver(CaptchaSolvingService.CAPTCHA_GURU, "21da5a4e9b179e583a715f844b9e221b"), proxy=str(MGR.next_proxy()))
        token = c.register()
        proxys = c.get_proxys(token)

        text = ""
        for proxy in proxys['results']:
            text += f"{proxy['proxy_address']}:{proxy['port']}@{proxy['username']}:{proxy['password']}\n"

        with open("AutoProxy.txt", "r+") as f:
            f.seek(0, 2)
            f.write(text)

if __name__ == '__main__':
    for num in range(config.threads):
        Process(target=reg_and_get).start()
