import requests
import json
import telebot
from config import keys, TOKEN


bot = telebot.TeleBot(TOKEN)


class ConvertionException(Exception):
    pass

class GetPrice:

    @bot.message_handler(commands=['start', 'help'])
    def help(message: telebot.types.Message):
        text = 'Чтобы начать работу, введите комманду боту в следующем формате: \n <Имя валюты, цену которой он хочет узнать>' \
               ' <Имя котируемой валюты>' \
               ' <Кол-во переводимой валюты>\n Чтобы увидеть список всех валют: /values'
        bot.reply_to(message, text)

    @bot.message_handler(commands=['values'])
    def values(message: telebot.types.Message):
        text = 'Доступные валюты:'
        for key in keys.keys():
            text = '\n'.join((text, key,))
        bot.reply_to(message, text)

    @bot.message_handler(content_types=['text', ])
    def converter(message: telebot.types.Message):
        values = message.text.split(' ')

        try:
            if len(values) != 3:
                raise ConvertionException('Слишком много параметров')

            quote, base, amount = values
            total_base = CryptoConverter.convert(quote, base, amount)
        except ConvertionException as e:
            bot.reply_to(message, f'Ошибка пользователя.\n{e}')
        except Exception as e:
            bot.reply_to(message, f'Не удалось обработать команду\n{e}')
        else:
            text = f'Цена {amount} {quote} в {base} - {total_base}'
            bot.send_message(message.chat.id, text)

class CryptoConverter:
    @staticmethod

    def convert(quote: str, base: str, amount: str):
        if quote == base:
            raise ConvertionException(f'Невозможно перевести одинаковые валюты {quote}')
        try:
            quote_ticker = keys[quote]
        except KeyError:
            raise ConvertionException(f'Не удалось обработать валюту {quote}')

        try:
            base_ticker = keys[base]
        except KeyError:
            raise ConvertionException(f'Не удалось обработать валюту {base}')

        try:
            amount = float(amount)
        except ValueError:
            raise ConvertionException(f'Не удалось обработать количество {amount}')

        r = requests.get(f'https://min-api.cryptocompare.com/data/price?fsym={quote_ticker}&tsyms={base_ticker}')
        total_base = json.loads(r.content)[keys[base]]

        if amount > 1:
            total_base *= float(amount)

        return total_base


bot.polling()
