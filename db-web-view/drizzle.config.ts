import { defineConfig } from "drizzle-kit";

// Edit your config here...

// postgresql://[username[:password]@][host][:port][/database][?param1=value1&param2=value2]   

export default defineConfig({
    schema: "./schema/*",
    out: "./drizzle",
    dialect: 'postgresql',
    dbCredentials: {
        url: process.env.DB_URL || process.env.DATABASE_URL || "postgresql+psycopg://postgres:postgres@localhost:5432/postgres",
    }
});
