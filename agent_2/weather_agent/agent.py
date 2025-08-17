from google.adk.agents import Agent
import requests


async def fetch_weather_data(location: str):
    url = "https://weather-api167.p.rapidapi.com/api/weather/current"
    querystring = {"place": location, "units": "standard", "lang": "en", "mode": "json"}

    headers = {
        "x-rapidapi-key": "7ba32e98d4mshbc361eccff72622p1e309fjsn7cfa4fbda7cd",
        "x-rapidapi-host": "weather-api167.p.rapidapi.com",
        "Accept": "application/json",
    }
    response = requests.get(url, headers=headers, params=querystring)
    weather_info = response.json()
    weather_summery = weather_info["summery"]
    return {"weather_summery": weather_summery}


root_agent = Agent(
    name="weather_agent",
    description="Weather Agenet",
    model="gemini-2.0-flash",
    instruction="""
You are a helpful weather assistant.

You have following task:
- Extract the location from user message.
- Use the fetch_weather_data tool and pass the location in fetch_weather_data for fetching the weather data of particular location.
""",
    tools=[fetch_weather_data],
)
