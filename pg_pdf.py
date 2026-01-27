import os
import uuid
import pprint
from openai import OpenAI
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector
from langchain_community.document_loaders import PyPDFLoader

load_dotenv()
api_key=os.getenv('OPENROUTER_API_KEY')
db_url=os.getenv('DATABASE_URL')

file_path = "./docs/mem0.pdf"
loader = PyPDFLoader(file_path)

docs = loader.load()

pprint.pp(docs[0].metadata)

pprint.pp(docs)

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=os.getenv("OPENROUTER_API_KEY"),
)

embeddings = OpenAIEmbeddings(
    model="text-embedding-ada-002",
    openai_api_base="https://openrouter.ai/api/v1",
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
)

connection = "postgresql+psycopg://postgres:postgres@localhost:5432/postgres"
collection_name = "mem0"

vector_store = PGVector(
    embeddings=embeddings,
    collection_name=collection_name,
    connection=connection,
    use_jsonb=True,
)

uuid_ids = [str(uuid.uuid4()) for _ in range(len(docs))]
vector_store.add_documents(docs, ids=uuid_ids)