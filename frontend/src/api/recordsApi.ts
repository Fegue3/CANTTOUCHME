// Record API calls for creating, listing and checking chain integrity.

import { requestJson } from "./http";
import type { ChainStatusResponse, RecordsListResponse } from "../types";

export type ListRecordsParams = {
  page: number;
  page_size: number;
  start_date?: string;
  end_date?: string;
  status?: "valid" | "invalid";
};

export function createRecord(token: string, text: string) {
  // Create a new encrypted record for the active user.
  return requestJson<{ id: string; block_index: number; message: string }>("/records", {
    method: "POST",
    token,
    body: { text },
  });
}

export function listRecords(token: string, params: ListRecordsParams) {
  // Fetch a paginated record list with optional filters.
  const search = new URLSearchParams();
  search.set("page", String(params.page));
  search.set("page_size", String(params.page_size));
  if (params.start_date) search.set("start_date", params.start_date);
  if (params.end_date) search.set("end_date", params.end_date);
  if (params.status) search.set("status", params.status);

  return requestJson<RecordsListResponse>(`/records?${search.toString()}`, { token });
}

export function chainStatus(token: string) {
  // Fetch the aggregated status of the user's record chain.
  return requestJson<ChainStatusResponse>("/records/chain/status", { token });
}

export function verifyRecord(token: string, recordId: string) {
  // Validate a single record by id.
  return requestJson(`/records/${recordId}/verify`, { token });
}
