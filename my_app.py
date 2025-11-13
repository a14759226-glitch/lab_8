from models import Users
from models import Currencies_List
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs
from jinja2 import Environment, PackageLoader, select_autoescape

env = Environment(
    loader=PackageLoader("my_app"),
    autoescape=select_autoescape()
)

import requests
import sys


def get_currencies(currency_codes: list, url: str = "https://www.cbr-xml-daily.ru/daily_json.js",
                   handle=sys.stdout) -> dict:
    """
    Получает курсы валют с API Центробанка России.

    Args:
        currency_codes (list): Список символьных кодов валют (например, ['USD', 'EUR']).

    Returns:
        dict: Словарь, где ключи - символьные коды валют, а значения - их курсы.
              Возвращает None в случае ошибки запроса.
    """
    try:

        response = requests.get(url)

        response.raise_for_status()  # Проверка на ошибки HTTP
        data = response.json()

        currencies = {}

        if "Valute" in data:
            for code in currency_codes:
                if code in data["Valute"]:
                    currencies[code] = data["Valute"][code]["Value"]
                else:
                    currencies[code] = f"Код валюты '{code}' не найден."
        return currencies

    except requests.exceptions.RequestException as e:
        # print(f"Ошибка при запросе к API: {e}", file=handle)
        handle.write(f"Ошибка при запросе к API: {e}")
        # raise ValueError('Упали с исключением')
        raise requests.exceptions.RequestException('Упали с исключением')


current_user = None
all_currencies_list = Currencies_List(
    'AUD', 'AZN', 'GBP', 'AMD', 'BYN', 'BGN', 'BRL', 'HUF', 'HKD', 'DKK',
    'USD', 'EUR', 'INR', 'KZT', 'CAD', 'KGS', 'CNY', 'MDL', 'NOK', 'PLN',
    'RON', 'XDR', 'SGD', 'TJS', 'TRY', 'TMT', 'UZS', 'UAH', 'CZK', 'SEK',
    'CHF', 'ZAR', 'KRW', 'JPY'
)


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == '/':
            self.show_register_page()
        elif self.path == '/currencies':
            self.show_currencies_page()
        elif self.path == '/subscriptions':
            self.show_subscriptions_page()
        else:
            self.send_error(404)

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        data = parse_qs(post_data)

        if self.path == '/':
            self.handle_register(data)
        elif self.path == '/currencies':
            self.handle_currencies(data)
        elif self.path == '/remove_subscription':
            self.handle_remove_subscription(data)

    def show_register_page(self, registered=False):
        template = env.get_template("register.html")
        html = template.render(registered=registered)
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())

    def show_currencies_page(self, saved=False):
        global current_user

        selected_currencies = []
        if current_user and hasattr(current_user, 'subscriptions'):
            selected_currencies = current_user.subscriptions

        template = env.get_template("currencies.html")
        html = template.render(
            available_currencies=all_currencies_list.id,
            selected_currencies=selected_currencies,
            saved=saved
        )
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())

    def show_subscriptions_page(self):
        global current_user

        user_currencies = []
        current_rates = {}

        if current_user and hasattr(current_user, 'subscriptions'):
            user_currencies = current_user.subscriptions
            current_rates = get_currencies(user_currencies)

        template = env.get_template("subscriptions.html")
        html = template.render(
            user=current_user,
            user_currencies=user_currencies,
            current_rates=current_rates
        )
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())

    def handle_register(self, data):
        global current_user

        name = data.get('name', [''])[0]
        age = int(data.get('age', [0])[0])
        email = data.get('email', [''])[0]

        current_user = Users(name, age, email)
        current_user.subscriptions = []

        self.show_register_page(registered=True)

    def handle_currencies(self, data):
        global current_user

        selected_currencies = data.get('currencies', [])
        current_user.subscriptions = selected_currencies
        self.show_currencies_page(saved=True)

    def handle_remove_subscription(self, data):
        global current_user

        currency_to_remove = data.get('currency', [''])[0]
        if currency_to_remove in current_user.subscriptions:
            current_user.subscriptions.remove(currency_to_remove)

        self.show_subscriptions_page()


httpd = HTTPServer(('localhost', 8080), SimpleHTTPRequestHandler)
print('server is running')
httpd.serve_forever()
