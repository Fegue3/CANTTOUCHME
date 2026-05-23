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
  return requestJson<{ id: string; block_index: number; message: string }>("/records", {
    method: "POST",
    token,
    body: { text },
  });
}

export function listRecords(token: string, params: ListRecordsParams) {
  const search = new URLSearchParams();
  search.set("page", String(params.page));
  search.set("page_size", String(params.page_size));
  if (params.start_date) search.set("start_date", params.start_date);
  if (params.end_date) search.set("end_date", params.end_date);
  if (params.status) search.set("status", params.status);

  return requestJson<RecordsListResponse>(`/records?${search.toString()}`, { token });
}

export function chainStatus(token: string) {
  return requestJson<ChainStatusResponse>("/records/chain/status", { token });
}

export function verifyRecord(token: string, recordId: string) {
  return requestJson(`/records/${recordId}/verify`, { token });
}
