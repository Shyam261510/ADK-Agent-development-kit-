from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from agent import weather_agent
import asyncio
from uuid import uuid4
from google.genai import types


async def call_agent_async(query: str, runner, user_id, session_id):
    """Sends a query to the agent and prints the final response."""

    print(f"\n>>> User Query: {query}")

    # Prepare the user's message in ADK format

    content = types.Content(role="user", parts=[types.Part(text=query)])

    final_response_text = "Agent did not produce a final response."  # Default

    # Key Concept: run_async executes the agent logic and yields Events.
    # We iterate through events to find the final answer

    async for event in runner.run_async(
        user_id=user_id, session_id=session_id, new_message=content
    ):
        # You can uncomment the line below to see *all* events during execution
        # print(f"  [Event] Author: {event.author}, Type: {type(event).__name__}, Final: {event.is_final_response()}, Content: {event.content}")

        # Key Concept: is_final_response() marks the concluding message for the turn.

        if event.is_final_response():
            if event.content and event.content.parts:

                for part in event.content.parts:
                    if hasattr(part, "text") and part.text:
                        final_response_text = part.text

                    elif hasattr(part, "function_call") and part.function_call:
                        final_response_text = part.function_call

            elif event.actions and event.actions.escalate:
                final_response_text = (
                    f"Agent escalated: {event.error_message or 'No specific message.'}"
                )
            break

    print(f"<<< Agent Response: {final_response_text}")


async def main_async():
    session_service = InMemorySessionService()

    APP_NAME = "weather_tutorial_app"

    USER_ID = "user_1"

    SESSION_ID = uuid4().__str__()

        # Define initial state data - user prefers Celsius initially
    initial_state = {
        "user_preference_temperature_unit": "Celsius"
    }

    session = session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID,state=initial_state
    )


    # --- Runner ---
    # Key Concept: Runner orchestrates the agent execution loop.
    runner = Runner(
        agent=weather_agent,  # The agent we want to run
        app_name=APP_NAME,  # Associates runs with our app
        session_service=session_service,
        
        
            )

    print(
        f"Session created: App='{APP_NAME}', User='{USER_ID}', Session='{SESSION_ID}'"
    )

    print(f"Runner created for agent '{runner.agent.name}'.")

    while True:
        user_input = input("You: ")      

            # 2. Manually update state preference to Fahrenheit - DIRECTLY MODIFY STORAGE
        print("\n--- Manually Updating State: Setting unit to Fahrenheit ---")
            
                # Access the internal storage directly - THIS IS SPECIFIC TO InMemorySessionService for testing
                # NOTE: In production with persistent services (Database, VertexAI), you would
                # typically update state via agent actions or specific service APIs if available,
                # not by direct manipulation of internal storage.
        stored_session = session_service.sessions[APP_NAME][USER_ID][SESSION_ID]
        stored_session.state['user_preference_temperature_unit'] = 'Fahrenheit'
  
        
         # Call the agent first
        await call_agent_async(
            query=user_input, runner=runner, user_id=USER_ID, session_id=SESSION_ID
        )
        
        
        # If user wants to quit, break after calling
        if user_input.lower() in ["byy", "quit"]:
            print("👋 Exiting chat...")
            break


if __name__ == "__main__":
    asyncio.run(main_async())
