import dateparser
import requests
from bs4 import BeautifulSoup
from random import choice
import pycountry
from geotext import GeoText
import numpy as np


def get_user_agent():
    user_agents = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.47",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.102 Safari/537.36 OPR/90.0.4480.54",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.53 Safari/537.36 Edg/103.0.1264.37",
        # Mobile user agents
        "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Linux; Android 9; SM-G960U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.181 Mobile Safari/537.36",
        # Tablet user agents
        "Mozilla/5.0 (iPad; CPU OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Linux; Android 10; SM-T510) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
        "Mozilla/5.0 (Android 10; Tablet; SM-T515) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
        # Smart TV user agents
        "Mozilla/5.0 (SMART-TV; X11; Linux x86_64) AppleWebKit/537.42 (KHTML, like Gecko) Safari/537.42",
        "Mozilla/5.0 (Web0S; Linux/SmartTV) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.36 Safari/537.36",
        "Mozilla/5.0 (SMART-TV; Linux; Tizen 4.0) AppleWebkit/605.1.15 (KHTML, like Gecko) SamsungBrowser/8.2 Chrome/63.0.3239.84 Safari/605.1.15",
        # Gaming console user agents
        "Mozilla/5.0 (PlayStation 4 3.11) AppleWebKit/537.73 (KHTML, like Gecko)",
        "Mozilla/5.0 (Nintendo Switch; WiFi) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.1.15384 NintendoBrowser/13.1.1.15383",
        "Mozilla/5.0 (Xbox One; Xbox One OS 10.0.18363.1016; en-US) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36 Edge/44.18363.1016.0",
        # Other browsers
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/86.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
    ]

    return choice(user_agents)


session = requests.Session()


def web_scrape(url, format="text"):
    headers = {
        "User-Agent": get_user_agent(),
    }
    print(url)
    if format == "text":
        return session.get(url, headers=headers).text
    elif format == "json":
        return session.get(url, headers=headers).json()


def get_soup(resp):
    return BeautifulSoup(resp, "html.parser")


def convert_string_to_date(text):
    date = dateparser.parse(text)
    if date:
        return date.strftime("%Y-%m-%d")
    return np.nan


def get_country_name(location):
    try:
        country = pycountry.countries.search_fuzzy(location)
        if country:
            return country[0].name
    except LookupError:
        pass
    return ""


def extract_city_names(text):
    places = GeoText(text)
    return places.cities
