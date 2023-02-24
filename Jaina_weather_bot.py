import telebot
from pyowm import OWM


class WeatherBot:
    def __init__(self, token, owm_api_key):
        self.bot = telebot.TeleBot(token)
        self.owm = OWM(owm_api_key)
        self.mgr = self.owm.weather_manager()

    def run(self):
        @self.bot.message_handler(content_types=['text'])
        def get_text_messages(message):
            if message.text == '/weather':
                self.bot.send_message(message.from_user.id, "Введите название города")
                self.bot.register_next_step_handler(message, self.get_weather)
            else:
                self.bot.send_message(message.from_user.id, 'Напиши /weather')

        self.bot.polling(non_stop=True, interval=0)

    def get_weather(self, message):
        city = message.text
        try:
            observation = self.mgr.weather_at_place(city)
            weather = observation.weather
            temperature = weather.temperature("celsius")
            lat, lon = observation.location.lat, observation.location.lon
            location = f"https://yandex.ru/pogoda/maps/nowcast?lat={lat}&lon={lon}&via=hnav&le_Lightning=1"
            self.bot.send_message(
                message.from_user.id,
                f"В городе {city} сейчас {round(temperature['temp'])} градусов, "
                f"но чувствуется как {round(temperature['feels_like'])} градусов",
            )
            self.bot.send_message(message.from_user.id, location)
            self.continue_or_stop(message)
        except Exception:
            self.bot.send_message(message.from_user.id, "Упс такого города нет, попробуйте еще раз")
            self.bot.send_message(message.from_user.id, "Введите название города")
            self.bot.register_next_step_handler(message, self.get_weather)

    def continue_or_stop(self, message):
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(telebot.types.KeyboardButton('Продолжить'), telebot.types.KeyboardButton('Остановиться'))
        self.bot.send_message(
            message.from_user.id,
            "Что Вы хотите сделать дальше?",
            reply_markup=keyboard,
        )
        self.bot.register_next_step_handler(message, self.process_continue_or_stop)

    def process_continue_or_stop(self, message):
        if message.text == 'Продолжить':
            self.bot.send_message(message.from_user.id, "Введите название города")
            self.bot.register_next_step_handler(message, self.get_weather)
        elif message.text == 'Остановиться':
            self.bot.send_message(message.from_user.id, "До новых встреч!")
        else:
            self.bot.send_message(message.from_user.id, "Неизвестная команда")
            self.continue_or_stop(message)
if __name__ == "__main__":
    bot = WeatherBot("6285646632:AAFR-AZg_sUo_LZKurFClv2eenx3F5Vp_EE", "93a1888b6dca6e98a6415a26b4d1a6ff")
    bot.run()