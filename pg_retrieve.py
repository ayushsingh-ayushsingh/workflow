import os

from openai import OpenAI
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector

load_dotenv()

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=os.getenv("OPENROUTER_API_KEY"),
)

embeddings = OpenAIEmbeddings(
    model="text-embedding-ada-002",
    openai_api_base="https://openrouter.ai/api/v1",
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
)

connection = os.getenv("DATABASE_URL")
collection_name = "mem0"

vector_store = PGVector(
    embeddings=embeddings,
    collection_name=collection_name,
    connection=connection,
    use_jsonb=True,
)


def format_docs(docs):
    return "\n\n\n".join(doc.page_content for doc in docs)

query_prompt = input("Prompt: ")

similar_docs = vector_store.similarity_search(query_prompt)
context = format_docs(similar_docs)

print("\n\n\n")
print(context)
print("\n\n\n")

completion = client.chat.completions.create(
  model="openai/gpt-oss-20b:free",
  messages=[
    {
      "role": "system",
      "content": "You are a Chat Bot and you have access to Mem0 research paper, you will receive a query prompt and some context, you have to respond on the basis of the context. Keep your responses small under a paragraph or two."
    },
    {
      "role": "user",
      "content": f"CONTEXT: {context}\n\n\nQUERY: {query_prompt}"
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