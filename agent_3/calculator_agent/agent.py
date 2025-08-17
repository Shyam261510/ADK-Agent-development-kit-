from google.adk.agents import Agent

OPERATIONS = {
    "sum": ["sum", "add", "addition", "plus"],
    "subtract": ["subtract", "minus", "subtraction"],
    "multiply": ["multiply", "times", "multiplication"],
    "divide": ["divide", "division"],
    "percentage": ["percentage", "percent"],
}


def normalize_operation(op: str) -> str:
    op = op.lower()
    for key, keywords in OPERATIONS.items():
        if op in keywords:
            return key
    return None


def calculate(operation: str, number1: int, number2: int) -> dict:
    """
    Perform calculations based on the given operation.
    Supported: sum, subtract, multiply, divide, percentage
    """
    op = normalize_operation(operation)
    if not op:
        return {"error": f"Unsupported operation: {operation}"}

    try:
        if op == "sum":
            result = number1 + number2
        elif op == "subtract":
            result = number1 - number2
        elif op == "multiply":
            result = number1 * number2
        elif op == "divide":
            if number2 == 0:
                return {"error": "Division by zero is not allowed"}
            result = number1 / number2
        elif op == "percentage":
            result = (number1 * number2) / 100
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}


root_agent = Agent(
    name="calculator_agent",
    description="An AI assistant that performs basic math calculations.",
    model="gemini-2.0-flash",
    instruction="""
    You are a helpful calculator agent that performs basic mathematical operations.
    Always follow these steps:

    1. Extract the operation, number1, and number2 from the user's request.  
       Example:  
       User: "What is the addition of 3 and 5?"  
       → operation = "sum", number1 = 3, number2 = 5  

    2. Call the `calculate` tool with these parameters.  

    3. If the tool returns "error", politely explain the issue to the user.  

    4. Otherwise, provide the result in a clear and friendly way.  
       Example: "The result of adding 3 and 5 is 8 ✅"  

    Keep responses short, clear, and user-friendly.
    """,
    tools=[calculate],
)
