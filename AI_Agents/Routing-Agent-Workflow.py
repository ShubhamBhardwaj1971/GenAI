from openai import OpenAI
from dotenv import load_dotenv
import os
import requests

# Load environment variables from .env file
load_dotenv()
# Initialize the client
def openai_tool_call(city: str) -> str:
    """
    Make an OpenAI API call to get weather information for a city and return it as a poem.
    
    Args:
        city (str): Name of the city to get weather for
        
    Returns:
        str: Poetic weather description
    """
    # Initialize the client
    client = OpenAI()

    # Define the available tools
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get the current weather for a specific city",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city name to get weather for"
                        }
                    },
                    "required": ["location"],
                    "additionalProperties": False
                }
            }
        }
    ]

    # Make the API call
    response = client.chat.completions.create(
        model="gpt-4",  # Fixed the model name
        messages=[
            {"role": "system", "content": "You are a helpful weather assistant. Use the weather function to provide accurate weather information."},
            {"role": "user", "content": f"What's the weather like in {city} today?"}
        ],
        tools=tools
    )

    # Handle the response
    if response.choices[0].message.tool_calls:
        tool_call = response.choices[0].message.tool_calls[0]
        function_args = eval(tool_call.function.arguments)
        location = function_args.get('location')
        weather_data = get_weather(location)
        
        messages = [
            {"role": "system", "content": "You are a helpful weather assistant. Use the weather function to provide accurate weather information."},
            {"role": "user", "content": f"What's the weather like in {city} today?"},
            {"role": "assistant", "content": None, "tool_calls": [tool_call]},
            {
                "role": "tool",
                "content": str(weather_data),
                "tool_call_id": tool_call.id
            }
        ]
        
        final_response = client.chat.completions.create(
            model="gpt-4",
            messages=messages
        )
        
        return final_response.choices[0].message.content
    else:
        return response.choices[0].message.content
    
def router_agent(prompt: str) -> str:
    """
    Routes the user input to the appropriate agent and returns their response.
    
    Args:
        prompt (str): The user's input prompt
        
    Returns:
        str: Response from the selected agent
    """
    client = OpenAI()
    
    # First, get routing decision
    routing_response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": """You are a Router Agent. Your only job is to decide which agent should handle the user's request.
            RESPOND WITH ONLY ONE OF THESE THREE WORDS: 'reasoning', 'conversational', or 'weather'.
            
            Use these rules:
            - If the request is about weather, respond with 'weather'
            - If the request requires complex reasoning, math, or coding, respond with 'reasoning'
            - If the request is casual conversation or simple questions, respond with 'conversational'"""},
            {"role": "user", "content": prompt}
        ],
        temperature=0,    # Use 0 for consistent routing
        max_tokens=50     # Short response needed
    )
    
    # Get the routing decision
    route = routing_response.choices[0].message.content.strip().lower()
    
    # Route to appropriate agent and return their response
    if 'weather' in route:
        # Extract city name (you might want to make this more sophisticated)
        return openai_tool_call(prompt)
    elif route == 'reasoning':
        return reasoning_agent(prompt)
    elif route == 'conversational':
        return conversational_agent(prompt)
    else:
        return "Error: Unable to determine appropriate agent for your request."

def reasoning_agent(prompt: str) -> str:
    """The reasoning agent handles complex queries requiring detailed analysis."""
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o",  # Fixed model name from gpt-4o
        messages=[
            {"role": "system", "content": "You are a Reasoning Agent. Provide detailed, analytical responses with step-by-step explanations when appropriate."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def conversational_agent(prompt: str) -> str:
    """The conversational agent handles casual conversation and simple queries."""
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # Changed from gpt-4o-mini to a real model
        messages=[
            {"role": "system", "content": "You are a Conversational Agent. Provide friendly, concise responses in a natural conversational tone."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

print(router_agent("Write a python program to calculate the area of a circle"));