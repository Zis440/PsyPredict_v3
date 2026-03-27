import { v } from "convex/values";
import { query, mutation } from "./_generated/server";

// Get the current authenticated user's profile
export const currentUser = query({
  args: {},
  handler: async (ctx) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) return null;

    const userId = identity.subject;

    // Try to get the profile
    const profile = await ctx.db
      .query("profiles")
      .withIndex("by_userId", (q) => q.eq("userId", userId))
      .first();

    if (profile) return profile;

    // If no profile exists yet, return basic info from Clerk identity
    return {
      _id: null,
      userId,
      fullName: identity.name ?? null,
      email: identity.email ?? null,
      avatarUrl: identity.pictureUrl ?? null,
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
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) throw new Error("Not authenticated");

    const userId = identity.subject;

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
