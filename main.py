import telebot
import requests
import json

Token = '6152442103:AAEZpbEXOp88sgwB-fuYSWMH_hBFzPqok08'


bot = telebot.TeleBot(Token)

keys = {
    'биткоин': 'BTC',
    'доллар': 'USD',
    'евро': 'EUR',
    'юань': 'CNY',
}


# Исключния для отлова ошибок
class ConvertionException(Exception):
    pass

# Создаем новый класс
# Записываем один статический метод, который будет конвертировать валюты
class CryptoConverter:
    @staticmethod
    def convert(quote: str, base: str, amount: str):

        if quote == base:
            raise ConvertionException(f'Невозможно перевести одинаковые валюты {base}.')

        # Ловим ошибки неправильного ввода пользователем
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


# Обработчик вывода инструкции
@bot.message_handler(commands=['start', 'help'])
def echo_test(message: telebot.types.Message):
    text = 'Чтобы начать работу введите комманду боту в следующем формате:\n<имя валюты> \
<в какую валюту перести> \
<количество переводимой валюты> \nУвидеть список всех доступных валют: /values'
    bot.reply_to(message, text)

# Обработчик получения валют
@bot.message_handler(commands=['values'])
def values(message: telebot.types.Message):
    text = 'Доступные валюты: '
    for key in keys.keys():
       text =  '\n'.join((text, key, ))
    bot.reply_to(message, text)
# bot.polling()


# Конвертация валют
@bot.message_handler(content_types=['text', ])
def convert(message: telebot.types.Message):
    try:
        values = message.text.split(' ')

        if len(values) != 3:
            raise ConvertionException('Слишком много параметров.')
        # биткоин доллар 1
        quote, base, amount = values
        total_base = CryptoConverter.convert(quote, base, amount)
    except ConvertionException as e:
        bot.reply_to(message, f'Ошибка пользователя.\n{e}')
    except Exception as e:
        bot.reply_to(message, f'Не удалось отработать команду \n{e}')

    if quote == base:
        raise ConvertionException(f'Невозможно перевести одинаковые валюты {base}.')

    # Ловим ошибки неправильного ввода пользователем
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
    quote_ticker, base_ticker = keys[quote], keys[base]
    text = f'Цена {amount} {quote} в {base} - {total_base}'
    # Проверка бота на работоспособность
    bot.send_message(message.chat.id, text)
    return total_base

bot.polling()