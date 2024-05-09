from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, conint


# USER SCHEMAS
class UserSchema(BaseModel):
    first_name: str
    last_name: str
    id_number: int
    email: EmailStr


class UserCreate(UserSchema):
    password: str


class UserResponse(UserSchema):
    pass

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Post(BaseModel):
    title: str
    content: str
    published: bool = False
    # rating: Optional[int] = None


class CreatePost(Post):
    pass


class UpdatePost(BaseModel):
    published: bool
    # rating: Optional[int] = None


class PostResponse(Post):
    id: int
    created_at: datetime
    owner_id: int
    owner: UserResponse

    # rating: Optional[int] = None

    class Config:
        orm_mode = True


# This schema should not extend Post class but only BaseModel.
# It totally has no relationship with the Posts class it only has two attributes of TYPE: Post and votes.
# capitalize Post and no caps in votes
class PostOut(BaseModel):
    Post: PostResponse
    votes: int

    class Config:
        orm_mode = True


# TOKEN SCHEMAS
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None


# VOTES SCHEMAS
class Vote(BaseModel):
    post_id: int
    dir: conint(le=1)


class VoteRequest(Vote):
    class Config:
        orm_mode = True


class VoteResponse(Vote):
    ...
