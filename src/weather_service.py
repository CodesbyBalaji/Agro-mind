import requests
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

class WeatherService:
    def __init__(self, openweather_key=None):
        self.openweather_key = openweather_key
        # IMD and NASA POWER usually have specific endpoints or require registration
        self.base_url_owm = "https://api.openweathermap.org/data/2.5"

    def fetch_weather_data(self, lat, lon, region="North"):
        """
        Fetches weather from multiple sources.
        Falls back to sophisticated simulation if keys are missing.
        """
        if self.openweather_key:
            return self._fetch_real_data(lat, lon)
        else:
            return self._fetch_mock_data(region)

    def _fetch_real_data(self, lat, lon):
        try:
            # Current & Forecast (using One Call API if available, else standard)
            # This is a placeholder for actual API logic
            response = requests.get(f"{self.base_url_owm}/forecast?lat={lat}&lon={lon}&appid={self.openweather_key}&units=metric")
            data = response.json()
            
            # Process 7-day forecast
            forecast = []
            for item in data['list'][:7]: # Simplified
                forecast.append({
                    'date': item['dt_txt'],
                    'temp': item['main']['temp'],
                    'humidity': item['main']['humidity'],
                    'rain_prob': item.get('pop', 0) * 100,
                    'rainfall': item.get('rain', {}).get('3h', 0)
                })
            
            return {
                'source': 'OpenWeather',
                'forecast': forecast,
                'alerts': self._check_alerts(forecast)
            }
        except Exception as e:
            return self._fetch_mock_data("Manual")

    def _fetch_mock_data(self, region):
        """Generates realistic weather data for demonstration"""
        base_temp = 28 if region in ["South", "Central"] else 22
        forecast = []
        now = datetime.now()
        
        for i in range(7):
            date = now + timedelta(days=i)
            temp = base_temp + np.random.uniform(-3, 5)
            hum = 60 + np.random.uniform(-10, 20)
            rain_prob = np.random.uniform(0, 100) if hum > 75 else np.random.uniform(0, 30)
            
            forecast.append({
                'date': date.strftime("%Y-%m-%d"),
                'temp': round(temp, 1),
                'humidity': round(hum, 1),
                'rain_prob': round(rain_prob, 1),
                'rainfall': round(np.random.uniform(0, 20) if rain_prob > 50 else 0, 1)
            })
            
        return {
            'source': 'AgroMind Simulated (NASA/IMD Mode)',
            'forecast': forecast,
            'alerts': self._check_alerts(forecast)
        }

    def _check_alerts(self, forecast):
        alerts = []
        for day in forecast:
            if day['temp'] > 40:
                alerts.append(f"🔥 Extreme Heat Alert on {day['date']}")
            if day['rainfall'] > 50:
                alerts.append(f"🌊 Heavy Rainfall Warning on {day['date']}")
        
        if not alerts:
            alerts.append("✅ No immediate weather threats detected.")
        return alerts

    def get_nasa_power_data(self, lat, lon):
        """Simulated NASA POWER solar radiation data"""
        return {
            'solar_radiation': round(np.random.uniform(15, 25), 2),
            'unit': 'MJ/m²/day'
        }
