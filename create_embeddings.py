import os
import bs4

from openai import OpenAI
from langchain_chroma import Chroma
from dotenv import load_dotenv
# from langchain_community.document_loaders import WebBaseLoader
# from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings

load_dotenv()
api_key=os.getenv('OPENROUTER_API_KEY')

# bs4_strainer = bs4.SoupStrainer(class_=("post-title", "post-header", "post-content"))
# loader = WebBaseLoader(
#     web_paths=("https://lilianweng.github.io/posts/2023-06-23-agent/",),
#     bs_kwargs={"parse_only": bs4_strainer},
# )

# docs = loader.load()

# text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
# splits = text_splitter.split_documents(docs)

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=os.getenv("OPENROUTER_API_KEY"),
)

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

# vector_store.add_documents(splits)
# print(vector_store._collection.count())
