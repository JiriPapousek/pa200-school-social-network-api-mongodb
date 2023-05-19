from bson import ObjectId
from typing import Union
from pydantic import BaseModel, Field


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None



class User(BaseModel):

    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    hashed_password: str = Field(...)
    username: str = Field(...)
    is_teacher: bool = Field(...)
    course_ids: list[str] = Field(default_factory=list)
    class_ids: list[str] = Field(default_factory=list)
    likes_post_ids: list[str] = Field(default_factory=list)
    likes_comment_ids: list[str] = Field(default_factory=list)

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class UserPermissions(BaseModel):

    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    username: str = Field(...)
    is_teacher: bool = Field(...)
    course_ids: list[str] = Field(default_factory=list)
    class_ids: list[str] = Field(default_factory=list)

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class UserCreate(BaseModel):
    username: str = Field(...)
    password: str = Field(...)
    is_teacher: bool = Field(...)
    course_ids: list[str] = Field(default_factory=list)
    class_ids: list[str] = Field(default_factory=list)

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class Class(BaseModel):

    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(...)
    user_ids: list[str] = Field(default_factory=list)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class ClassCreate(BaseModel):

    name: str = Field(...)
    user_ids: list[str] = Field(default_factory=list)


    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class Course(BaseModel):

    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(...)
    user_ids: list[str] = Field(default_factory=list)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class CourseCreate(BaseModel):
    name: str = Field(...)
    user_ids: list[str] = Field(default_factory=list)

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class Post(BaseModel):

    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    text: str = Field(...)
    author_id: str = Field(...)
    course_id: str = Field(default=None)
    class_id: str = Field(default=None)
    likes_user_ids: list[str] = Field(default_factory=list)
    comment_ids: list[str] = Field(default_factory=list)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class Comment(BaseModel):

    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    text: str = Field(...)
    author_id: str = Field(...)
    post_id: str = Field(...)
    likes_user_ids: list[str] = Field(default_factory=list)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


