from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import requests
import dateparser
from datetime import datetime
from datetime import datetime, timedelta


# Ваш API ключ від OpenWeatherMap
API_KEY = "c19b752ad72d6ea846da2c06784a02e3"

class ActionGetCurrentWeather(Action):
    def name(self) -> Text:
        return "action_get_current_weather"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        city = tracker.get_slot("city")
        
        if not city:
            dispatcher.utter_message(text="Будь ласка, вкажіть місто.")
            return []

        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            temp = data["main"]["temp"]
            description = data["weather"][0]["description"]
            message = f"Зараз у {city} температура {temp}°C, стан погоди: {description}."
        else:
            message = f"Вибачте, я не можу знайти поточну погоду для {city}."
        
        dispatcher.utter_message(text=message)
        return [SlotSet("city", None)]  # Очищаємо слот після дії



class ActionGetForecastWeather(Action):
    def name(self):
        return "action_get_forecast_weather"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        # Витягуємо слоти
        city = tracker.get_slot("city")
        date_time = tracker.get_slot("date_time")
        weather_condition = tracker.get_slot("weather_condition")

        # Перевірка наявності міста та дати
        if not city:
            dispatcher.utter_message(text="Please specify a city.")
            return []
        if not date_time:
            dispatcher.utter_message(text="Please specify a date.")
            return []

        # Поточна дата
        today = datetime.now().date()

        # Парсинг дати з date_time
        parsed_date = dateparser.parse(date_time, settings={'PREFER_DATES_FROM': 'future'})
        if not parsed_date:
            dispatcher.utter_message(text="I couldn’t understand the date. Please try again (e.g., 'tomorrow', 'in three days', or '2025.10.23').")
            return []

        target_date = parsed_date.date()
        days_ahead = (target_date - today).days

        # Перевірка, чи дата в майбутньому і в межах доступного прогнозу (5 днів для безкоштовного OpenWeatherMap)
        if days_ahead < 0:
            dispatcher.utter_message(text="I can only provide forecasts for future dates.")
            return []
        if days_ahead > 5:
            dispatcher.utter_message(text="I can only provide forecasts up to 5 days ahead with the current API.")
            return []

        # Запит до API OpenWeatherMap
        api_key = "c19b752ad72d6ea846da2c06784a02e3"  # Замініть на ваш ключ
        url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"
        response = requests.get(url)

        if response.status_code != 200:
            dispatcher.utter_message(text=f"Sorry, I couldn’t find the forecast for {city}.")
            return []

        # Пошук прогнозу для потрібної дати
        forecast_data = response.json()["list"]
        for item in forecast_data:
            item_date = datetime.fromtimestamp(item["dt"]).date()
            if item_date == target_date:
                temp = item["main"]["temp"]
                description = item["weather"][0]["description"].lower()

                # Обробка запиту з конкретною умовою погоди
                if weather_condition:
                    weather_condition = weather_condition.lower()
                    if weather_condition in description:
                        message = f"Yes, it will be {weather_condition} in {city} on {target_date}."
                    else:
                        message = f"No, it won’t be {weather_condition} in {city} on {target_date}. Expect {description} with a temperature of {temp}°C."
                else:
                    message = f"The weather in {city} on {target_date} will be {description} with a temperature of {temp}°C."
                
                dispatcher.utter_message(text=message)
                return []

        dispatcher.utter_message(text=f"Sorry, I couldn’t find a forecast for {city} on {target_date}.")
        return []