# core/network.py
import requests

class NetworkUtils:
    def __init__(self):
        self.proxies = []

    def fetch_proxies(self):
        self.proxies = []
        try:
            res = requests.get(
                "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
                timeout=10
            )
            lines = [p.strip() for p in res.text.splitlines() if p.strip()]
            self.proxies = [p for p in lines if ":" in p][:20]
        except:
            self.proxies = []