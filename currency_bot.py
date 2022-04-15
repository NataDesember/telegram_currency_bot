import telebot
import requests
import json

from config import api_key, token_key

base_list_url = 'http://api.exchangeratesapi.io/v1/latest?access_key=' + api_key + '&base=USD'
base_convert_url = 'http://api.exchangeratesapi.io/v1/convert?access_key=' + api_key + '&'


class APIException (Exception):
    def __init__(self, text):
        super()
        self.text = text


class API:

    @staticmethod
    def get_price(base, quote, amount):
        url = base_convert_url + 'from=' + base + '&to=' + quote + '&amount=' + amount
        response = requests.get(url)
        if (response.status_code != 200):
            raise APIException(response.text())
        js = response.json()
        map = json.loads(js)
        if (not map['success']):
            raise APIException(response.text())
        return map['info']['rate']

    @staticmethod
    def get_currencies():
        url = base_list_url
        response = requests.get(url)
        if (response.status_code != 200):
            raise APIException(response.text())
        js = response.json()
        map = json.loads(js)
        if (not map['success']):
            raise APIException(response.text())
        return map['rates']

bot = telebot.TeleBot(token_key, parse_mode=None)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	bot.reply_to(message, "Hey, type (from) (to) (amount) to see currency rates. Example: USD EUR 10")


@bot.message_handler(commands=['values'])
def send_values(message):
    try:
        rates = API.get_currencies()
        ask = ''
        for k, v in rates.items():
            ask = ask + 'USD/' + k + ' = ' + v + '\n'
        bot.reply_to(message, ask)
    except APIException as error:
        bot.reply_to(message, error.text)
        bot.reply_to(message, "The preferred currencies are USD, EUR, and RUB")

@bot.message_handler(func=lambda m: True)
def rate_currency(message):
    (from_cur, to_cur, amount) = message.text.split(' ')
    try:
        rate = API.get_price(from_cur, to_cur, amount)
        bot.reply_to(message, 'Rate is ' + rate)
    except APIException as error:
        bot.reply_to(message, error.text)


bot.infinity_polling()