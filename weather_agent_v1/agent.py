from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm 
from dotenv import load_dotenv
from pydantic import BaseModel , Field

load_dotenv()

# --- Define Output Schema ---

class WeatherReportSchema(BaseModel):
    status: str = Field(description="Indicates request result: 'success' or 'error'")
    response: str = Field(description="If success → weather report; if error → error message")

# @title Define the get_weather Tool

def get_weather(city:str)-> dict:
    """
    Retrives the current weather data for user specified city.

    Args: city:str -> The name of the city ( e.g "New York" , "Landon" , "Tokoyo" )

    return dict -> Dictonary which conatin the following information.

                - "status" key which can be ( error or success ).
                - If "status" key value is success then it includes "report" key which contain the actual weather data
                - If "status" key value is error then it includes "error_message" key which contain error message.
      """
    print(f"--- Tool: get_weather called for city: {city} ---")

    city_normalized = city.lower().replace(" ", "")

    # Mock weather data
    mock_weather_db = {
        "newyork": {"status": "success", "report": "The weather in New York is sunny with a temperature of 25°C."},
        "london": {"status": "success", "report": "It's cloudy in London with a temperature of 15°C."},
        "tokyo": {"status": "success", "report": "Tokyo is experiencing light rain and a temperature of 18°C."},
    }

    if city_normalized in mock_weather_db:
        return mock_weather_db[city_normalized]
    else:
        return {"status": "error", "error_message": f"Sorry, I don't have weather information for '{city}'."}
    


weather_agent = Agent(
    name="weather_agent_v1",
    description="Weather Assistant",
    model="gemini-2.0-flash",
    instruction="""
    You are a helpful weather assistant how gives the weather report based on the user specified city.
    - Extract the city name from the user request.
    - Use the get_weather tool and pass the city name to the tool
        example ( User : What is the weather of London city or london here city is London or london)
    - If tool return error then give polite response
    - If tool doesn't give error then return the weather report which the user request's.
""",
tools=[get_weather],
output_schema=WeatherReportSchema,
output_key="weather_report"
)

