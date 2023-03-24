from pydantic import BaseModel


class User(BaseModel):
    username: str
    hashed_password: str


class Student

class Post(BaseModel):
    author: User
    text: str


class Wall(BaseModel):
    posts: list[Post]
