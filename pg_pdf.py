import os
import pprint
from openai import OpenAI
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector
from langchain_community.document_loaders import PyPDFLoader
print("1")

load_dotenv()
api_key=os.getenv('OPENROUTER_API_KEY')
db_url=os.getenv('DATABASE_URL')
print("2")

file_path = "./docs/Ayush_Singh_Resume.pdf"
loader = PyPDFLoader(file_path)
print("3")

docs = loader.load()
print("4")

pprint.pp(docs[0].metadata)
print("5")

pprint.pp(docs)
print("6")

# client = OpenAI(
#   base_url="https://openrouter.ai/api/v1",
#   api_key=os.getenv("OPENROUTER_API_KEY"),
# )

# embeddings = OpenAIEmbeddings(
#     model="text-embedding-ada-002",
#     openai_api_base="https://openrouter.ai/api/v1",
#     openai_api_key=os.getenv("OPENROUTER_API_KEY"),
# )

# connection = "postgresql+psycopg://postgres:postgres@localhost:5432/postgres"
# collection_name = "learn-rag"

# vector_store = PGVector(
#     embeddings=embeddings,
#     collection_name=collection_name,
#     connection=connection,
#     use_jsonb=True,
# )

# vector_store.add_documents(docs, ids=[doc.metadata["id"] for doc in docs])
