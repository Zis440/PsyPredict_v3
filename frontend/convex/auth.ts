import Google from "@auth/core/providers/google";
import MicrosoftEntraId from "@auth/core/providers/microsoft-entra-id";
import { convexAuth } from "@convex-dev/auth/server";

export const { auth, signIn, signOut, store } = convexAuth({
  providers: [Google, MicrosoftEntraId],
});
