import { convexAuth } from "@convex-dev/auth/server";
import password from "./password";

export const { auth, signIn, signOut, store } = convexAuth({
  providers: [password],
});
