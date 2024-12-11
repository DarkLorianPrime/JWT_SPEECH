import uuid

from pydantic import BaseModel

from schemes.__meta__ import BodyModel


class SignUpRequestSchema(BodyModel):
    username: str
    email: str
    password: str


class SignUpResponseSchema(BaseModel):
    id: uuid.UUID

    class Meta:
        orm_mode = True


class SignInRequestSchema(BodyModel):
    login: str
    password: str


class SignInResponseSchema(BaseModel):
    access_token: str
    refresh_token: str


class RefreshRequestSchema(BodyModel):
    refresh_token: str


class RefreshTokenSchema(BaseModel):
    token_id: uuid.UUID
    user_id: uuid.UUID