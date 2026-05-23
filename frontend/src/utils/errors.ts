import { ApiError } from "../api/http";

const errorMessages: Record<string, string> = {
  "Email already registered": "Este email já está registado.",
  "Invalid credentials": "Email ou palavra-passe inválidos.",
  "Authentication required": "É necessário iniciar sessão.",
  "Invalid or expired token": "A sessão expirou. Inicie sessão novamente.",
  "Session expired": "A sessão expirou. Inicie sessão novamente.",
  "Invalid session": "A sessão já não é válida. Inicie sessão novamente.",
  "Record not found": "Registo não encontrado.",
};

export function friendlyError(error: unknown, fallback: string) {
  if (error instanceof ApiError) {
    return errorMessages[error.message] ?? fallback;
  }

  if (error instanceof Error) {
    return error.message;
  }

  return fallback;
}
