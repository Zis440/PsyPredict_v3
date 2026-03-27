import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({

  // User profiles (extends auth users with app-specific data)
  profiles: defineTable({
    userId: v.string(),
    fullName: v.optional(v.string()),
    email: v.optional(v.string()),
    avatarUrl: v.optional(v.string()),
    updatedAt: v.optional(v.string()),
  }).index("by_userId", ["userId"]),

  // Conversations (chat sessions)
  conversations: defineTable({
    userId: v.string(),
    title: v.optional(v.string()),
    createdAt: v.string(),
  }).index("by_userId", ["userId"]),

  // Messages within conversations
  messages: defineTable({
    userId: v.string(),
    conversationId: v.id("conversations"),
    content: v.string(),
    metadata: v.optional(v.any()),
    createdAt: v.string(),
  }).index("by_conversationId", ["conversationId"]),
});
