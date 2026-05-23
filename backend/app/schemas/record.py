from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


SimpleValidationStatus = Literal["valid", "invalid"]
DecryptStatus = Literal["valid", "decrypt_error", "not_checked"]
OverallStatus = Literal[
    "valid",
    "invalid_hmac",
    "invalid_block_hash",
    "invalid_previous_hash",
    "invalid_rsa_signature",
    "decrypt_error",
    "chain_affected",
]
ChainStateStatus = Literal["valid", "invalid", "missing"]


class RecordCreateRequest(BaseModel):
    text: str = Field(min_length=1, max_length=10000)


class RecordCreateResponse(BaseModel):
    id: str
    block_index: int
    message: str


class RecordValidation(BaseModel):
    hmac: SimpleValidationStatus
    block_hash: SimpleValidationStatus
    previous_hash: SimpleValidationStatus
    rsa_signature: SimpleValidationStatus
    decrypt: DecryptStatus
    overall: OverallStatus


class RecordItem(BaseModel):
    id: str
    block_index: int
    timestamp: str | None
    text: str | None
    created_at: datetime
    validation: RecordValidation


class RecordsListResponse(BaseModel):
    page: int
    page_size: int
    total: int
    records: list[RecordItem]


class ChainStateValidation(BaseModel):
    status: ChainStateStatus
    block_count_match: bool | None = None
    last_hash_match: bool | None = None
    signature: SimpleValidationStatus | None = None


class ChainStatusResponse(BaseModel):
    total_blocks: int
    valid_blocks: int
    invalid_blocks: int
    first_invalid_block_index: int | None
    chain_status: Literal["valid", "invalid"]
    chain_state: ChainStateValidation


class RecordVerifyResponse(BaseModel):
    record_id: str
    block_index: int
    validation: RecordValidation
