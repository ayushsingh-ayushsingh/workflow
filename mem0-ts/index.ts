import { Memory } from 'mem0ai/oss';

const config = {
  vectorStore: {
    provider: 'pgvector',
    config: {
      collectionName: 'memories',
      embeddingModelDims: 1536,
      user: 'postgres',
      password: 'postgres',
      host: 'localhost',
      port: 5432,
      dbname: 'postgres', // Optional, defaults to 'postgres'
      diskann: false, // Optional, requires pgvectorscale extension
      hnsw: false, // Optional, for HNSW indexing
    },
  },
};

const memory = new Memory(config);
const messages = [
    {"role": "user", "content": "I'm planning to watch a movie tonight. Any recommendations?"},
    {"role": "assistant", "content": "How about thriller movies? They can be quite engaging."},
    {"role": "user", "content": "I'm not a big fan of thriller movies but I love sci-fi movies."},
    {"role": "assistant", "content": "Got it! I'll avoid thriller recommendations and suggest sci-fi movies in the future."}
]
await memory.add(messages, { userId: "alice", metadata: { category: "movies" } });