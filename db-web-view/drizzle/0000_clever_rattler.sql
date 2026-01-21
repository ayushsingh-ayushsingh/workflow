-- Current sql file was generated after introspecting the database
-- If you want to run this migration please uncomment this code before executing migrations
/*
CREATE TABLE "langchain_pg_collection" (
	"uuid" uuid PRIMARY KEY NOT NULL,
	"name" varchar NOT NULL,
	"cmetadata" json,
	CONSTRAINT "langchain_pg_collection_name_key" UNIQUE("name")
);
--> statement-breakpoint
CREATE TABLE "langchain_pg_embedding" (
	"id" varchar PRIMARY KEY NOT NULL,
	"collection_id" uuid,
	"embedding" vector,
	"document" varchar,
	"cmetadata" jsonb
);
--> statement-breakpoint
ALTER TABLE "langchain_pg_embedding" ADD CONSTRAINT "langchain_pg_embedding_collection_id_fkey" FOREIGN KEY ("collection_id") REFERENCES "public"."langchain_pg_collection"("uuid") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
CREATE INDEX "ix_cmetadata_gin" ON "langchain_pg_embedding" USING gin ("cmetadata" jsonb_path_ops);
*/