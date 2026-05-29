// Shared TypeScript types that mirror the API payloads and responses.

export type EncryptionAlgorithm = "AES-128-CBC" | "AES-128-CTR";
export type HmacAlgorithm = "HMAC-SHA256" | "HMAC-SHA512";

export type UserPublic = {
  email: string;
  encryption_algorithm: EncryptionAlgorithm;
  hmac_algorithm: HmacAlgorithm;
};

export type LoginResponse = {
  access_token: string;
  token_type: "bearer";
  expires_in: number;
  user: UserPublic;
};

export type RecordValidation = {
  hmac: "valid" | "invalid";
  block_hash: "valid" | "invalid";
  previous_hash: "valid" | "invalid";
  rsa_signature: "valid" | "invalid";
  decrypt: "valid" | "decrypt_error" | "not_checked";
  overall:
    | "valid"
    | "invalid_hmac"
    | "invalid_block_hash"
    | "invalid_previous_hash"
    | "invalid_rsa_signature"
    | "decrypt_error"
    | "chain_affected";
};

export type RecordItem = {
  id: string;
  block_index: number;
  timestamp: string | null;
  text: string | null;
  created_at: string;
  validation: RecordValidation;
};

export type RecordsListResponse = {
  page: number;
  page_size: number;
  total: number;
  records: RecordItem[];
};

export type ChainStatusResponse = {
  total_blocks: number;
  valid_blocks: number;
  invalid_blocks: number;
  first_invalid_block_index: number | null;
  chain_status: "valid" | "invalid";
};
