from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import requests
import dateparser
from datetime import datetime, timedelta
from config import API_KEY

WEATHER_EMOJIS = {
    "clear sky": "☀️",
    "few clouds": "🌤️",
    "scattered clouds": "⛅",
    "broken clouds": "☁️",
    "overcast clouds": "☁️",
    "shower rain": "🌧️",
    "rain": "🌧️",
    "thunderstorm": "⛈️",
    "snow": "❄️",
    "mist": "🌫️",
    "fog": "🌫️",
}

class ActionGetCurrentWeather(Action):
    def name(self) -> Text:
        return "action_get_current_weather"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        city = tracker.get_slot("city")
        if not city:
            dispatcher.utter_message(text="Please specify the city.")
            return []

        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            temp = round(data["main"]["temp"])
            description = data["weather"][0]["description"].lower()
            emoji = WEATHER_EMOJIS.get(description, "🌍")
            message = f"🌆 Now in {city}: {emoji} {description}, 🌡️ {temp}°C"
        else:
            message = f"❌ Sorry, I can't find the current weather for {city}."
        
        dispatcher.utter_message(text=message)
        return [SlotSet("city", None)]

class ActionGetForecastWeather(Action):
    def name(self):
        return "action_get_forecast_weather"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        city = tracker.get_slot("city")
        weather_condition = tracker.get_slot("weather_condition")

        if not city:
            dispatcher.utter_message(text="Please specify a city.")
            return []

        # Отримуємо всі сутності date_time
        date_time_entities = [entity["value"] for entity in tracker.latest_message["entities"] if entity["entity"] == "date_time"]
        date_time = " ".join(date_time_entities) if date_time_entities else tracker.get_slot("date_time")
        
        if not date_time:
            dispatcher.utter_message(text="Please specify a date.")
            return []

        today = datetime.now().date()
        print(f"Today: {today}, date_time: {date_time}")  # Дебагінг

        if "day after tomorrow" in date_time.lower():
            target_date = today + timedelta(days=2)
        else:
            parsed_date = dateparser.parse(
                date_time,
                settings={'PREFER_DATES_FROM': 'future', 'DATE_ORDER': 'DMY'}
            )
            if not parsed_date:
                try:
                    normalized_date = date_time.replace('/', '.')
                    parsed_date = datetime.strptime(normalized_date, "%Y.%m.%d")
                except ValueError:
                    try:
                        parsed_date = datetime.strptime(normalized_date, "%d.%m.%Y")
                    except ValueError:
                        dispatcher.utter_message(text="❓ I couldn’t understand the date. Please try again (e.g., 'tomorrow', '23 February 2025', or '2025.02.23').")
                        return []
            
            target_date = parsed_date.date()
            if target_date < today:
                target_date = target_date.replace(year=today.year)

        days_ahead = (target_date - today).days
        print(f"Target date: {target_date}, Days ahead: {days_ahead}")  # Дебагінг

        if days_ahead < 0:
            dispatcher.utter_message(text="⏳ I can only provide forecasts for future dates.")
            return []
        if days_ahead > 5:
            dispatcher.utter_message(text="⏰ I can only provide forecasts up to 5 days ahead with the current API.")
            return []

        url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
        response = requests.get(url)

        if response.status_code != 200:
            dispatcher.utter_message(text=f"❌ Sorry, I couldn’t find the forecast for {city}.")
            return []

        forecast_data = response.json()["list"]
        for item in forecast_data:
            item_date = datetime.fromtimestamp(item["dt"]).date()
            if item_date == target_date:
                temp = round(item["main"]["temp"])
                description = item["weather"][0]["description"].lower()
                emoji = WEATHER_EMOJIS.get(description, "🌍")
                formatted_date = target_date.strftime("%B %d, %Y")

                if weather_condition:
                    weather_condition = weather_condition.lower()
                    if weather_condition in description:
                        message = f"✅ Yes, it will be {weather_condition} in {city} on {formatted_date}. {emoji} {description}, 🌡️ {temp}°C"
                    else:
                        message = f"❌ No, it won’t be {weather_condition} in {city} on {formatted_date}. Expect {emoji} {description}, 🌡️ {temp}°C"
                else:
                    message = f"🌆 Weather in {city} on {formatted_date}: {emoji} {description}, 🌡️ {temp}°C"
                
                dispatcher.utter_message(text=message)
                return [SlotSet("city", None)]

        dispatcher.utter_message(text=f"❌ Sorry, I couldn’t find a forecast for {city} on {target_date}.")
        return [SlotSet("city", None)]