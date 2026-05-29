// Authentication API calls used by the login and registration pages.

import { requestJson } from "./http";
import type { EncryptionAlgorithm, HmacAlgorithm, LoginResponse, UserPublic } from "../types";

export type RegisterPayload = {
  email: string;
  password: string;
  confirm_password: string;
  encryption_algorithm: EncryptionAlgorithm;
  hmac_algorithm: HmacAlgorithm;
};

export function register(payload: RegisterPayload) {
  // Register a new user account.
  return requestJson<{ message: string }>("/auth/register", {
    method: "POST",
    body: payload,
  });
}

export function login(email: string, password: string) {
  // Request a bearer token for an existing account.
  return requestJson<LoginResponse>("/auth/login", {
    method: "POST",
    body: { email, password },
  });
}

export function me(token: string) {
  // Fetch the current authenticated user's public profile.
  return requestJson<UserPublic>("/auth/me", { token });
}

export function logout(token: string) {
  // Invalidate the current server-side session.
  return requestJson<{ message: string }>("/auth/logout", {
    method: "POST",
    token,
  });
}
