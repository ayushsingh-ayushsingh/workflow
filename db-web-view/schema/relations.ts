import { relations } from "drizzle-orm/relations";
import { langchainPgCollection, langchainPgEmbedding } from "./schema";

export const langchainPgEmbeddingRelations = relations(langchainPgEmbedding, ({one}) => ({
	langchainPgCollection: one(langchainPgCollection, {
		fields: [langchainPgEmbedding.collectionId],
		references: [langchainPgCollection.uuid]
	}),
}));

export const langchainPgCollectionRelations = relations(langchainPgCollection, ({many}) => ({
	langchainPgEmbeddings: many(langchainPgEmbedding),
}));