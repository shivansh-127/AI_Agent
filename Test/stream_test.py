import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)

stream = client.chat.completions.create(
    model=os.getenv("MODEL"),
    messages=[{"role": "user", "content": "Explain what an API is in 100 words"}],
    stream=True,
)

full_response = ""

for chunk in stream:
    if not chunk.choices:
        continue

    piece = chunk.choices[0].delta.content
    if piece:
        print(piece, end="", flush=True)   
        full_response += piece

print("\nFull Response")
print(full_response) #I will send this to LLM for history     