import { ConvexError } from "convex/values";
import { Password } from "@convex-dev/auth/providers/Password";

export default Password({
  profile(params) {
    const email = params.email as string;
    const name = params.name as string | undefined;

    // Basic email format check
    if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      throw new ConvexError("Please enter a valid email address.");
    }

    return { email, name: name || email.split("@")[0] };
  },

  validatePasswordRequirements(password: string) {
    if (password.length < 8) {
      throw new ConvexError("Password must be at least 8 characters.");
    }
    if (!/[a-z]/.test(password)) {
      throw new ConvexError("Password must contain a lowercase letter.");
    }
    if (!/[A-Z]/.test(password)) {
      throw new ConvexError("Password must contain an uppercase letter.");
    }
    if (!/\d/.test(password)) {
      throw new ConvexError("Password must contain a number.");
    }
  },
});
