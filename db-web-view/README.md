# View your Database here

Edit config at ./drizzle.config.ts

```ts
import { defineConfig } from "drizzle-kit"; 

export default defineConfig({
    schema: "./schema/*",
    out: "./drizzle",
    dialect: 'postgresql',
    dbCredentials: {
        url: process.env.DB_URL || process.env.DATABASE_URL,
    }
});
```
### For my current RAG Setup 

```ts
DATABASE_URL = postgresql+psycopg://postgres:postgres@localhost:5432/postgres
```

### How to view tables and execute SQL queries?

```bash
cd db-web-view
bun install
bunx drizzle-kit studio
```

Then open Chromium browser and open [local.drizzle.studio](local.drizzle.studio)