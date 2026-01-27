import os
import uuid
import pprint
from dotenv import load_dotenv
from langchain_postgres import PGVector
from langchain_community.document_loaders import PyPDFLoader
from langchain_ollama import OllamaEmbeddings

load_dotenv()
db_url=os.getenv('DATABASE_URL')

# file_path = "./docs/postgresql-18-A4.pdf"
# file_path = "./docs/Ayush_Singh_Resume.pdf"
file_path = "./docs/sample-report.pdf"
loader = PyPDFLoader(file_path, mode="page")

docs = loader.load()


collection_name = "postgresql-18-docs"

embeddings = OllamaEmbeddings(model="nomic-embed-text:v1.5")

vector_store = PGVector(
    embeddings=embeddings,
    collection_name=collection_name,
    connection=db_url,
    use_jsonb=True,
)

uuid_ids = [str(uuid.uuid4()) for _ in range(len(docs))]
vector_store.add_documents(docs, ids=uuid_ids)

print("Task Completed")