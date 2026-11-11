from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv() #by default looks for .env file

client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)

response = client.embeddings.create(
    model=os.getenv("EMBED_MODEL"),
    input=["I am a good boy", "Python is a good language"]
)
print(len(response.data[0].embedding)) #768
print(len(response.data[1].embedding))

for i, emb in enumerate(response.data):
    print(f"Embedding {i} length: {len(emb.embedding)}")
    print(emb.embedding[:5])
