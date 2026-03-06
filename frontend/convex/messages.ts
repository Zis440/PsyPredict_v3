import { v } from "convex/values";
import { query, mutation } from "./_generated/server";
import { getAuthUserId } from "@convex-dev/auth/server";

// List all messages for a conversation (ordered by creation time)
export const listByConversation = query({
  args: { conversationId: v.id("conversations") },
  handler: async (ctx, args) => {
    const userId = await getAuthUserId(ctx);
    if (!userId) return [];

    // Verify conversation ownership
    const conversation = await ctx.db.get(args.conversationId);
    if (!conversation || conversation.userId !== userId) return [];

    return await ctx.db
      .query("messages")
      .withIndex("by_conversationId", (q) =>
        q.eq("conversationId", args.conversationId)
      )
      .collect();
  },
});

// Insert a new message
export const create = mutation({
  args: {
    conversationId: v.id("conversations"),
    content: v.string(),
    metadata: v.optional(v.any()),
  },
  handler: async (ctx, args) => {
    const userId = await getAuthUserId(ctx);
    if (!userId) throw new Error("Not authenticated");

    return await ctx.db.insert("messages", {
      userId,
      conversationId: args.conversationId,
      content: args.content,
      metadata: args.metadata,
      createdAt: new Date().toISOString(),
    });
  },
});
