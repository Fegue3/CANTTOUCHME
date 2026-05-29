# Pydantic models for authentication request and response payloads.

from typing import Literal

from pydantic import BaseModel, EmailStr, Field, model_validator


EncryptionAlgorithm = Literal["AES-128-CBC", "AES-128-CTR"]
HmacAlgorithm = Literal["HMAC-SHA256", "HMAC-SHA512"]


class RegisterRequest(BaseModel):
    # Payload for user registration, including algorithm choices.

    email: EmailStr
    password: str = Field(min_length=8, max_length=256)
    confirm_password: str = Field(min_length=8, max_length=256)
    encryption_algorithm: EncryptionAlgorithm
    hmac_algorithm: HmacAlgorithm

    @model_validator(mode="after")
    def passwords_match(self) -> "RegisterRequest":
        # Reject registration payloads where the confirmation does not match.
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


class MessageResponse(BaseModel):
    # Simple success or status message wrapper.

    message: str


class LoginRequest(BaseModel):
    # Credentials sent by the login form.

    email: EmailStr
    password: str = Field(min_length=1, max_length=256)


class UserPublic(BaseModel):
    # Public user fields that can safely be exposed to the client.

    email: EmailStr
    encryption_algorithm: EncryptionAlgorithm
    hmac_algorithm: HmacAlgorithm


class LoginResponse(BaseModel):
    # Successful login payload with token metadata and user info.

    access_token: str
    token_type: str
    expires_in: int
    user: UserPublic
