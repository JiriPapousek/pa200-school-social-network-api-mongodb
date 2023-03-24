from sqlalchemy import Column, Integer, Boolean, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from .database import Base


like_table = Table(
    "likes",
    Base.metadata,
    Column("username", ForeignKey("users.username"), primary_key=True),
    Column("post_id", ForeignKey("posts.id"), primary_key=True)
)


class UserClassAssociation(Base):
    __tablename__ = "user_class"

    username = Column(ForeignKey("users.username"), primary_key=True),
    class_id = Column(ForeignKey("classes.id"), primary_key=True)

    user = relationship("User", back_populates="classes")
    in_class = relationship("Class", back_populates="users")


class UserCourseAssociation(Base):
    __tablename__ = "user_course"

    username = Column(ForeignKey("users.username"), primary_key=True),
    class_id = Column(ForeignKey("classes.id"), primary_key=True)

    user = relationship("User", back_populates="courses")
    in_course = relationship("Course", back_populates="users")


class User(Base):
    __tablename__ = "users"
    username = Column(String, primary_key=True, index=True)
    hashed_password = Column(String)
    is_teacher = Column(Boolean)

    likes = relationship(secondary=like_table, back_populates="likes")
    posts = relationship("Post", back_populates="author")
    classes = relationship("UserClassAssociation", back_populates="user")
    courses = relationship("UserCourseAssociation", back_populates="user")


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    author_username = Column(ForeignKey("users.username"))

    author = relationship("User", back_populates="posts")
    likes = relationship(secondary=like_table, back_populates="likes")
    wall = relationship("Wall", back_populates="posts")
    comments = relationship("Comment", back_populates="post")


class Wall(Base):
    __tablename__ = "walls"

    id = Column(Integer, primary_key=True, index=True)
    posts = relationship("Post", back_populates="wall")


class Class(Base):
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    users = relationship("UserClassAssociation", back_populates="in_class")


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    users = relationship("UserCourseAssociation", back_populates="in_course")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    author_username = Column(ForeignKey("users.username"))
    post_id = Column(ForeignKey("posts.id"))

    author = relationship("User", back_populates="posts")
    likes = relationship(secondary=like_table, back_populates="likes")
    post = relationship("Post", back_populates="comments")

