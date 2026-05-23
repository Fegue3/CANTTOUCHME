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
  return requestJson<{ message: string }>("/auth/register", {
    method: "POST",
    body: payload,
  });
}

export function login(email: string, password: string) {
  return requestJson<LoginResponse>("/auth/login", {
    method: "POST",
    body: { email, password },
  });
}

export function me(token: string) {
  return requestJson<UserPublic>("/auth/me", { token });
}

export function logout(token: string) {
  return requestJson<{ message: string }>("/auth/logout", {
    method: "POST",
    token,
  });
}
