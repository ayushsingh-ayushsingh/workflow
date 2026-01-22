from pg_embed import vector_store

results = vector_store.similarity_search(
    "exhibition in library"
)
for doc in results:
    print(f"* {doc.page_content} [{doc.metadata}]")