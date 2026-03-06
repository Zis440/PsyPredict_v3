import { v } from "convex/values";
import { query, mutation } from "./_generated/server";
import { getAuthUserId } from "@convex-dev/auth/server";

// Get the current authenticated user's profile
export const currentUser = query({
  args: {},
  handler: async (ctx) => {
    const userId = await getAuthUserId(ctx);
    if (!userId) return null;

    // Try to get the profile
    const profile = await ctx.db
      .query("profiles")
      .withIndex("by_userId", (q) => q.eq("userId", userId))
      .first();

    if (profile) return profile;

    // If no profile exists yet, return basic info from auth user
    const authUser = await ctx.db.get(userId);
    return {
      _id: null,
      userId,
      fullName: (authUser as any)?.name ?? null,
      email: (authUser as any)?.email ?? null,
      avatarUrl: (authUser as any)?.image ?? null,
      updatedAt: null,
    };
  },
});

// Update user profile
export const updateProfile = mutation({
  args: {
    fullName: v.optional(v.string()),
    email: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const userId = await getAuthUserId(ctx);
    if (!userId) throw new Error("Not authenticated");

    const existing = await ctx.db
      .query("profiles")
      .withIndex("by_userId", (q) => q.eq("userId", userId))
      .first();

    if (existing) {
      await ctx.db.patch(existing._id, {
        fullName: args.fullName,
        email: args.email,
        updatedAt: new Date().toISOString(),
      });
    } else {
      await ctx.db.insert("profiles", {
        userId,
        fullName: args.fullName,
        email: args.email,
        updatedAt: new Date().toISOString(),
      });
    }
  },
});
