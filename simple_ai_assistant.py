# standard library imports
import os

# Third-party imports

from openai import OpenAI
from dotenv import load_dotenv

# Local modules
from tools import TOOLS, run_tool
from Utilities.utilities import log

load_dotenv() #by default looks for .env file

client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)

messages = []

# Safety limit: The max number of model rounds fro ONE user question
MAX_STEPS = 5

messages.append(
    {
        "role": "system",
        "content": (
                     "You are a helpful, humble assistant ."
                     "Answer general questions (programming, science, advice) from your own knowledge. "
                     "Use a tool ONLY when the user asks for the current time, the weather, or their city. "
                     "Keep answers under 100 words."
                   ),
    }
)

def stream_chat(history):
    stream = client.chat.completions.create(
    model=os.getenv("MODEL"),
    messages=history,
    tools=TOOLS,
    stream=True,
)

full_response = ""
calls = {}
label_printed = fals

def build_tool_calls_payload(tool_calls):
    """
    Converts our collected tool calls into the dict format
    that the API expects inside an assistant message.
    """

    payload = []
    for tool_call in tool_calls:
        tool_call_dict = {
            "id": tool_call.id,
            "type": "function",
            "function": {
                "name": tool_call.fucntion.name,
                "arguments": tool_call.function.arguments,
            },
        }
        payload.append(tool_call_dict)

    return payload

while True:

    user_input = input("\nShivansh:")

    if user_input.lower() in ["exit", "quit", "bye", "goodbye"]:
        break

    messages.append(
         {
             "role": "user",
             "content": user_input
         }
    )

    #Chained Tool Calling
    for step in range(MAX_STEPS):

        full_response, tool_calls = stream_chat(messages)
        
       # msg = response.choices[0].message

        if not tool_calls:
            break

        log(f"Step {step + 1}: model requested {len(tool_calls)} tool calls")

        messages.append({
            "role": "assistant",
            "content": full_response,
            "tool_calls": build_tool_calls_payload(tool_calls)
        })


        for tool_call in tool_calls:
            result = run_tool(tool_call)
            messages.append({
                "role" : "tool",
                "tool_id" : tool_call.id,
                "content" : str(result),
            })

    else:
        #In Python, else after a for loop runs only if the loop finishes normally, meaning it wasn't ended early by a break
         fallback = "Sorry, I could not finish this within the step limit."
         messages.append({
             "role" : "assistant",
             "content" : "fallback"
         })
         print("Assistant: " + fallback)
         continue
        
    messages.append({
        "role" : "assistant",
        "content" : msg.content
    })

    print("Assistance: " + (msg.content or ""))
             