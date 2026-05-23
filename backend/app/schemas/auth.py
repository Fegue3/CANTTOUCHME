from typing import Literal

from pydantic import BaseModel, EmailStr, Field, model_validator


EncryptionAlgorithm = Literal["AES-128-CBC", "AES-128-CTR"]
HmacAlgorithm = Literal["HMAC-SHA256", "HMAC-SHA512"]


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=256)
    confirm_password: str = Field(min_length=8, max_length=256)
    encryption_algorithm: EncryptionAlgorithm
    hmac_algorithm: HmacAlgorithm

    @model_validator(mode="after")
    def passwords_match(self) -> "RegisterRequest":
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


class MessageResponse(BaseModel):
    message: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=256)


class UserPublic(BaseModel):
    email: EmailStr
    encryption_algorithm: EncryptionAlgorithm
    hmac_algorithm: HmacAlgorithm


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: UserPublic
