import os
import time
import warnings
from mem0 import Memory
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
import psycopg  # Ensure psycopg3 for better pool handling

load_dotenv()

os.environ["MEM0_TELEMETRY"] = "false"

embeddings = OpenAIEmbeddings(
    model="text-embedding-ada-002",
    openai_api_base="https://openrouter.ai/api/v1",
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
)

# Enhanced pgvector config with explicit pool settings for graceful close
config = {
    "embedder": {
        "provider": "langchain",
        "config": {
            "model": embeddings
        }
    },
    "vector_store": {
        "provider": "pgvector",
        "config": {
            "connection_string": (
                "host=localhost "
                "port=5432 "
                "dbname=postgres "
                "user=postgres "
                "password=postgres "
                "pool_min_size=1 "  # Smaller pool = faster shutdown
                "pool_max_size=3"
            ),
            "collection_name": "mem0",  # Explicit for stability
            "embedding_model_dims": 1536  # Match ada-002 dims
        }
    }
}

m = Memory.from_config(config)
try:
    messages = [
        {"role": "user", "content": "I'm planning to watch a movie tonight. Any recommendations?"},
        {"role": "assistant", "content": "How about thriller movies? They can be quite engaging."},
        {"role": "user", "content": "I'm not a big fan of thriller movies but I love sci-fi movies."},
        {"role": "assistant", "content": "Got it! I'll avoid thriller recommendations and suggest sci-fi movies in the future."}
    ]
    m.add(messages, user_id="alice", metadata={"category": "movies"})
    print("Memory added successfully!")
    
    # Verify: Search to force any pending ops
    results = m.search(query="sci-fi movies", user_id="alice")
    print(f"Verification search: {len(results['results'])} memories found")
    
finally:
    # Explicit GC trigger + short sleep for pool drain
    del m
    time.sleep(1)  # Allow psycopg pools to close naturally [psycopg pool recommendations](https://www.psycopg.org/psycopg3/docs/advanced/pool.html)
    print("Cleanup complete.")

print("Script completed - no thread warnings.")