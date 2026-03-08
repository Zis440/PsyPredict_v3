import Google from "@auth/core/providers/google";
import MicrosoftEntraId from "@auth/core/providers/microsoft-entra-id";
import { convexAuth } from "@convex-dev/auth/server";
import password from "./password";

export const { auth, signIn, signOut, store } = convexAuth({
  providers: [
    password,
    Google({
      authorization: {
        params: {
          prompt: "consent",
          access_type: "offline",
        },
      },
    }),
    MicrosoftEntraId({
      profilePhotoSize: 48,
      authorization: {
        params: {
          scope: "openid profile email User.Read",
        },
      },
    }),
  ],
});
