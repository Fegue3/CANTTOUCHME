from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.dependencies import AuthContext, require_auth
from app.schemas.record import (
    ChainStateValidation,
    ChainStatusResponse,
    RecordCreateRequest,
    RecordCreateResponse,
    RecordsListResponse,
    RecordVerifyResponse,
)
from app.services import record_service


router = APIRouter(prefix="/records", tags=["records"])


@router.post("", response_model=RecordCreateResponse, status_code=status.HTTP_201_CREATED)
def create_record(
    payload: RecordCreateRequest,
    context: AuthContext = Depends(require_auth),
) -> RecordCreateResponse:
    record = record_service.create_record(context.user, context.session, payload.text)
    return RecordCreateResponse(
        id=record["id"],
        block_index=record["block_index"],
        message="Record created successfully",
    )


@router.get("", response_model=RecordsListResponse)
def list_records(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=50),
    start_date: date | None = None,
    end_date: date | None = None,
    status_filter: str | None = Query(default=None, alias="status", pattern="^(valid|invalid)$"),
    context: AuthContext = Depends(require_auth),
) -> RecordsListResponse:
    records = record_service.validate_records(context.user, context.session)
    filtered = record_service.filter_records(records, start_date, end_date, status_filter)
    total = len(filtered)
    offset = (page - 1) * page_size
    return RecordsListResponse(
        page=page,
        page_size=page_size,
        total=total,
        records=filtered[offset : offset + page_size],
    )


@router.get("/chain/status", response_model=ChainStatusResponse)
def chain_status(context: AuthContext = Depends(require_auth)) -> ChainStatusResponse:
    records = record_service.validate_records(context.user, context.session)
    chain_state: ChainStateValidation = record_service.validate_chain_state(context.user["id"])
    valid_blocks = sum(1 for record in records if record.validation.overall == "valid")
    invalid_blocks = len(records) - valid_blocks
    first_invalid = next(
        (
            record.block_index
            for record in records
            if record.validation.overall != "valid"
        ),
        None,
    )
    overall_valid = invalid_blocks == 0 and chain_state.status == "valid"
    return ChainStatusResponse(
        total_blocks=len(records),
        valid_blocks=valid_blocks,
        invalid_blocks=invalid_blocks,
        first_invalid_block_index=first_invalid,
        chain_status="valid" if overall_valid else "invalid",
        chain_state=chain_state,
    )


@router.get("/{record_id}/verify", response_model=RecordVerifyResponse)
def verify_record(
    record_id: UUID,
    context: AuthContext = Depends(require_auth),
) -> RecordVerifyResponse:
    if record_service.find_record_for_user(record_id, context.user["id"]) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")

    records = record_service.validate_records(context.user, context.session)
    record = next((item for item in records if item.id == str(record_id)), None)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")

    return RecordVerifyResponse(
        record_id=record.id,
        block_index=record.block_index,
        validation=record.validation,
    )
