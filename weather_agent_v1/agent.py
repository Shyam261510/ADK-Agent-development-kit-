from google.adk.agents import Agent
from dotenv import load_dotenv
from google.adk.tools import ToolContext
from google.adk.tools.base_tool import BaseTool
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types
from typing import Optional,Dict,Any

# from pydantic import BaseModel , Field
from sub_tools.farewell_agent import farewell_agent
from sub_tools.greeting_agent import greeting_agent
from sub_tools.context_agent import context_agent

load_dotenv()

# # --- Define Output Schema ---

# class WeatherReportSchema(BaseModel):
#     status: str = Field(description="Indicates request result: 'success' or 'error'")
#     response: str = Field(description="If success → weather report; if error → error message")

# @title Define the get_weather Tool


def get_weather(city: str, tool_context: ToolContext) -> dict:
    """Retrieves weather, converts temp unit based on session state."""
    print(f"--- Tool: get_weather_stateful called for {city} ---")

    # --- Read preference from state ---

    preferred_unit = tool_context.state.get(
        "user_preference_temperature_unit", "Celsius"
    )  # Default to Celsius
    print(
        f"--- Tool: Reading state 'user_preference_temperature_unit': {preferred_unit} ---"
    )

    city_normalized = city.lower().replace(" ", "")

    # Mock weather data (always stored in Celsius internally)
    mock_weather_db = {
        "newyork": {"temp_c": 25, "condition": "sunny"},
        "london": {"temp_c": 15, "condition": "cloudy"},
        "tokyo": {"temp_c": 18, "condition": "light rain"},
    }

    if city_normalized in mock_weather_db:
        data = mock_weather_db[city_normalized]
        temp_c = data["temp_c"]
        condition = data["condition"]

        # Format temperature based on state preference
        if preferred_unit == "Fahrenheit":
            temp_value = (temp_c * 9 / 5) + 32  # Calculate Fahrenheit
            temp_unit = "°F"
        else:  # Default to Celsius
            temp_value = temp_c
            temp_unit = "°C"

        report = f"The weather in {city.capitalize()} is {condition} with a temperature of {temp_value:.0f}{temp_unit}."
        result = {"status": "success", "report": report}
        print(f"--- Tool: Generated report in {preferred_unit}. Result: {result} ---")

        # Example of writing back to state (optional for this tool)
        tool_context.state["last_city_checked_stateful"] = city
        print(f"--- Tool: Updated state 'last_city_checked_stateful': {city} ---")

        return result


def block_keyword_gaurdrail(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """
    Inspects the latest user message for 'BLOCK'. If found, blocks the LLM call
    and returns a predefined LlmResponse. Otherwise, returns None to proceed.
    """


    last_user_message_text = ""

    if llm_request.contents:
        # Find the most recent message with role 'user'
        for content in reversed(llm_request.contents):
            if content.role == "user" and content.parts:
                # Assuming text is in the first part for simplicity
                if content.parts[0].text:
                    last_user_message_text = content.parts[0].text
                    break  # Found the last user message text
    # --- Guardrail Logic ---
    keyword_to_block = "BLOCK"

    if keyword_to_block in last_user_message_text.upper():
        callback_context.state["guardrail_block_keyword_triggered"] = True
        # Construct and return an LlmResponse to stop the flow and send this back instead
        return LlmResponse(
            content=types.Content(
                role="model",  # Mimic a response from the agent's perspective
                parts=[
                    types.Part(
                        text=f"I cannot process this request because it contains the blocked keyword '{keyword_to_block}'."
                    )
                ],
            )
        )
    else:
        return None



def block_paris_tool_guardrail(tool:BaseTool,args:Dict[str,Any], tool_context:ToolContext)-> Optional[dict]:

    """
    Checks if 'get_weather_stateful' is called for 'Paris'.
    If so, blocks the tool execution and returns a specific error dictionary.
    Otherwise, allows the tool call to proceed by returning None.
    """

    tool_name = tool.name

    target_tool_name = "get_weather"

    blocked_city = "paris"

    if tool_name == target_tool_name:
        city_agrument = args.get("city","") # default value "" (empty string)

        if city_agrument and city_agrument.lower() == blocked_city:
            tool_context.state['guardrail_tool_block_triggered'] = True
            # Return a dictionary matching the tool's expected output format for errors
            # This dictionary becomes the tool's result, skipping the actual tool run.
            return {
                "status": "error",
                "error_message": f"Policy restriction: Weather checks for '{city_agrument.capitalize()}' are currently disabled by a tool guardrail."
            }
        
        else:
            return None

weather_agent = Agent(
    name="weather_agent_v1",
    description="The main coordinator agent. Handles weather requests and delegates greetings/farewells to specialists.",
    model="gemini-2.0-flash",
    instruction="""
            You are the main Weather Agent coordinating a team. Your primary responsibility is to provide weather information. "
                    "Use the 'get_weather' tool ONLY for specific weather requests (e.g., 'weather in London'). "
                    "You have specialized sub-agents: "
                    "1. 'greeting_agent': Handles simple greetings like 'Hi', 'Hello'. Delegate to it for these. "
                    "2. 'farewell_agent': Handles simple farewells like 'Bye', 'See you'. Delegate to it for these. "
                    "3. 'context_agent': Give the context of above held conversation like 'How the conversation starts?' , 'What user asks?' , 'How it ends ?'
                    "Analyze the user's query. If it's a greeting, delegate to 'greeting_agent'. If it's a farewell, delegate to 'farewell_agent'. "
                    "If it's a weather request, handle it yourself using 'get_weather'. "
                    "For anything else, respond appropriately or state you cannot handle it."
""",
    tools=[get_weather],
    sub_agents=[greeting_agent, farewell_agent, context_agent],
    before_model_callback=block_keyword_gaurdrail,
    before_tool_callback=block_paris_tool_guardrail
)
