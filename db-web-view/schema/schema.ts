import { pgTable, unique, uuid, varchar, json, index, foreignKey, vector, jsonb } from "drizzle-orm/pg-core"


export const langchainPgCollection = pgTable("langchain_pg_collection", {
	uuid: uuid().primaryKey().notNull(),
	name: varchar().notNull(),
	cmetadata: json(),
}, (table) => [
	unique("langchain_pg_collection_name_key").on(table.name),
]);

export const langchainPgEmbedding = pgTable("langchain_pg_embedding", {
	id: varchar().primaryKey().notNull(),
	collectionId: uuid("collection_id"),
	embedding: vector({ dimensions: 1536 }),
	document: varchar(),
	cmetadata: jsonb(),
}, (table) => [
	index("ix_cmetadata_gin").using("gin", table.cmetadata.asc().nullsLast().op("jsonb_path_ops")),
	foreignKey({
			columns: [table.collectionId],
			foreignColumns: [langchainPgCollection.uuid],
			name: "langchain_pg_embedding_collection_id_fkey"
		}).onDelete("cascade"),
]);
