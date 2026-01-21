import os

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=os.getenv('OPENROUTER_API_KEY'),
)

query_prompt = input("Prompt: ")

completion = client.chat.completions.create(
  model="openai/gpt-oss-20b:free",
  messages=[
    {
      "role": "system",
      "content": "You are a Chat Bot and you have access to all the documentation of the company, you will receive a query prompt and some context, you have to respond on the basis of the context. Keep your responses small under a paragraph or two."
    },
    {
      "role": "user",
      "content": query_prompt
    }
  ],
  stream=True
)

# print(completion.choices[0].message.content)

for chunk in completion:
    if not chunk.choices:
        continue

    delta = chunk.choices[0].delta

    if hasattr(delta, "content") and delta.content:
        print(delta.content, end="", flush=True)

print()