import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

load_dotenv()

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# Reload vector store (NO embedding here)
embeddings = OpenAIEmbeddings(
    model="text-embedding-ada-002",
    openai_api_base="https://openrouter.ai/api/v1",
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
)

vector_store = Chroma(
    collection_name="learn-rag",
    embedding_function=embeddings,
    persist_directory="./chroma_langchain_db",
)

query_prompt = "What is an autonomous agent?"

results = vector_store.similarity_search_with_score(
    query_prompt,
)

# High-accuracy filtering
HIGH_ACCURACY_DISTANCE = 0.1  # cosine distance

filtered_docs = [
    doc for doc, distance in results
    if distance <= HIGH_ACCURACY_DISTANCE
]

context = format_docs(filtered_docs)

print("Context:\n")
print(context)