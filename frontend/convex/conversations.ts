import { v } from "convex/values";
import { query, mutation } from "./_generated/server";
import { getAuthUserId } from "@convex-dev/auth/server";

// List all conversations for the current user
export const list = query({
  args: {},
  handler: async (ctx) => {
    const userId = await getAuthUserId(ctx);
    if (!userId) return [];

    return await ctx.db
      .query("conversations")
      .withIndex("by_userId", (q) => q.eq("userId", userId))
      .collect();
  },
});

// Get a single conversation (with ownership check)
export const get = query({
  args: { id: v.id("conversations") },
  handler: async (ctx, args) => {
    const userId = await getAuthUserId(ctx);
    if (!userId) return null;

    const conversation = await ctx.db.get(args.id);
    if (!conversation || conversation.userId !== userId) return null;

    return conversation;
  },
});

// Create a new conversation
export const create = mutation({
  args: { title: v.optional(v.string()) },
  handler: async (ctx, args) => {
    const userId = await getAuthUserId(ctx);
    if (!userId) throw new Error("Not authenticated");

    return await ctx.db.insert("conversations", {
      userId,
      title: args.title ?? `Chat on ${new Date().toLocaleDateString()}`,
      createdAt: new Date().toISOString(),
    });
  },
});

// Delete a conversation and all its messages
export const remove = mutation({
  args: { id: v.id("conversations") },
  handler: async (ctx, args) => {
    const userId = await getAuthUserId(ctx);
    if (!userId) throw new Error("Not authenticated");

    const conversation = await ctx.db.get(args.id);
    if (!conversation || conversation.userId !== userId) {
      throw new Error("Conversation not found or access denied");
    }

    // Delete all messages in this conversation
    const messages = await ctx.db
      .query("messages")
      .withIndex("by_conversationId", (q) => q.eq("conversationId", args.id))
      .collect();

    for (const message of messages) {
      await ctx.db.delete(message._id);
    }

    // Delete the conversation itself
    await ctx.db.delete(args.id);
  },
});
