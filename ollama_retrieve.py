query_prompt = input("Prompt: ")

from ollama_embed import vector_store

def format_docs(docs):
    return "\n".join(doc.page_content for doc in docs)

similar_docs = vector_store.similarity_search(query_prompt)
context = format_docs(similar_docs)

print(context)

# completion = client.chat.completions.create(
#   model="openai/gpt-oss-20b:free",
#   messages=[
#     {
#       "role": "system",
#       "content": "You are a Chat Bot and you have access to all the documentation of the company, you will receive a query prompt and some context, you have to respond on the basis of the context. Keep your responses small under a paragraph or two."
#     },
#     {
#       "role": "user",
#       "content": f"CONTEXT: {context}\n\n\nQUERY: {query_prompt}"
#     }
#   ],
# )


# print(completion.choices[0].message.content)

# for chunk in completion:
#     if not chunk.choices:
#         continue

#     delta = chunk.choices[0].delta

#     if hasattr(delta, "content") and delta.content:
#         print(delta.content, end="", flush=True)

# print()